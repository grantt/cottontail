import pika
import errors
import utils

EXCHANGE_DIRECT = u'direct'
EXCHANGE_TOPIC = u'topic'
EXCHANGE_FANOUT = u'fanout'
EXCHANGE_HEADERS = u'headers'
EXCHANGE_TYPES = {EXCHANGE_DIRECT, EXCHANGE_TOPIC, EXCHANGE_FANOUT, EXCHANGE_HEADERS}


class CottontailClient(object):
    """
    A client for implementing messaging patterns using the RabbitMQ library.
    Supported patterns include pub/sub, RPC, and work queues.

    Args:
        exchange_name (str): Name of the message exchange to create

        hostname (str, optional): Hostname for this pub/sub client, defaults to 'localhost'.
        port (int, optional): Numeric port for this pub/sub client, defaults to '5555'.
        exchange_type (str, optional): Exchange type to create ('headers', 'topic', 'direct', 'fanout'),
            defaults to 'direct'.
        confirm_delivery (bool, optional): Whether to request 'ack' messages from consumers, default is True.
        logger (module, optional): The logging module to use with this Client instance, default is 'utils.logger'.

    Attributes:
        logger (module): The logging module to use with this Client instance

    Raises:
        CottontailError: If exchange_type is not in the valid EXCHANGE_TYPES
    """

    def __init__(self, exchange_name, hostname='localhost', port=5672, exchange_type=EXCHANGE_DIRECT,
                 confirm_delivery=True, logger=utils.logger):

        # Setup logging
        self.logger = logger

        if exchange_type not in EXCHANGE_TYPES:
            raise errors.CottontailError(u"'{}' is not a valid exchange type".format(exchange_type), errors.INVALID)

        # Initial setup of the connection to the Pika core
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
        self._channel = self._connection.channel()
        self.exchange = exchange_name

        # Declare our new exchange with type
        self._channel.exchange_declare(exchange=self.exchange, type=exchange_type)

        # Turn on delivery confirmations, if requested
        if confirm_delivery:
            self.logger.info('Confirming delivery for channel: {}'.format(self._channel))
            self._channel.confirm_delivery()

    def publish(self, topic, content):
        """
        Publish a message with a specified topic to the exchange

        Args:
            topic (str): The topic of the message, to be read by subscribers of that topic.
            content (str): The contents of the message to be sent

        Raises:
            TypeError: If 'content' is not a string
        """

        if not isinstance(content, str):
            raise TypeError("You must specify a message as a string.")

        # Format the message as a : separated string
        message = "{}:{}".format(topic, content)
        self.logger.info('Sending message :{}:{}'.format(topic, content))
        self._channel.basic_publish(
            exchange=self.exchange,
            routing_key=topic,
            body=message
        )

    def subscribe(self, topic='', acknowledge=True):
        """
        Subscribe to the messages of a particular topic

        Args:
            topic (basestring, optional): The name of the topic to subscribe to, defaults to '' (all messages).
            acknowledge (bool, optional): Whether to send an 'ack' message back to the
                producer upon message receipt, default is True.

        Returns:
            bool: True if successful

        Raises:
            TypeError: If 'topic' is not a basestring
        """

        if not isinstance(topic, basestring):
            raise TypeError("You must specify topic as a basestring")

        result = self._channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self._channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=topic)

        self.logger.info('Subscribing to topic: {}'.format(topic))
        self._channel.basic_consume(self.on_message, queue=queue_name, no_ack=not acknowledge)

        return True

    def unsubscribe(self, topic=''):
        """
        Unsubscribe to the messages of a particular topic

        Args:
            topic (basestring, optional): The name of the topic to subscribe to, defaults to '' (all messages).

        Returns:
            bool: True if successful

        Raises:
            TypeError: If 'topic' is not a basestring
        """

        if not isinstance(topic, basestring):
            raise TypeError("You must specify topic as a basestring")

        if self._channel:
            self.logger.info('Unsubscribing from topic: {}'.format(topic))
            self._channel.basic_cancel(self.on_cancelok, topic)

        return True

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

    def close(self):
        """
        Closes the Pika connection

        Returns:
            bool: True if successful
        """

        self.logger.info('Closing connection: {}'.format(self._connection))
        self._connection.close()
        return True

    ####################
    # Callback methods #
    ####################

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """
        Read the inbound message from the topic channel. Override this method for alternate implementations

        Returns:
            object: The Python object representing the message received
        """
        print "Handling message {}:{}".format(basic_deliver.routing_key, body)
        self.logger.info("Handling message {}:{}".format(basic_deliver.routing_key, body))
        self.acknowledge(basic_deliver.delivery_tag)