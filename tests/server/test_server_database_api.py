import pytest
from hive.server.database_api.methods import list_comments
from hive.steem.client import SteemClient

@pytest.fixture
def client():
  return SteemClient(url='https://api.hive.blog')

def test_list_comments_by_cashout_time(client):
  reference_data = await client.list_comments({"start":["1990-01-01T00:00:00","steemit","firstpost"],"limit":10,"order":"by_cashout_time"})
  test_data = await list_comments(["1990-01-01T00:00:00","steemit","firstpost"],10,"by_cashout_time")
  assert reference_data
  assert test_data
  assert len(reference_data) == len(test_data)
  to_compare = ['author','permlink']
  for idx in range(len(reference_data)):
    for key in to_compare:
      assert reference_data[idx][key] == test_data[idx][key]
    assert reference_data[idx]['cashout_time'] == test_data[idx]['payout_at']

def test_list_comments_by_permlink(client):
  reference_data = await client.list_comments({"start":["steemit","firstpost"],"limit":10,"order":"by_permlink"})
  test_data = await list_comments(["steemit","firstpost"],10,"by_permlink")
  assert reference_data
  assert test_data
  assert len(reference_data) == len(test_data)
  to_compare = ['author','permlink']
  for idx in range(len(reference_data)):
    for key in to_compare:
      assert reference_data[idx][key] == test_data[idx][key]

def test_list_comments_by_root(client):
  reference_data = await client.list_comments({"start":["steemit","firstpost","",""],"limit":10,"order":"by_root"})
  test_data = await list_comments(["steemit","firstpost","",""],10,"by_root")
  assert reference_data
  assert test_data
  assert len(reference_data) == len(test_data)
  to_compare = ['author','permlink','root_author','root_permlink']
  for idx in range(len(reference_data)):
    for key in to_compare:
      assert reference_data[idx][key] == test_data[idx][key]

def test_list_comments_by_parent(client):
  reference_data = await client.list_comments({"start":["steemit","firstpost","",""],"limit":10,"order":"by_parent"})
  test_data = await list_comments(["steemit","firstpost","",""],10,"by_parent")
  assert reference_data
  assert test_data
  assert len(reference_data) == len(test_data)
  to_compare = ['author','permlink','parent_author','parent_permlink']
  for idx in range(len(reference_data)):
    for key in to_compare:
      assert reference_data[idx][key] == test_data[idx][key]