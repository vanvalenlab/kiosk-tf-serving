# Copyright 2016-2019 The Van Valen Lab at the California Institute of
# Technology (Caltech), with support from the Paul Allen Family Foundation,
# Google, & National Institutes of Health (NIH) under Grant U24CA224309-01.
# All rights reserved.
#
# Licensed under a modified Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.github.com/vanvalenlab/kiosk-tf-serving/LICENSE
#
# The Work provided may be used for non-commercial academic purposes only.
# For any other use of the Work, including commercial use, please contact:
# vanvalenlab@gmail.com
#
# Neither the name of Caltech nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

# Using official tensorflow-serving as base image
ARG TF_SERVING_VERSION=1.11.1
ARG TF_SERVING_BUILD_IMAGE=tensorflow/serving:${TF_SERVING_VERSION}-devel-gpu

FROM ${TF_SERVING_BUILD_IMAGE}

WORKDIR /kiosk/tf-serving

ENV PORT=8500 \
    REST_API_PORT=8501 \
    REST_API_TIMEOUT=30000 \
    ENABLE_BATCHING=false \
    TF_CPP_MIN_LOG_LEVEL=0 \
    GRPC_CHANNEL_ARGS="" \
    MODEL_CONFIG_FILE=/kiosk/tf-serving/models.conf

# Copy requirements.txt and install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy python script to generate model configuration file
COPY . .

ENTRYPOINT "./bin/entrypoint.sh"
