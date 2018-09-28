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

RUN apt-get update && apt-get install -y python3 \
        python3-pip

RUN pip3 install boto3 \
        google-cloud-storage \
        python-decouple

# Including our functions
COPY generate_config.py tf_serving_startup.sh /opt/
RUN chmod 755 /opt/tf_serving_startup.sh

#CMD sleep 10000
CMD ["/bin/sh", "-c", "/opt/tf_serving_startup.sh"]
