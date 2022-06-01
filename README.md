# ![DeepCell Kiosk Banner](https://raw.githubusercontent.com/vanvalenlab/kiosk-console/master/docs/images/DeepCell_Kiosk_Banner.png)

[![Build Status](https://github.com/vanvalenlab/kiosk-tf-serving/workflows/build/badge.svg)](https://github.com/vanvalenlab/kiosk-tf-serving/actions)
[![Coverage Status](https://coveralls.io/repos/github/vanvalenlab/kiosk-tf-serving/badge.svg?branch=master)](https://coveralls.io/github/vanvalenlab/kiosk-tf-serving?branch=master)
[![Modified Apache 2.0](https://img.shields.io/badge/license-Modified%20Apache%202-blue)](/LICENSE)

`kiosk-tf-serving` uses [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving) to serve deep learning models over gRPC and REST APIs. A configuration file can be automatically created using `python write_config_file.py` to allow any model found in a (AWS or GCS) storage bucket to be served.

TensorFlow serving will host all versions of all models in the bucket via RPC and REST APIs.

This repository is part of the [DeepCell Kiosk](https://github.com/vanvalenlab/kiosk-console). More information about the Kiosk project is available through [Read the Docs](https://deepcell-kiosk.readthedocs.io/en/master) and our [FAQ](http://www.deepcell.org/faq) page.

## Docker

Build the docker image by running

```bash
docker build --pull -t $(whoami)/kiosk-tf-serving -f docker/Dockerfile.server .
```

Run the docker image by running

```bash
# write the configuration files for a given bucket
python write_config_model.py --storage-bucket=$STORAGE_BUCKET

# mount the config files and run the image
docker run --gpus=1 -it \
    -v $PWD:/config \
    -e PORT=8500 \
    -e REST_API_PORT=8501 \
    -p 8500:8500 \
    -p 8501:8501 \
    $(whoami)/kiosk-tf-serving:latest
```

## Configuration

The `kiosk-tf-serving` can be configured using environmental variables in a `.env` file.

| Name | Description | Default Value |
| :--- | :--- | :--- |
| `STORAGE_BUCKET` | **REQUIRED**: Cloud storage bucket address (e.g. `"gs://bucket-name"`). | `""` |
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

## Contribute

We welcome contributions to the [kiosk-console](https://github.com/vanvalenlab/kiosk-console) and its associated projects. If you are interested, please refer to our [Developer Documentation](https://deepcell-kiosk.readthedocs.io/en/master/DEVELOPER.html), [Code of Conduct](https://github.com/vanvalenlab/kiosk-console/blob/master/CODE_OF_CONDUCT.md) and [Contributing Guidelines](https://github.com/vanvalenlab/kiosk-console/blob/master/CONTRIBUTING.md).

## License

This software is license under a modified Apache-2.0 license. See [LICENSE](/LICENSE) for full  details.

## Copyright

Copyright © 2018-2022 [The Van Valen Lab](http://www.vanvalen.caltech.edu/) at the California Institute of Technology (Caltech), with support from the Paul Allen Family Foundation, Google, & National Institutes of Health (NIH) under Grant U24CA224309-01.
All rights reserved.
