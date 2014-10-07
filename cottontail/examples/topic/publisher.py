import cottontail


def run():
    test_cli = cottontail.CottontailMessenger('test_topic', exchange_type=cottontail.EXCHANGE_TOPIC)

    for n in xrange(100):
        if n % 2:
            topic = 'something.test'
        else:
            topic = 'something.other'
        test_cli.publish(topic, str(n))

if __name__ == '__main__':
    run()