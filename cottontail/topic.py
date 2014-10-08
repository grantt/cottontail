from base import CottontailBase, EXCHANGE_TOPIC


class TopicBase(CottontailBase):
    """
    A service base class for implementing work queue messaging patterns using the RabbitMQ library.
    """
    exchange_type = EXCHANGE_TOPIC


class TopicPublisher(TopicBase):
    """
    A server class for publishing messages in a pub/sub pattern.

    Overwritten methods:
        _bind_to_queue: Not necessary for a queue publisher, only a subscriber
    """

    def _bind_to_queue(self, queue, topic):
        pass


class TopicSubscriber(TopicBase):
    """
    A worker class for consuming messages of a particular topic in a pub/sub pattern.

    """
    pass