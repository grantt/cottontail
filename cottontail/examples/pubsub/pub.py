import cottontail


def run():
    test_cli = cottontail.Publisher('pubsub_test')

    for n in xrange(100):
        test_cli.publish('', str(n))

if __name__ == '__main__':
    run()