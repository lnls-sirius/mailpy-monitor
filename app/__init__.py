import queue

SMS_MAX_QUEUE_SIZE = 1000
SMS_QUEUE = queue.Queue(maxsize=SMS_MAX_QUEUE_SIZE)
