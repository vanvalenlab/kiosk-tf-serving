# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG TF_SERVING_VERSION=1.10.1
ARG TF_SERVING_BUILD_IMAGE=tensorflow/serving:${TF_SERVING_VERSION}-devel-gpu

FROM ${TF_SERVING_BUILD_IMAGE} as build_image
FROM nvcr.io/vvlab/tensorflow:18.04-py3
#FROM nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04

ARG TF_SERVING_VERSION_GIT_BRANCH=master
ARG TF_SERVING_VERSION_GIT_COMMIT=head

LABEL maintainer="gvasudevan@google.com"
LABEL tensorflow_serving_github_branchtag=${TF_SERVING_VERSION_GIT_BRANCH}
LABEL tensorflow_serving_github_commit=${TF_SERVING_VERSION_GIT_COMMIT}

# Dealing with a keyboard issue
COPY ./keyboard /etc/default/keyboard

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        ca-certificates \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
        #nvidia-cuda-toolkit \

# Install TF Serving GPU pkg
COPY --from=build_image /usr/local/bin/tensorflow_model_server /usr/bin/tensorflow_model_server

# Including our functions
COPY generate_config.py /opt/generate_config.py
COPY tf_serving_startup.sh /
RUN chmod 755 /tf_serving_startup.sh
CMD ["/bin/sh", "-c", "/tf_serving_startup.sh"]


#CMD ["/bin/bash"]
