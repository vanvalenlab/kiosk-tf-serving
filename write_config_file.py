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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import argparse
import logging

from decouple import config

from writers import S3ConfigWriter
from writers import GCSConfigWriter


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
                         ' ["aws", "gke"].  Got {}'.format(
                             args.cloud_provider))

    # Write the config file
    writer.write(args.file_path)
