import os
from nose import with_setup
from nose import SkipTest
from nose.tools import assert_true
from nose.tools import assert_false
from nose.tools import assert_equal

from nxdrive.client import NuxeoClient


TEST_WORKSPACE = '/default-domain/workspaces/test-nxdrive'

nxclient = None


def setup_integration_server():
    global nxclient
    NUXEO_URL = os.environ.get('NXDRIVE_TEST_NUXEO_URL')
    USER = os.environ.get('NXDRIVE_TEST_USER')
    PASSWORD = os.environ.get('NXDRIVE_TEST_PASSWORD')
    if None in (NUXEO_URL, USER, PASSWORD):
        raise SkipTest("No integration server configuration found in "
                       "environment.")
    nxclient = NuxeoClient(NUXEO_URL, USER, PASSWORD)

    parent_path = os.path.dirname(TEST_WORKSPACE)
    workspace_name = os.path.basename(TEST_WORKSPACE)
    nxclient.create(parent_path, 'Workspace', name=workspace_name,
                    properties={'dc:title': 'Nuxeo Drive Tests'})


def teardown_integration_server():
    if nxclient is not None and nxclient.exists(TEST_WORKSPACE):
        nxclient.delete(TEST_WORKSPACE)


with_integration_server = with_setup(
    setup_integration_server, teardown_integration_server)


@with_integration_server
def test_authenticate():
    assert_true(nxclient.authenticate())

    bad_client = NuxeoClient(nxclient.server_url,
                             'someone else',
                             'bad password')
    assert_false(bad_client.authenticate())


@with_integration_server
def test_make_documents():
    doc1 = nxclient.make_file(TEST_WORKSPACE, 'Document_1.txt')
    assert_true(nxclient.exists(doc1))
    assert_equal(nxclient.get_content(doc1), "")

    doc2 = nxclient.make_file(TEST_WORKSPACE, 'Document_2.txt',
                              content='Some text.')
    assert_true(nxclient.exists(doc2))
    assert_equal(nxclient.get_content(doc2), "Some text.")

    nxclient.delete(doc2)
    assert_true(nxclient.exists(doc1))
    assert_false(nxclient.exists(doc2))


# TODO: add tests with long file names and special characters