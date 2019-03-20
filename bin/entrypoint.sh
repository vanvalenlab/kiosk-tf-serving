#!/bin/bash

if [ "$DEBUG" == "TRUE" ]
then
while true; do sleep 10000; done
else

# write the configuration file
python write_config_file.py \
    --cloud-provider=$CLOUD_PROVIDER \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$MODEL_CONFIG_FILE \
  && \
tensorflow_model_server \
    --port=$RPC_PORT \
    --rest_api_port=$REST_PORT \
    --rest_api_timeout_in_ms=$REST_TIMEOUT \
    --model_config_file=$MODEL_CONFIG_FILE \
    --enable_batching=$ENABLE_BATCHING \
    --grpc_channel_arguments=$GRPC_CHANNEL_ARGS \
  && \
/bin/bash # hack to keep from exiting

fi
