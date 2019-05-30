#!/bin/bash

# write the configuration files, then run the server
python write_config_file.py \
    --cloud-provider=$CLOUD_PROVIDER \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$MODEL_CONFIG_FILE \
  && \
echo "prometheus_config: {" > $BATCHING_CONFIG_FILE
echo "  enable: ${PROMETHEUS_MONITORING_ENABLED}," >> $BATCHING_CONFIG_FILE
echo "  path: ${PROMETHEUS_MONITORING_PATH}" >> $BATCHING_CONFIG_FILE
echo "}" >> $MONITORING_CONFIG_FILE \
  && \
echo "max_batch_size { value: ${MAX_BATCH_SIZE} }" > $MONITORING_CONFIG_FILE
echo "batch_timeout_micros { value: ${BATCH_TIMEOUT_MICROS} }" >> $MONITORING_CONFIG_FILE
echo "max_enqueued_batches { value: ${MAX_ENQUEUED_BATCHES} }" >> $MONITORING_CONFIG_FILE
echo "num_batch_threads { value: $(nproc) }" >> $MONITORING_CONFIG_FILE \
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
