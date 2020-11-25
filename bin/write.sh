#!/bin/bash

# write the configuration files before running the server
python write_config_file.py \
    --storage-bucket=$STORAGE_BUCKET \
    --model-prefix=$MODEL_PREFIX \
    --file-path=$MODEL_CONFIG_FILE \
    --monitoring-enabled=$PROMETHEUS_MONITORING_ENABLED \
    --monitoring-path=$PROMETHEUS_MONITORING_PATH \
    --monitoring-file-path=$MONITORING_CONFIG_FILE \
    --enable-batching=$MONITORING_CONFIG_FILE \
    --max-batch-size=$MAX_BATCH_SIZE \
    --batch-timeout=$BATCH_TIMEOUT_MICROS \
    --max-enqueued-batches=$MAX_ENQUEUED_BATCHES \
    --batch-file-path=$BATCHING_CONFIG_FILE
