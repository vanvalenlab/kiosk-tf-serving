#!/bin/sh

# write the configuration file
python write_config_file.py \
    --cloud-provider=$CLOUD_PROVIDER \
    --bucket=$BUCKET \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$TF_SERVING_CONFIG_FILE \
  && \
tensorflow_model_server \
    --port=$RPC_PORT \
    --rest_api_port=$REST_PORT \
    --rest_api_timeout_in_ms=$REST_TIMEOUT \
    --model_config_file=$TF_SERVING_CONFIG_FILE \
  && \
/bin/bash # hack to keep from exiting
# while true; do sleep 1000; done
