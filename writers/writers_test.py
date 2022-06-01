# Copyright 2016-2022 The Van Valen Lab at the California Institute of
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

import writers


def test_get_model_config_writer():
    # Test s3:// protocol gets correct class
    writer_cls = writers.get_model_config_writer('s3://bucket-name/model-path')
    assert writer_cls is writers.S3ConfigWriter

    writer_cls = writers.get_model_config_writer('gs://bucket-name/model-path')
    assert writer_cls is writers.GCSConfigWriter

    with pytest.raises(ValueError):
        writers.get_model_config_writer('abc://bucket-name/model-path')


class TestConfigWriter(object):

    def basic_test(self, tmpdir):
        writer = writers.ConfigWriter()
        assert hasattr(writer, 'write')
        path = os.path.join(str(tmpdir), 'base.conf')
        with pytest.raises(NotImplementedError):
            writer.write(path)


class TestMonitoringConfigWriter(object):

    @pytest.mark.parametrize(
        'monitoring_path,enabled', [
            ('/monitoring/prometheus/metrics', True),
            ('/monitoring/prometheus/metrics', False),
            ('/other/path', True),
            ('/other/path', False),
        ]
    )
    def test_write(self, monitoring_path, enabled, tmpdir):
        writer = writers.MonitoringConfigWriter(enabled, monitoring_path)

        dirpath = str(tmpdir)
        path = os.path.join(dirpath, 'monitoring.conf')
        writer.write(path)

        # test existence
        assert os.path.exists(path)
        assert os.path.isfile(path)

        # test correctness
        with open(path) as f:
            content = f.readlines()
            assert len(content) == 4
            assert content[0] == 'prometheus_config: {\n'
            assert content[1] == '  enable: {},\n'.format(
                str(enabled).lower())
            assert content[2] == '  path: "{}"\n'.format(
                monitoring_path)
            assert content[3] == '}\n'


class TestBatchConfigWriter(object):

    def test_bad_inputs(self):
        # test wrong value types for each parameter
        # str instead of number yields ValueErrr
        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size='two',
                batch_timeout=0,
                max_enqueued_batches=1)

        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size=2,
                batch_timeout='zero',
                max_enqueued_batches=1)

        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size=2,
                batch_timeout=0,
                max_enqueued_batches='one')

        # test numeric values that are out of bounds.
        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size=-2,  # must be non-negative
                batch_timeout=1,
                max_enqueued_batches=1)

        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size=2,
                batch_timeout=-1,  # must be non-negative
                max_enqueued_batches=1)

        with pytest.raises(ValueError):
            writer = writers.BatchConfigWriter(
                max_batch_size=2,
                batch_timeout=1,
                max_enqueued_batches=-1)  # must be non-negative

    def test_write(self, tmpdir):
        writer = writers.BatchConfigWriter(
            max_batch_size='1',
            batch_timeout='3000000',
            max_enqueued_batches=5)

        path = os.path.join(str(tmpdir), 'batch.conf')
        writer.write(path)

        # test existence
        assert os.path.exists(path)
        assert os.path.isfile(path)

        # test correctness
        with open(path) as f:
            content = ''.join(f.readlines())
            required = [
                'max_batch_size {',
                'value: {}'.format(writer.max_batch_size),
                'batch_timeout_micros {',
                'value: {}'.format(writer.batch_timeout),
                'max_batch_size {',
                'value: {}'.format(writer.max_batch_size),
                'max_enqueued_batches {',
                'value: {}'.format(writer.max_enqueued_batches),
                'num_batch_threads {'
            ]
            for x in required:
                assert x in content


class TestModelConfigWriter(object):

    def _get_writer(self):
        bucket = 'test-bucket'
        prefix = 'models'
        return writers.writers.ModelConfigWriter(
            bucket, prefix, protocol='test')

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

    def test_write(self, tmpdir, mocker):
        writer = self._get_writer()
        # monkey-patch the get_models function
        pre = writer.model_prefix
        N = 5
        get_list = lambda: ['{}{}/model.pb'.format(pre, i) for i in range(N)]

        mocker.patch.object(writer, '_get_models_from_bucket', get_list)

        path = os.path.join(str(tmpdir), 'model.conf')
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

        mocker.patch.object(writer, '_get_models_from_bucket', lambda: [])

        path = os.path.join(str(tmpdir), 'model.conf')
        with pytest.raises(Exception):
            writer.write(path)

    def test_get_models_from_bucket(self):
        with pytest.raises(NotImplementedError):
            self._get_writer()._get_models_from_bucket()


class TestS3ConfigWriter(object):

    def test_write(self, tmpdir, mocker):

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

        mocker.patch('writers.writers.boto3.client',
                     lambda *x, **_: DummyClient(prefix, N))

        writer = writers.S3ConfigWriter(bucket, prefix,
                                        aws_access_key_id,
                                        aws_secret_access_key)

        path = os.path.join(str(tmpdir), 'model.conf')
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

        mocker.patch.object(writer, '_get_models_from_bucket', lambda: [])

        path = os.path.join(str(tmpdir), 'model.conf')
        with pytest.raises(Exception):
            writer.write(path)


class TestGSCConfigWriter(object):

    def test_write(self, tmpdir, mocker):

        class DummyBucket(object):
            def __init__(self, name, num=5):
                self.name = name
                self.num = num

        class DummyClient(object):
            def __init__(self, prefix='models', num=5):
                self.prefix = prefix
                self.name = prefix
                self.num = num

            def get_bucket(self, bucket):
                return DummyClient(bucket, self.num)

            def list_blobs(self, prefix):
                pre = '/'.join(p for p in prefix.split('/') if p)
                for i in range(self.num):
                    name = '{}/{}/model.pb'.format(pre, i)
                    yield DummyBucket(name, self.num)

        N = 3
        bucket = 'test-bucket'
        prefix = 'models'

        mocker.patch('writers.writers.storage.Client',
                     lambda *x, **_: DummyClient(prefix, N))

        writer = writers.GCSConfigWriter(bucket, prefix)

        path = os.path.join(str(tmpdir), 'model.conf')
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

        mocker.patch.object(writer, '_get_models_from_bucket', lambda: [])

        path = os.path.join(str(tmpdir), 'model.conf')
        with pytest.raises(Exception):
            writer.write(path)
