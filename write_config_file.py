# Copyright 2016-2022 The Van Valen Lab at the California Institute of
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

import writers


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

    # Model Config args
    parser.add_argument('-c', '--cloud-provider',
                        choices=['aws', 'gke'],
                        required=False,
                        help='DEPRECATED: Cloud Provider')

    parser.add_argument('-p', '--model-prefix',
                        default='/',
                        help='Base directory of models')

    parser.add_argument('-f', '--file-path',
                        default=os.path.join(root_dir, 'models.conf'),
                        help='Full filepath of configuration file')

    parser.add_argument('-b', '--storage-bucket', required=True,
                        help='Cloud Storage Bucket '
                             '(e.g. gs://deepcell-models)')

    # Batch Config Args
    parser.add_argument('--enable-batching', type=bool, default=True,
                        help='Boolean switch for batching configuration.')

    parser.add_argument('--max-batch-size', type=int, default=1,
                        help='Maximum batch size for tf-serving.')

    parser.add_argument('--batch-timeout', type=int, default=0,
                        help='Batch timeout in microseconds.')

    parser.add_argument('--max-enqueued-batches', type=int, default=128,
                        help='Maximum number of work items to store.')

    parser.add_argument('--batch-file-path',
                        default=os.path.join(root_dir, 'batch.conf'),
                        help='Full filepath of batch configuration file')

    # Monitoring Config Args
    parser.add_argument('--monitoring-enabled', type=bool, default=True,
                        help='Whether to enable prometheus monitoring.')

    parser.add_argument('--monitoring-path',
                        default='/monitoring/prometheus/metrics',
                        help='API endpoint for prometheus scraping.')

    parser.add_argument('--monitoring-file-path',
                        default=os.path.join(root_dir, 'monitoring.conf'),
                        help='Full filepath of monitoring configuration file')

    return parser


def write_model_config_file(args):
    # Create the ConfigWriter based on the cloud provider
    writer_cls = writers.get_model_config_writer(args.storage_bucket)

    writerkwargs = {
        'bucket': str(args.storage_bucket).split('://')[-1],
        'model_prefix': args.model_prefix,
    }

    # additional AWS required credentials
    if isinstance(writer_cls, writers.S3ConfigWriter):
        writerkwargs['aws_access_key_id'] = config('AWS_ACCESS_KEY_ID')
        writerkwargs['aws_secret_access_key'] = config('AWS_SECRET_ACCESS_KEY')

    writer = writer_cls(**writerkwargs)

    # Write the config file
    writer.write(args.file_path)


def write_monitoring_config_file(args):
    writer = writers.MonitoringConfigWriter(
        monitoring_enabled=args.monitoring_enabled,
        monitoring_path=args.monitoring_path)

    writer.write(args.monitoring_file_path)


def write_batching_config_file(args):
    writer = writers.BatchConfigWriter(
        max_batch_size=args.max_batch_size,
        batch_timeout=args.batch_timeout,
        max_enqueued_batches=args.max_enqueued_batches)

    writer.write(args.batch_file_path)


if __name__ == '__main__':
    initialize_logger(config('LOG_LEVEL', default='DEBUG'))

    # Get command line arguments
    ARGS = get_arg_parser().parse_args()

    write_model_config_file(ARGS)

    write_monitoring_config_file(ARGS)

    write_batching_config_file(ARGS)
