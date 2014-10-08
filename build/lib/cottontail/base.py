import pika
import errors
import utils

EXCHANGE_DIRECT = u'direct'
EXCHANGE_TOPIC = u'topic'
EXCHANGE_FANOUT = u'fanout'
EXCHANGE_HEADERS = u'headers'
EXCHANGE_TYPES = {EXCHANGE_DIRECT, EXCHANGE_TOPIC, EXCHANGE_FANOUT, EXCHANGE_HEADERS}


class CottontailBase(object):
    """
    A service base class for implementing messaging patterns using the RabbitMQ library.
    Supported patterns include pub/sub, RPC, topic subscription, and work queues.

    Args:
        exchange_name (str, optional): Name of the message exchange to create, defaults to ''.
        hostname (str, optional): Hostname for this pub/sub client, defaults to 'localhost'.
        port (int, optional): Numeric port for this pub/sub client, defaults to '5672'.
        exchange_type (str, optional): Exchange type to create ('headers', 'topic', 'direct', 'fanout'),
            defaults to 'direct'.
        confirm_delivery (bool, optional): Whether to request 'ack' messages from consumers, default is True.
        logger (module, optional): The logging module to use with this Client instance, default is 'utils.logger'.

    Attributes:
        logger (module): The logging module to use with this Client instance.
        exchange_name (string): Exchange name to create, default '', the default exchange.
        exchange_type (string): Exchange type to create ('headers', 'topic', 'direct', or 'fanout'), default 'direct'.
        exchange (tuple): The exchange name and type represented as a tuple.

    Raises:
        CottontailError: If exchange_type is not in the valid EXCHANGE_TYPES.
    """

    exchange_type = EXCHANGE_DIRECT

    def __init__(self, exchange_name='', hostname='localhost', port=5672, logger=utils.logger):
        # Setup logging
        self.logger = logger

        # Initial setup of the connection to the Pika core
        self.logger.info("Setting up a pika connection on {}:{}".format(hostname, port))
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=hostname,
                port=port
            )
        )

        self._channel = self._create_channel()

        self._declare_exchange(exchange_name)

    def _declare_exchange(self, exchange_name):
        """
        Setup the exchange on RabbitMQ

        Raises:
            CottontailError: If exchange_type is not in the valid EXCHANGE_TYPES.

        """
        # Validate the exchange type
        if self.exchange_type not in EXCHANGE_TYPES:
            raise errors.CottontailError("'{}' is not a valid exchange type".format(self.exchange_type), errors.INVALID)

        # Declare our new exchange with type
        self.exchange_name = exchange_name
        self.exchange = (self.exchange_name, self.exchange_type)

        self.logger.info("Declaring exchange '{}' of type '{}' on channel '{}'".format(
            exchange_name,
            self.exchange_type,
            self._channel
        ))

        if not self.exchange_name:
            self.logger.warn("Using the default exchange ('') makes subscription unavailable")

        self._channel.exchange_declare(*self.exchange)

    def _create_channel(self):
        """
        Instantiate a new channel on the RabbitMQ connection

        Returns:
            (pika.channel.Channel): The created Channel object
        """

        self.logger.info("Setting up a new channel on the connection")
        return self._connection.channel()

    def declare_queue(self, name, durable=True, exclusive=False):
        """
        Args:
            name (string): Name of the queue to declare

            durable (bool, optional): Survive reboots of the broker, defaults to True so we can increase reliability.
            exclusive (bool, optional): Only allow access by the current connection, defaults to True.

        Returns:
            basestring: The name of the successfully declared queue
        """

        params = {
            'durable': durable,
            'exclusive': exclusive,
        }
        if name:
            params['queue'] = name

        self.logger.info("Declaring queue '{}' on channel '{}'".format(name, self._channel))
        result = self._channel.queue_declare(**params)

        return result.method.queue

    def delete_queue(self, name):
        """
        Args:
            name (string): Name of the queue to delete
            if_unused (bool, optional): only delete if it's unused
            if_empty (bool, optional): only delete if the queue is empty
            nowait (bool, optional): Do not wait for a Queue.DeleteOk

        Raises:
            TypeError: If 'name' is not a string
        """

        if not isinstance(name, basestring):
            raise TypeError("You must specify a queue's 'name' as a string.")

        self.logger.info("Deleting queue '{}' on channel '{}'".format(name, self._channel))
        self._channel.queue_delete(
            queue=name,
            if_unused=False,
            if_empty=False,
            nowait=False)

    def _bind_to_queue(self, queue, topic):
        """

        """

        self.logger.info("Binding to queue: '{}' on exchange: '{}'. Looking for messages of topic: '{}'".format(
            queue,
            self.exchange_name,
            topic
        ))
        self._channel.queue_bind(exchange=self.exchange_name, queue=queue, routing_key=topic)

    def publish(self, topic, content):
        """
        Publish a message with a specified topic to the exchange

        Args:
            topic (str): The topic of the message, to be read by subscribers of that topic.
            content (str): The contents of the message to be sent

        Raises:
            TypeError: If 'content' is not a string
        """

        if not isinstance(content, basestring):
            raise TypeError("You must specify a message as a string.")

        # Format the message as a : separated string
        message = "{}:{}".format(topic, content)
        self.logger.info('Sending message :{}:{}'.format(topic, content))
        self._channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=topic,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    def subscribe(self, queue_name=None, topic=None, acknowledge=True, exclusive=False):
        """
        Subscribe to the messages of a particular queue

        Args:
            queue_name (basestring, optional): The name of the queue to subscribe to, defaults to None.
            topic (basestring, optional): The topic or key to filter messages by, defaults to None.
            acknowledge (bool, optional): Whether to send an 'ack' message back to the
                producer upon message receipt, default is True.

        Returns:
            bool: True if successful

        Raises:
            CottontailError: If a subscription is issued to the default ('') exchange.
                See http://docs.oasis-open.org/amqp/core/v1.0/amqp-core-complete-v1.0.pdf for details.
        """

        # if not self.exchange_name:
        #     raise errors.CottontailError("The default exchange is not eligible for subscription", errors.INVALID)

        queue = self.declare_queue(queue_name, exclusive=exclusive)

        self._bind_to_queue(queue, topic)

        # self.logger.info('Subscribing to topic: {}'.format(topic))
        self._channel.basic_consume(self._on_message, queue=queue, no_ack=not acknowledge)

        return queue

    def listen(self):
        """
        Listen continuously on the subscriber socket for incoming messages.
        """
        self.logger.info('Listening for messages...')
        self._channel.start_consuming()

    def acknowledge(self, message_receipt):
        """
        Acknowledge the message delivery from RabbitMQ by sending a Basic.Ack RPC method for the delivery tag.

        Args:
            message_receipt (int): The delivery tag from the Basic.Deliver frame

        """
        self.logger.info('Acknowledging message: {}'.format(message_receipt))
        self._channel.basic_ack(message_receipt)

    def close_connection(self):
        """
        Closes the connection to RabbitMQ

        Returns:
            bool: True if successful
        """

        self.logger.info('Closing connection: {}'.format(self._connection))
        self._connection.close()

        return True

    ####################
    # Callback methods #
    ####################

    def _on_exchange_declare_ok(self, unused_frame):
        """
        Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        Args:
            unused_frame (pika.Frame.Method): Exchange.DeclareOk response frame

        """
        self.logger.info('Exchange declared')

    def _on_message(self, channel, basic_deliver, properties, body):
        """
        Default callback for message delivery, used to handle messages and
        acknowledge receipt.

        Args:
            channel (pika.channel.Channel): The Channel object
            basic_deliver (pika.Spec.Basic.Deliver): The basic_deliver object, carrying
                the exchange, routing_key, delivery tag, and a redelivered flag
            properties (pika.Spec.BasicProperties): An instance of BasicProperties with
                the message properties
            body (basestring): The message that was delivered.
        """
        self.logger.info("Handling message {}:{}".format(basic_deliver.routing_key, body))
        self.acknowledge(basic_deliver.delivery_tag)


    # Future Callbacks, dependent on non-blocking Connection Adapters
    # http://pika.readthedocs.org/en/latest/modules/adapters/index.html

    def _on_declare_queue_ok(self, method_frame):
        """
        Default success callback for queue declaration

        Args:
            method_frame (pika.frame.Method): The Queue.DeclareOk frame
        """
        self.logger.info('Queue declared')

    def _on_delete_queue_ok(self, method_frame):
        """
        Default success callback for queue deletion

        Args:
            method_frame (pika.frame.Method): The Queue.DeleteOk frame
        """
        self.logger.info('Queue deleted')
