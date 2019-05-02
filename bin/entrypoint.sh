#!/bin/bash

# write the configuration file
python write_config_file.py \
    --cloud-provider=$CLOUD_PROVIDER \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$MODEL_CONFIG_FILE \
  && \
tensorflow_model_server \
    --port=$PORT \
    --rest_api_port=$REST_API_PORT \
    --rest_api_timeout_in_ms=$REST_API_TIMEOUT \
    --model_config_file=$MODEL_CONFIG_FILE \
    --enable_batching=$ENABLE_BATCHING \
    --grpc_channel_arguments=$GRPC_CHANNEL_ARGS \
    --monitoring_config_file=./monitoring_config.txt \
  && \
/bin/bash # hack to keep from exiting
