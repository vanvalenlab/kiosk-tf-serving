# kiosk-tf-serving

[![Build Status](https://travis-ci.org/vanvalenlab/kiosk-tf-serving.svg?branch=master)](https://travis-ci.org/vanvalenlab/kiosk-tf-serving)
[![Coverage Status](https://coveralls.io/repos/github/vanvalenlab/kiosk-tf-serving/badge.svg?branch=master)](https://coveralls.io/github/vanvalenlab/kiosk-tf-serving?branch=master)

TensorFlow-Serving configuration files automatically generated based on the contents of a storage bucket.  `write_config_file.py` will automatically read the contents of the storage bucket and write a configuration file for tensorflow-serving.

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
    -e MODEL_PREFIX=models \
    -e PORT=8500 \
    -e REST_API_PORT=8501 \
    -e REST_API_TIMEOUT=30000 \
    -e CLOUD_PROVIDER=aws \
    -e AWS_S3_BUCKET=YOUR_BUCKET_NAME \
    -e AWS_ACCESS_KEY_ID=YOUR_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY \
    -p 8500:8500 \
    -p 8501:8501 \
    $(whoami)/kiosk-tf-serving:latest
```
