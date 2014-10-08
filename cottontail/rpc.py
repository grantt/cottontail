import uuid
import pika
from base import CottontailBase, EXCHANGE_FANOUT


class RPCBase(CottontailBase):
    """
    A service base class for implementing RPC messaging patterns using the RabbitMQ library.
    """
    def _declare_exchange(self, exchange_name):
        pass

    def _bind_to_queue(self, queue, topic):
        pass


class RPCServer(RPCBase):
    """
    A server class for handling RPC requests.

    Overwritten methods:
        _create_channel: Alter prefetch_count
        _on_message:

    Additional methods:
        _process_message:
        _execute_call:
    """
    def _create_channel(self):
        """
        Instantiate a new channel on the RabbitMQ connection with a specification
        that the worker not receive more than a single message at a time. This should
        ensure fair dispatching of messages with respect to worker load.

        Returns:
            (pika.channel.Channel): The created Channel object
        """

        self._channel = super(RPCServer, self)._create_channel()
        self._channel.basic_qos(prefetch_count=1)
        return self._channel

    def _on_message(self, channel, basic_deliver, properties, body):
        args, kwargs = self._process_message(body)

        self.logger.info("Executing RPC function")
        response = self._execute_call(*args, **kwargs)

        self.logger.info("Returning response message")
        channel.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=str(response)
        )

        super(RPCServer, self)._on_message(channel, basic_deliver, properties, body)

    def _process_message(self, body):
        return [], {}

    def _execute_call(self, *args, **kwargs):
        pass


class RPCClient(RPCBase):
    """
    A client class for submitting RPC requests.

    Overridden methods:
        __init__:
        _bind_to_queue:
        _on_message:
        _declare_exchange:

    Additional methods
        call:
        _compose_message

    Attributes:
        callback_queue (string): Name of the callback queue
    """
    def __init__(self, **kw):
        super(RPCClient, self).__init__(**kw)

        # Automatically subscribe to a callback queue
        self.callback_queue = self.subscribe(exclusive=True, acknowledge=False)

        # Initialize response
        self.response = None

    def _on_message(self, channel, basic_deliver, properties, body):
        self.logger.info("Routing RPC request {}:{}".format(basic_deliver.routing_key, body))
        if self.correlation_id == properties.correlation_id:
            self.response = body

    def call(self, function, *fn_args, **fn_kwargs):
        self.response = None
        self.correlation_id = str(uuid.uuid4())

        body = self._compose_message(*fn_args, **fn_kwargs)

        self._channel.basic_publish(
            exchange='',
            routing_key=function,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
            ),
            body=body)
        while self.response is None:
            self._connection.process_data_events()
        return self.response

    def _compose_message(self, *fn_args, **fn_kwargs):
        return ''