import cottontail


def run():
    test_cli = cottontail.CottontailMessenger('test')

    for n in xrange(100):
        if n % 2:
            topic = 'test'
        else:
            topic = 'other'
        test_cli.publish(topic, str(n))

if __name__ == '__main__':
    run()