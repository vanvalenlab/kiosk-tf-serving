#!/bin/sh

python /opt/generate_config.py \
   --model_prefix=$MODEL_PREFIX \
   --aws_s3_bucket=$AWS_S3_BUCKET \
   --aws_access_key_id=$AWS_ACCESS_KEY_ID \
   --aws_secret_access_key=$AWS_SECRET_ACCESS_KEY

tensorflow_model_server \
    --port=$RPC_PORT \
    --rest_api_port=$REST_PORT \
    --rest_api_timeout_in_ms=$REST_TIMEOUT \
    --model_config_file=/opt/models.conf
#    --file_system_poll_wait_seconds=30
#    > log_file.txt

# hack to keep from exiting
while true; do sleep 1000; done
