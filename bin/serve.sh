#!/bin/bash

tensorflow_model_server \
    --port=$PORT \
    --rest_api_port=$REST_API_PORT \
    --rest_api_timeout_in_ms=$REST_API_TIMEOUT \
    --model_config_file=$MODEL_CONFIG_FILE \
    --enable_batching=$ENABLE_BATCHING \
    --grpc_channel_arguments=$GRPC_CHANNEL_ARGS \
    --tensorflow_session_parallelism=$TF_SESSION_PARALLELISM \
    --monitoring_config_file=$MONITORING_CONFIG_FILE \
    --batching_parameters_file=$BATCHING_CONFIG_FILE \
  && \
/bin/bash # hack to keep from exiting
