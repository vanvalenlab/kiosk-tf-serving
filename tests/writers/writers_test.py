# Copyright 2016-2018 The Van Valen Lab at the California Institute of
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
"""Tests for config writer classes"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import os
import shutil
import tempfile
import six

import pytest

from writers import writers


# Workaround for python2 not supporting `with tempfile.TemporaryDirectory() as`
# These are unnecessary if not supporting python2
@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()


@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    cleanup = lambda: shutil.rmtree(dirpath)
    with cd(dirpath, cleanup):
        yield dirpath


class TestTFServingConfigWriter(object):

    def _get_writer(self):
        bucket = 'test-bucket'
        prefix = 'models'
        return writers.TFServingConfigWriter(bucket, prefix, protocol='test')

    def test_get_model_url(self):
        writer = self._get_writer()
        model_name = 'test-model'
        url = writer.get_model_url(model_name)
        assert isinstance(url, six.string_types)
        assert url.startswith(writer._storage_protocol + '://')
        assert writer.bucket in url
        assert url.endswith(writer.model_prefix + model_name)

    def test_filter_models(self):
        writer = self._get_writer()
        prefix = writer.model_prefix

        num = 5
        # empty directory outside of prefix
        objs = ['{}'.format(i) for i in range(num)]
        assert not list(writer._filter_models(objs))

        # empty directory outside of prefix, trailing "/"
        objs = ['{}'.format(i) for i in range(num)]
        assert not list(writer._filter_models(objs))

        # empty directory inside prefix
        objs = ['{}{}'.format(prefix, i) for i in range(num)]
        assert not list(writer._filter_models(objs))

        # empty directory inside of prefix, trailing "/"
        objs = ['{}{}/'.format(prefix, i) for i in range(num)]
        assert not list(writer._filter_models(objs))

        # invalid non-empty directory inside of prefix
        objs = ['{}{}/not_a_model'.format(prefix, i) for i in range(num)]
        assert not list(writer._filter_models(objs))

        # non-empty directory inside of prefix
        objs = ['{}{}/model.pB'.format(prefix, i) for i in range(num)]
        assert len(list(writer._filter_models(objs))) == num

    def test_write(self):
        writer = self._get_writer()
        # monkey-patch the get_models function
        pre = writer.model_prefix
        N = 5
        get_list = lambda: ['{}{}/model.pb'.format(pre, i) for i in range(N)]
        writer._get_models_from_bucket = get_list

        with tempdir() as dirpath:
            path = os.path.join(dirpath, 'model.conf')
            writer.write(path)
            # test existence
            assert os.path.exists(path)
            assert os.path.isfile(path)
            # test correctness
            with open(path) as f:
                content = f.readlines()
                assert content[0] == 'model_config_list: {\n'
                assert len(content) == N * 8 + 2
                clean = lambda x: x.replace(' ', '').replace('\n', '')
                for n in range(N):
                    i = n * 8 + 1  # starting line num for each model
                    assert clean(content[i]) == 'config:{'
                    inside = set([clean(c) for c in content[i + 1: i + 7]])
                    # model_name from `_get_models_from_bucket`
                    model_name = '{}{}/model.pb'.format(pre, n)
                    assert 'name:"{}"'.format(model_name) in inside
                    bp = writer.get_model_url(model_name)
                    assert 'base_path:"{}"'.format(bp) in inside

        with tempdir() as dirpath:
            path = os.path.join(dirpath, 'model.conf')
            writer._get_models_from_bucket = lambda: []
            with pytest.raises(Exception):
                writer.write(path)

    def test_get_models_from_bucket(self):
        with pytest.raises(NotImplementedError):
            self._get_writer()._get_models_from_bucket()


class TestS3ConfigWriter(object):

    def test_write(self):

        class DummyClient(object):
            def __init__(self, prefix='models', num=5):
                self.prefix = prefix
                self.num = num

            def _iter(self):
                pre = '/'.join(p for p in self.prefix.split('/') if p)
                for i in range(self.num):
                    yield {'Key': '{}/{}/model.pb'.format(pre, i)}

            def list_objects_v2(self, Bucket, StartAfter):
                contents = [x for x in self._iter()]
                return {'Contents': contents}

        N = 3
        bucket = 'test-bucket'
        prefix = 'models'
        aws_access_key_id = 'testAccessKeyId'
        aws_secret_access_key = 'testSecretAccessKey'
        writer = writers.S3ConfigWriter(bucket, prefix,
                                        aws_access_key_id,
                                        aws_secret_access_key)
        writer.client = DummyClient(prefix, N)
        with tempdir() as dirpath:
            path = os.path.join(dirpath, 'model.conf')
            writer.write(path)
            # test existence
            assert os.path.exists(path)
            assert os.path.isfile(path)
            # test correctness
            with open(path) as f:
                content = f.readlines()
                assert content[0] == 'model_config_list: {\n'
                assert len(content) == N * 8 + 2
                clean = lambda x: x.replace(' ', '').replace('\n', '')
                for n in range(N):
                    i = n * 8 + 1  # starting line num for each model
                    assert clean(content[i]) == 'config:{'
                    inside = set([clean(c) for c in content[i + 1: i + 7]])
                    assert 'name:"{}"'.format(n) in inside
                    bp = writer.get_model_url(n)
                    assert 'base_path:"{}"'.format(bp) in inside

        with tempdir() as dirpath:
            path = os.path.join(dirpath, 'model.conf')
            writer._get_models_from_bucket = lambda: []
            with pytest.raises(Exception):
                writer.write(path)
