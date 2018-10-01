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

FROM ${TF_SERVING_BUILD_IMAGE}

# Dealing with a keyboard issue
COPY ./keyboard /etc/default/keyboard

WORKDIR /kiosk/tf-serving

ENV RPC_PORT=8500 \
    REST_PORT=8501 \
    REST_TIMEOUT=60000 \
    TF_SERVING_CONFIG_FILE=/kiosk/tf-serving/models.conf

# Copy requirements.txt and install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy python script to generate model configuration file
COPY write_config_file.py bin/entrypoint.sh ./

ENTRYPOINT "/kiosk/tf-serving/entrypoint.sh"
