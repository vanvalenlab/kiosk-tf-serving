# Copyright 2016-2019 The Van Valen Lab at the California Institute of
# Technology (Caltech), with support from the Paul Allen Family Foundation,
# Google, & National Institutes of Health (NIH) under Grant U24CA224309-01.
# All rights reserved.
#
# Licensed under a modified Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.github.com/vanvalenlab/kiosk-tf-serving/LICENSE
#
# The Work provided may be used for non-commercial academic purposes only.
# For any other use of the Work, including commercial use, please contact:
# vanvalenlab@gmail.com
#
# Neither the name of Caltech nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Classes to read a cloud bucket and write a tf-serving config file"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging


class ConfigWriter(object):
    """Base class for all Writers, must have a write() function."""

    def __init__(self):
        self.logger = logging.getLogger(str(self.__class__.__name__))

    def write(self, path):
        """Create batch config file and save to `path`.

        Args:
            path: str, the filepath of the config file to write.
        """
        raise NotImplementedError


class MonitoringConfigWriter(ConfigWriter):

    def write(self, path):
        """Create batch config file and save to `path`.

        Args:
            path: str, the filepath of the config file to write.
        """
        self.logger.debug('Writing monitoring config file to %s', path)
        with open(path, 'w+') as config_file:

            config_file.write('prometheus_config: {\n')
            config_file.write('  enable: true,\n')
            config_file.write('  path: "{}")\n'.format(path))
            config_file.write('}\n')


class ModelConfigWriter(ConfigWriter):
    """Abstract Class for ModelConfigWriter
    Reads all servable models from a cloud bucket
    and writes them in a config file for TensorFlow Serving.
    """

    def __init__(self, bucket, model_prefix, protocol=None):
        self._storage_protocol = protocol
        self.bucket = bucket
        self.model_prefix = model_prefix

        # Normalize model prefix
        if not self.model_prefix.endswith('/'):
            self.model_prefix = self.model_prefix + '/'

        super(ModelConfigWriter, self).__init__()

    def get_model_url(self, model):
        """Get the URL of the model in the given cloud bucket
        # Arguments:
            bucket: name of cloud storage bucket
            model: full key of the model folder for tf serving
        # Returns:
            formatted URL to be inserted into config file
        """
        return '{protocol}://{bucket}/{prefix}{model}'.format(
            protocol=self._storage_protocol,
            bucket=self.bucket,
            prefix=self.model_prefix,
            model=model)

    def _filter_models(self, objects):
        """Get unique list of model names
        # Arguments:
            objects: list of all objects in the storage bucket
        # Returns:
            models: list of folders containing versions of tf servables
        """
        models = set([])
        for o in objects:
            if o.startswith(self.model_prefix):
                o = o[:-1] if o.endswith('/') else o
                dirnames = o.replace(self.model_prefix, '').split('/')

                # only if there are subdirectories and a new model
                if len(dirnames) > 1 and dirnames[0] not in models:
                    # valid models contain a protobuf (.pb)
                    if any(d.lower().endswith('.pb') for d in dirnames):
                        models.add(dirnames[0])
                        yield dirnames[0]
        self.logger.debug('Found Models: %s', ', '.join(models))

    def write(self, path):
        """Create batch config file and save to `path`.

        Args:
            path: str, the filepath of the config file to write.
        """
        self.logger.debug('Writing model config file to %s', path)
        with open(path, 'w+') as config_file:

            config_file.write('model_config_list: {\n')

            i = 0
            for model in self._get_models_from_bucket():
                url = self.get_model_url(model)
                config_file.write('    config: {\n')
                config_file.write('        name: "{}"\n'.format(model))
                config_file.write('        base_path: "{}"\n'.format(url))
                config_file.write('        model_platform: "tensorflow"\n')
                config_file.write('        model_version_policy: {\n')
                config_file.write('            all: {}\n')
                config_file.write('        }\n')
                config_file.write('    }\n')
                i += 1

            if not i:
                raise Exception('No models found.')
            self.logger.info('Found %s models', i + 1)

            config_file.write('}\n')

        self.logger.info('Successfully wrote %s', path)

    def _get_models_from_bucket(self):
        """Query the cloud storage bucket for tensorflow servables
        # Returns:
            models: list of all servable models in the bucket and model_prefix
        """
        raise NotImplementedError


class S3ConfigWriter(ModelConfigWriter):

    def __init__(self,
                 bucket,
                 model_prefix,
                 aws_access_key_id,
                 aws_secret_access_key):
        import boto3
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        super(S3ConfigWriter, self).__init__(bucket, model_prefix, 's3')

    def _get_models_from_bucket(self):
        """Query the cloud storage bucket for tensorflow servables
        # Returns:
            models: list of paths to folder containg servable model versions
        """
        directories_verbose = self.client.list_objects_v2(
            Bucket=self.bucket, StartAfter=self.model_prefix)

        directories = (d['Key'] for d in directories_verbose['Contents'])
        for model in self._filter_models(directories):
            yield model


class GCSConfigWriter(ModelConfigWriter):

    def __init__(self, bucket, model_prefix):
        from google.cloud import storage
        self.client = storage.Client()
        super(GCSConfigWriter, self).__init__(bucket, model_prefix, 'gs')

    def _get_models_from_bucket(self):
        """Query the cloud storage bucket for tensorflow servables
        # Returns:
            models: list of all servable models in the bucket and model_prefix
        """
        bucket = self.client.get_bucket(self.bucket)
        blobs = (b.name for b in bucket.list_blobs(prefix=self.model_prefix))
        for model in self._filter_models(blobs):
            yield model
