#pylint: disable=missing-docstring
#pylint: disable=redefined-outer-name
import datetime
import pytest

from hive.utils.normalize import parse_time
from hive.steem.client import SteemClient

@pytest.fixture
def client():
    return SteemClient(url='https://api.hive.blog')

def test_instance(client):
    assert isinstance(client, SteemClient)

def test_stream_blocks(client):
     start_at = client.last_irreversible()
     stop_at = client.head_block() + 2
     streamed = 0

     def breaker():
         return True

     def exception_report():
         pass

     with pytest.raises(KeyboardInterrupt):
      for block in client.stream_blocks(start_at, trail_blocks=0, max_gap=100, breaker=breaker, exception_reporter = exception_report):
          num = block.get_num()
          assert num == start_at + streamed
          streamed += 1
          if streamed >= 20 and num >= stop_at:
              raise KeyboardInterrupt
     assert streamed >= 20
     assert num >= stop_at

def test_head_time(client):
    head = parse_time(client.head_time())
    assert head > datetime.datetime.now() - datetime.timedelta(minutes=15)

def test_head_block(client):
    assert client.head_block() > 23e6

def test_last_irreversible(client):
    assert client.last_irreversible() > 23e6

def test_gdgp_extended(client):
    ret = client.gdgp_extended()
    assert 'dgpo' in ret
    assert 'head_block_number' in ret['dgpo']
    assert 'usd_per_steem' in ret

def test_get_blocks_range(client):
    def breaker():
        return True
    lbound = 23000000
    blocks = client.get_blocks_range(lbound, lbound + 5, breaker)
    assert len(blocks) == 5
