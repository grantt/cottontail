Cottontail Examples
===================

Work Queue
----------
Example files located at: cottontail/examples/queue

Work queues are designed to run resource intensive processes on a scheduled basis instead of immediately.

In this example, tasks to be executed are mapped to messages. The server dispatches messages to the queue as it needs, and the worker reads the next message only after it has completed its callback action, thus limiting load on the workers.

Pub/Sub
-------
Example files located at: cottontail/examples/pubsub


Topics
------
Example files located at: cottontail/examples/topics


RPC
---
Example files located at: cottontail/examples/rpc