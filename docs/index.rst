.. cottontail documentation master file, created by
   sphinx-quickstart on Wed Oct  8 11:30:51 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction to Cottontail
==========================
Cottontail is a helpful wrapper around pika, the Python implementation of AMQP on RabbitMQ. Cottontail abstracts common messaging patterns into distinct server and client pair classes that can be used to implement direct messaging, work queues, pub/sub, routing, topics, and RPC.

Installing Cottontail
---------------------
Cottontail is freely available for download via PyPI `here <https://pypi.python.org/pypi/cottontail>`_ or may be installed using pip::

    pip install cottontail

To install from source, run "python setup.py install" in the root source directory.

Cottontail Usage
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   queue
   pubsub
   topic
   rpc
   examples

Author
------
`Grant Toeppen <https://github.com/grantt>`_

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

