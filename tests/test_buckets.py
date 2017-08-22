import os
import unittest

from requests import exceptions
import responses

from kbcstorage.buckets import Buckets
from kbcstorage.client import Client

from .bucket_responses import list_response, detail_response, create_response


class TestBuckets(unittest.TestCase):
    def setUp(self):
        self.client = Client(os.getenv('KBC_TEST_API_URL'),
                             os.getenv('KBC_TEST_TOKEN'))
        try:
            self.client.buckets.delete('in.c-py-test', force=True)
        except exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise

    def tearDown(self):
        try:
            self.client.drop_bucket('in.c-py-test', force=True)
        except exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise

    def test_create_bucket(self):
        bucket_id = self.client.buckets.create(name='py-test',
                                               stage='in',
                                               description='Test bucket')['id']
        self.assertTrue(self.client.buckets.exists(bucket_id))

    def test_bucket_exists(self):
        bucket_id = self.client.buckets.create(name='py-test',
                                               stage='in',
                                               description='Test bucket')['id']
        self.assertTrue(self.client.buckets.exists(bucket_id))
        self.assertFalse(
            self.client.buckets.exists('some-totally-non-existent-bucket')
        )


class TestBucketsWithMocks(unittest.TestCase):
    def setUp(self):
            token = 'dummy_token'
            base_url = 'https://connection.keboola.com/v2/storage/'
            self.buckets = Buckets(base_url, token)

    @responses.activate
    def test_list(self):
        """
        Buckets mocks list correctly.
        """
        responses.add(
            responses.Response(
                method='GET',
                url='https://connection.keboola.com/v2/storage/buckets',
                json=list_response
            )
        )
        buckets_list = self.buckets.list()
        assert isinstance(buckets_list, list)

    @responses.activate
    def test_detail_by_id(self):
        """
        Buckets mocks detail by integer id correctly.
        """
        responses.add(
            responses.Response(
                method='GET',
                url=('https://connection.keboola.com/v2/storage/buckets/'
                     'in.c-ga'),
                json=detail_response
            )
        )
        bucket_id = 'in.c-ga'
        bucket_detail = self.buckets.detail(bucket_id)
        assert bucket_detail['id'] == 'in.c-ga'

    @responses.activate
    def test_delete(self):
        """
        Buckets mock deletes bucket by id.
        """
        responses.add(
            responses.Response(
                method='DELETE',
                url='https://connection.keboola.com/v2/storage/buckets/1',
                json={}
            )
        )
        bucket_id = '1'
        deleted_detail = self.buckets.delete(bucket_id)
        assert deleted_detail is None

    @responses.activate
    def test_create(self):
        """
        Buckets mock creates new bucket.
        """
        responses.add(
            responses.Response(
                method='POST',
                url='https://connection.keboola.com/v2/storage/buckets',
                json=create_response
            )
        )
        name = 'my-new-bucket'
        description = 'Some Description'
        backend = 'snowflake'
        created_detail = self.buckets.create(name=name,
                                             description=description,
                                             backend=backend)
        assert created_detail['id'] == 'in.c-{}'.format(name)
