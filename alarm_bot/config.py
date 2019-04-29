from multiprocessing import JoinableQueue

# Init queue and its lock
workQueue = JoinableQueue(10)
