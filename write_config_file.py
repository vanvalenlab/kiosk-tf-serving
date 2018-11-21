# Copyright 2016-2018 The Van Valen Lab at the California Institute of
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
"""Generates a configuration file for TensorFlow Serving
to load all servables and versions from a cloud storage bucket.

Currently supporting Amazon Web Services and Google Cloud.
"""

import os
import sys
import argparse
import logging

import boto3
from google.cloud import storage as google_storage
from decouple import config


class TFServingConfigWriter(object):
    """Abstract Class for ConfigWriter
    Reads all servable models from a cloud bucket
    and writes them in a config file for TensorFlow Serving
    """

    def __init__(self, bucket, model_prefix, protocol=None):
        self._storage_protocol = protocol
        self.bucket = bucket
        self.model_prefix = model_prefix
        self.logger = logging.getLogger(str(self.__class__.__name__))

        # Normalize model prefix
        if not self.model_prefix.endswith('/'):
            self.model_prefix = self.model_prefix + '/'

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
                dirnames = o.replace(self.model_prefix, '').split('/')

                if len(dirnames) > 1 and dirnames[0] not in models:
                    models.add(dirnames[0])
                    yield dirnames[0]
        self.logger.debug('Found Models: %s', ', '.join(models))

    def write(self, path):
        """Create config file and write config block for each model
        # Arguments:
            models: list of models to register with tf-serving
        """
        self.logger.debug('Writing model config file to %s', path)
        with open(path, 'w+') as config_file:

            config_file.write('model_config_list: {\n')

            for i, model in enumerate(self._get_models_from_bucket()):
                url = self.get_model_url(model)

                config_file.write('    config: {\n')
                config_file.write('        name: "{}"\n'.format(model))
                config_file.write('        base_path: "{}"\n'.format(url))
                config_file.write('        model_platform: "tensorflow"\n')
                config_file.write('        model_version_policy: {\n')
                config_file.write('            all: {}\n')
                config_file.write('        }\n')
                config_file.write('    }\n')
            else:
                self.logger.info('Found %s models', i + 1)

            config_file.write('}\n')

        self.logger.info('Successfully wrote %s', path)

    def _get_models_from_bucket(self):
        """Query the cloud storage bucket for tensorflow servables
        # Returns:
            models: list of all servable models in the bucket and model_prefix
        """
        raise NotImplementedError


class S3ConfigWriter(TFServingConfigWriter):

    def __init__(self,
                 bucket,
                 model_prefix,
                 aws_access_key_id,
                 aws_secret_access_key):
        self.client = boto3.client('s3',
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


class GCSConfigWriter(TFServingConfigWriter):

    def __init__(self, bucket, model_prefix):
        self.client = google_storage.Client()
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


def initialize_logger(log_level='DEBUG'):
    log_level = str(log_level).upper()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s]:[%(name)s]: %(message)s')
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)

    if log_level == 'CRITICAL':
        console.setLevel(logging.CRITICAL)
    elif log_level == 'ERROR':
        console.setLevel(logging.ERROR)
    elif log_level == 'WARN':
        console.setLevel(logging.WARN)
    elif log_level == 'INFO':
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.DEBUG)

    logger.addHandler(console)


def get_arg_parser():
    """argument parser to consume command line arguments"""
    root_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--cloud-provider',
                        choices=['aws', 'gke'],
                        required=True,
                        help='Cloud Provider')

    parser.add_argument('-p', '--model-prefix',
                        default='/',
                        help='Base directory of models')

    parser.add_argument('-f', '--file-path',
                        default=os.path.join(root_dir, 'models.conf'),
                        help='Full filepath of configuration file')

    return parser


if __name__ == '__main__':
    initialize_logger(config('LOG_LEVEL', default='DEBUG'))

    # Get command line arguments
    args = get_arg_parser().parse_args()

    # Create the ConfigWriter based on the cloud provider
    if args.cloud_provider.lower() == 'aws':
        writer = S3ConfigWriter(
            bucket=config('AWS_S3_BUCKET'),
            model_prefix=args.model_prefix,
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))

    elif args.cloud_provider.lower() == 'gke':
        writer = GCSConfigWriter(
            bucket=config('GCLOUD_STORAGE_BUCKET'),
            model_prefix=args.model_prefix)
    
    else:
        raise ValueError('Expected `cloud_provider` to be one of'
                         ' {"aws", "gke"}.  Got {}'.format(
                             args.cloud_provider))

    # Write the config file
    writer.write(args.file_path)
