#!/bin/bash

# Add options for tensorflow_model_server based on settings
export options=(
  "--port=$PORT"
  "--rest_api_port=$REST_API_PORT"
  "--rest_api_timeout_in_ms=$REST_API_TIMEOUT"
  "--enable_batching=$ENABLE_BATCHING"
  "--grpc_channel_arguments=$GRPC_CHANNEL_ARGS"
  "--tensorflow_session_parallelism=$TF_SESSION_PARALLELISM"
  "--model_config_file=$MODEL_CONFIG_FILE"
)

# If PROMETHEUS_MONITORING_ENABLED, provide the monitoring config file.
if [ "${PROMETHEUS_MONITORING_ENABLED}" == "true" ] ; then
  echo "Using monitoring config file: $MONITORING_CONFIG_FILE"
  options+=("--monitoring_config_file=$MONITORING_CONFIG_FILE") ;
fi

# If ENABLE_BATCHING, provide the batching config file.
if [ "${ENABLE_BATCHING}" == "true" ] ; then
  echo "Using batching config file: $BATCHING_CONFIG_FILE"
  options+=("--batching_parameters_file=$BATCHING_CONFIG_FILE") ;
fi

tensorflow_model_server "${options[@]}" && /bin/bash # don't exit
