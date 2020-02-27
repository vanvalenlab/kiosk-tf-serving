# kiosk-tf-serving

[![Build Status](https://travis-ci.org/vanvalenlab/kiosk-tf-serving.svg?branch=master)](https://travis-ci.org/vanvalenlab/kiosk-tf-serving)
[![Coverage Status](https://coveralls.io/repos/github/vanvalenlab/kiosk-tf-serving/badge.svg?branch=master)](https://coveralls.io/github/vanvalenlab/kiosk-tf-serving?branch=master)

`kiosk-tf-serving` uses [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving) to serve deep learning models over gRPC API and REST API. A configuration file is automatically created on startup which allows any model found in a (AWS or GCS) storage bucket to be served.

TensorFlow serving will host all versions of all models in the bucket via RPC API and REST API.

## Docker

Compile the docker container by running

```bash
docker build --pull -t $(whoami)/kiosk-tf-serving .
```

Run the docker container by running

```bash
NV_GPU='0' nvidia-docker run -it \
    --runtime=nvidia \
    -e PORT=8500 \
    -e REST_API_PORT=8501 \
    -e STORAGE_BUCKET=YOUR_BUCKET_NAME \
    -e MODEL_PREFIX=models \
    -p 8500:8500 \
    -p 8501:8501 \
    $(whoami)/kiosk-tf-serving:latest
```

## Environmental Variables

The `kiosk-tf-serving` can be configured using environmental variables in a `.env` file.

| Name | Description | Default Value |
| :--- | :--- | :--- |
| `STORAGE_BUCKET` | **REQUIRED**: Cloud storage bucket address (e.g. `"gs://bucket-name"`). | `""` |
| `CLOUD_PROVIDER` | **REQUIRED**: The cloud provider hosting the DeepCell Kiosk. | `"gke"` |
| `PORT` | Port to listen on for gRPC API. | `8500` |
| `REST_API_PORT` | Port to listen on for HTTP/REST API. | `8501` |
| `REST_API_TIMEOUT` | Timeout in ms for HTTP/REST API calls. | `30000` |
| `GRPC_CHANNEL_ARGS` | Optional channel args for the gRPC API. | `""` |
| `MODEL_PREFIX` | Prefix of model directory in the cloud storage bucket. | `"/models"` |
| `MODEL_CONFIG_FILE` | Path of the model configuration file written by `write_config_file.py`. | `"/kiosk/tf-serving/models.conf"` |
| `ENABLE_BATCHING` | Whether to enable batching in TensorFlow Serving. | `true` |
| `MAX_BATCH_SIZE` | Maximum number of items in a batch. | `1` |
| `MAX_ENQUEUED_BATCHES` | Number of jobs to keep in queue to be processed. Jobs may take a long time if this value is too high. | `128` |
| `BATCH_TIMEOUT_MICROS` | The maximum amount of time in ms to wait before executing a batch. | `0` |
| `BATCHING_CONFIG_FILE` | Path of the batching configuration file created by `write_config_file.py`. | `"/kiosk/tf-serving/batching_config.txt"` |
| `PROMETHEUS_MONITORING_ENABLED` |  If `true`, a monitoring configuration file is written. | `true` |
| `PROMETHEUS_MONITORING_PATH` |  Prometheus scraping endpoint used if `PROMETHEUS_MONITORING_ENABLED`. | `"/monitoring/prometheus/metrics"` |
| `MONITORING_CONFIG_FILE` |  Path of the monitoring configuration file created by `write_config_file.py`. | `"/kiosk/tf-serving/monitoring_config.txt"` |
| `TF_CPP_MIN_LOG_LEVEL` | The log level of TensorFlow Serving. | `0` |
