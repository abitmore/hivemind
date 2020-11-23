""" Data provider for test operations """
import datetime
import dateutil.parser

from hive.indexer.mock_data_provider import MockDataProvider, MockDataProviderException

class MockBlockProvider(MockDataProvider):
    """ Data provider for test ops """

    min_block = 0
    max_block = 0

    last_real_block_num = 1
    last_real_block_time = dateutil.parser.isoparse("2016-03-24T16:05:00")

    @classmethod
    def set_last_real_block_num_date(cls, block_num, block_date):
        cls.last_real_block_num = int(block_num)
        cls.last_real_block_time = dateutil.parser.isoparse(block_date)

    @classmethod
    def load_block_data(cls, data_path):
        cls.block_data.clear()
        cls.min_block = 0
        cls.max_block = 0

        super().load_block_data(data_path)

    @classmethod
    def add_block_data_from_file(cls, file_name):
        from json import load
        data = {}
        with open(file_name, "r") as src:
            data = load(src)
        for block_num, block_data in data.items():
            assert isinstance(block_num, str), "Expected string as block_num"
            assert isinstance(block_data, dict), "Expected dict as block_data"
            cls.add_block_data(block_num, block_data)

    @classmethod
    def add_block_data(cls, _block_num, block_data):
        block_num = int(_block_num)

        if block_num > cls.max_block:
            cls.max_block = block_num
        if block_num < cls.min_block:
            cls.min_block = block_num

        if block_num in cls.block_data:
            if 'transactions' in cls.block_data[block_num] and 'transactions' in block_data:
                cls.block_data[block_num]['transactions'].extend(block_data['transactions'])
            if 'transaction_ids' in cls.block_data[block_num] and 'transaction_ids' in block_data:
                cls.block_data[block_num]['transaction_ids'].extend(block_data['transaction_ids'])
        else:
            cls.block_data[block_num] = block_data

    @classmethod
    def get_block_data(cls, block_num, make_on_empty=False):
        data = cls.block_data.get(block_num, None)
        if make_on_empty and data is None:
            data = cls.make_empty_block(block_num)
            if data is None:
                raise MockDataProviderException("No more blocks to serve")
        return data

    @classmethod
    def get_max_block_number(cls):
        return cls.max_block

    @classmethod
    def make_block_id(cls, block_num):
        return "{:08x}00000000000000000000000000000000".format(block_num)

    @classmethod
    def make_block_timestamp(cls, block_num):
        block_delta = block_num - cls.last_real_block_num
        time_delta = datetime.timedelta(days=0, seconds=block_delta*3, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        ret_time = cls.last_real_block_time + time_delta
        return ret_time.replace(microsecond=0).isoformat()

    @classmethod
    def make_empty_block(cls, block_num, witness="initminer"):
        block_data = {
            "previous": cls.make_block_id(block_num - 1),
            "timestamp": cls.make_block_timestamp(block_num),
            "witness": witness,
            "transaction_merkle_root": "0000000000000000000000000000000000000000",
            "extensions": [],
            "witness_signature": "",
            "transactions": [],
            "block_id": cls.make_block_id(block_num),
            "signing_key": "",
            "transaction_ids": []
            }
        # supply enough blocks to fill block queue with empty blocks only
        # throw exception if there is no more data to serve
        if cls.min_block < block_num < cls.max_block + 3:
            return block_data
        return None
