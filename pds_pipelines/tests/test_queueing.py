import os
import logging
from ast import literal_eval

import pytest

from pds_pipelines.queueing import QueueProcess, DIQueueProcess, UPCQueueProcess, IngestQueueProcess

@pytest.fixture
def queue_process():
    queue_process = QueueProcess('test_process', 'mro_ctx')
    queue_process.ready_queue.RemoveAll()
    return queue_process

@pytest.fixture
def di_queue_process():
    queue_process = DIQueueProcess('test_process', 'mro_ctx', volume='dummy_volume')
    queue_process.ready_queue.RemoveAll()
    return queue_process

@pytest.fixture
def upc_queue_process():
    queue_process = UPCQueueProcess('test_process', 'mro_ctx', volume='dummy_volume')
    queue_process.ready_queue.RemoveAll()
    return queue_process

@pytest.fixture
def ingest_queue_process():
    queue_process = IngestQueueProcess('test_process', 'mro_ctx', volume='dummy_volume')
    queue_process.ready_queue.RemoveAll()
    return queue_process

def test_queue_process_logger(queue_process):
    logger = queue_process.get_logger(log_level='INFO')

    assert isinstance(logger, logging.Logger)

def test_queue_process_archive_att(queue_process):
    mro_path = queue_process.get_archive_att('path')
    assert mro_path == "/pds_san/PDS_Archive/Mars_Reconnaissance_Orbiter/CTX/"

def test_queue_process_bad_archive_att(queue_process):
    with pytest.raises(KeyError):
        mro_path = queue_process.get_archive_att('fruit')

def test_queue_process_run(queue_process):
    try:
        queue_process.run(elements=['banana', 'apple'], copy=False)
        assert False
    except Exception as e:
        assert True

# Bad test, would need to be run against a populated DI database
def test_di_queue_process_matching_files(di_queue_process):
    res = di_queue_process.get_matching_files().all()
    assert len(res) == 0

def test_di_queue_process_enqueue(di_queue_process):
    di_queue_process.enqueue('Banana.txt')
    item = literal_eval(di_queue_process.ready_queue.QueueGet())
    assert  item[0] == 'Banana.txt'
    assert  item[1] == 'mro_ctx'

def test_di_queue_process_run(di_queue_process):
    try:
        di_queue_process.run(elements=['Banana.txt', 'Apple.txt'], copy=False)
        assert di_queue_process.ready_queue.QueueSize() == 2
        item = literal_eval(di_queue_process.ready_queue.QueueGet())
        assert  item[0] == os.path.join(di_queue_process.get_archive_att('path'), 'Banana.txt')
        assert  item[1] == 'mro_ctx'
    except Exception as e:
        assert False

# Bad test, would need to be run against a populated DI database
def test_upc_queue_process_matching_files(upc_queue_process):
    res = upc_queue_process.get_matching_files().all()
    assert len(res) == 0

def test_upc_queue_process_enqueue(upc_queue_process):
    upc_queue_process.enqueue('Banana.txt')
    item = literal_eval(upc_queue_process.ready_queue.QueueGet())
    assert  item[0] == 'Banana.txt'
    assert  item[1] == 'mro_ctx'

# Bad test, would need to be run against real file system
def test_ingest_queue_process_matching_files(ingest_queue_process):
    res = ingest_queue_process.get_matching_files()
    assert len(res) == 0

@pytest.mark.parametrize("element, queue",
                        [('Banana.txt', 'ready'),
                         ('voldesc.cat', 'link')])
def test_ingest_queue_process_enqueue(ingest_queue_process, queue, element):
    ingest_queue_process.enqueue(element)
    if queue == 'ready':
        item = literal_eval(ingest_queue_process.ready_queue.QueueGet())
    elif queue == 'link':
        item = literal_eval(ingest_queue_process.link_queue.QueueGet())
    assert  item[0] == element
    assert  item[1] == 'mro_ctx'
