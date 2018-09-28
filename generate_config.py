"""
generate_config.py
@author: andrewqho, willgraf

Script to generate Tensorflow Serving configuration file at Docker Build Time

The generate_config script pulls all subdirectories from a given bucket
and model home directory and generates the required configuration file
for Tensorflow Serving
"""

import os
import argparse

import boto3


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# Generate model.conf
def gen_config(aws_s3_bucket, aws_access_key_id, aws_secret_access_key, model_prefix): 
    # Create boto client object
    s3client = boto3.client('s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    
    # Get every object in specified bucket
    directories_verbose = s3client.list_objects_v2(
        Bucket=aws_s3_bucket, StartAfter=model_prefix)
    
    # Get unique list of model names
    models_list = set([])
    
    for directory in directories_verbose['Contents']:
        if directory['Key'].startswith(model_prefix):
            dirnames = directory['Key'].replace(model_prefix, '').split('/')
            if len(dirnames) > 1:
                models_list.add(dirnames[0])
    
    # Create config file and write config block for each model
    conf_file_path = os.path.join(ROOT_DIR, 'models.conf')
    with open(conf_file_path, 'w+') as config_file:
    
        config_file.write('model_config_list: {\n')
    
        for model in models_list:
            config_file.write('    config: {\n')
            config_file.write('        name: "{}"\n'.format(model))
            config_file.write('        base_path: "s3://{}/{}{}"\n'.format(aws_s3_bucket, model_prefix, model))
            config_file.write('        model_platform: "tensorflow"\n')
            config_file.write('        model_version_policy: {\n')
            config_file.write('            all: {}\n')
            config_file.write('        }\n')
            config_file.write('    }\n')
        config_file.write('}\n')

def get_arg_parser():
    """argument parser to consume command line arguments"""
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_prefix',
                        help='Base directory of models')

    parser.add_argument('--aws_s3_bucket',
                        help='specify target S3 Bucket')

    parser.add_argument('--aws_access_key_id', 
                        help='Access Key ID for S3 credentials')

    parser.add_argument('--aws_secret_access_key',
                        help='Secret Access Key for s3 credentials')

    return parser

if __name__ == '__main__':
    # Get command line arguments
    ARGS = get_arg_parser().parse_args()    

    AWS_S3_BUCKET = str(ARGS.aws_s3_bucket)
    AWS_ACCESS_KEY_ID = str(ARGS.aws_access_key_id)
    AWS_SECRET_ACCESS_KEY = str(ARGS.aws_secret_access_key)
    MODEL_PREFIX = str(ARGS.model_prefix)

    if not MODEL_PREFIX.endswith('/'):
        MODEL_PREFIX = MODEL_PREFIX + '/'
    
    # Generate configuration file
    gen_config(AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MODEL_PREFIX)
