from base import CottontailBase, EXCHANGE_FANOUT


class QueueBase(CottontailBase):
    """
    A service base class for implementing work queue messaging patterns using the RabbitMQ library.
    """
    exchange_type = EXCHANGE_FANOUT

    def _bind_to_queue(self, queue, topic):
        """
        """
        pass


class QueueServer(QueueBase):
    """
    A server class for publishing messages to a queue.

    """
    pass


class QueueWorker(QueueBase):
    """
    A worker class for consuming messages in a queue.

    Overwritten methods:
        _create_channel: Alter prefetch_count
    """

    def _create_channel(self):
        """
        Instantiate a new channel on the RabbitMQ connection with a specification
        that the worker not receive more than a single message at a time. This should
        ensure fair dispatching of messages with respect to worker load.

        Returns:
            (pika.channel.Channel): The created Channel object
        """

        self._channel = super(QueueWorker, self)._create_channel()
        self._channel.basic_qos(prefetch_count=1)
        return self._channel