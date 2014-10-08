import cottontail


def run():
    server = cottontail.QueueServer('queue')

    server.declare_queue('queue_test')

    for n in xrange(100):
        if n % 2:
            topic = 'test'
        else:
            topic = 'other'
        server.publish(topic, str(n))

if __name__ == '__main__':

    run()