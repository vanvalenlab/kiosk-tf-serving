#!/bin/bash

# write the configuration files, then run the server
python write_config_file.py \
    --cloud-provider=$CLOUD_PROVIDER \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$MODEL_CONFIG_FILE \
    --monitoring-enabled=$PROMETHEUS_MONITORING_ENABLED \
    --monitoring-path=$PROMETHEUS_MONITORING_PATH \
    --monitoring-file-path=$MONITORING_CONFIG_FILE \
    --enable-batching=$MONITORING_CONFIG_FILE \
    --max-batch-size=$MAX_BATCH_SIZE \
    --batch-timeout=$BATCH_TIMEOUT_MICROS \
    --max-enqueued-batches=$MAX_ENQUEUED_BATCHES \
    --batch-file-path=$BATCHING_CONFIG_FILE \
  && \
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
