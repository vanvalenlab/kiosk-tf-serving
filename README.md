# kiosk-tf-serving
TensorFlow-Serving configuration files automatically generated based on the contents of a storage bucket.

### TensorFlow Serving

This repo contains the files necessary to build a container to run tensorflow serving.  The container will run `write_config_file.py` which will read files from a cloud bucket and deploy tensorflow-serving based on an auto-generated config file.  This will expose all versions of all models in the bucket via RPC API and REST API.

Compile the docker container by running

```bash
docker build --pull -t $(whoami)/kiosk-tf-serving .
```

Run the docker container by running
```bash
NV_GPU='0' nvidia-docker run -it \
    --runtime=nvidia \
    -e MODEL_PREFIX=models \
    -e RPC_PORT=8500 \
    -e REST_PORT=8501 \
    -e CLOUD_PROVIDER=aws \
    -e AWS_S3_BUCKET=YOUR_BUCKET_NAME \
    -e AWS_ACCESS_KEY_ID=YOUR_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY \
    -p 8500:8500 \
    -p 8501:8501 \
    $(whoami)/kiosk-tf-serving:latest
```
