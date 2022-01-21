from ast import literal_eval

import pytest

from pds_pipelines.redis_lock import RedisLock
from pds_pipelines.redis_queue import RedisQueue, conditional_decode

@pytest.fixture
def general_queue():
    queue = RedisQueue('UPC_ReadyQueue', namespace = None)
    queue.RemoveAll()
    queue.QueueAdd(("/Path/to/my/file.img", "1", "ARCHIVE"))
    queue.QueueAdd(("/Path/to/my/file2.img", "2", "ARCHIVE"))
    queue.QueueAdd(("/Path/to/my/file3.img", "3", "ARCHIVE"))
    return queue

def test_redis_queue_name(general_queue):
    assert general_queue.getQueueName() == 'randomuser_queue:UPC_ReadyQueue'

def test_redis_queue_size(general_queue):
    assert general_queue.QueueSize() == 3

def test_redis_queue_add_get(general_queue):
    item = literal_eval(general_queue.QueueGet())
    inputfile = item[0]
    fid = item[1]
    archive = item[2]

    assert inputfile == "/Path/to/my/file.img"
    assert fid == "1"
    assert archive == "ARCHIVE"

def test_redis_queue_add_listget(general_queue):
    items = general_queue.ListGet()

    assert len(items) == 3

def test_redis_queue_add_recipeget(general_queue):
    item = general_queue.RecipeGet()

    assert item == "('/Path/to/my/file.img', '1', 'ARCHIVE')"

def test_redis_queue_qfile2qwork(general_queue):
    work_queue = RedisQueue('UPC_WorkQueue', namespace = None)

    item = general_queue.Qfile2Qwork(general_queue, work_queue)
    work_item = work_queue.QueueGet()
    assert item == work_item
