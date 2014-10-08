from base import CottontailBase, EXCHANGE_FANOUT


class PubSubBase(CottontailBase):
    """
    A service base class for implementing pub/sub messaging patterns using the RabbitMQ library.
    """
    exchange_type = EXCHANGE_FANOUT


class Publisher(PubSubBase):
    """
    A server class for publishing messages in a pub/sub pattern.

    Overwritten methods:
        _bind_to_queue: Not necessary for a queue publisher, only a subscriber
    """

    def _bind_to_queue(self, queue, topic):
        pass


class Subscriber(PubSubBase):
    """
    A worker class for consuming messages in a pub/sub pattern.

    """
    pass