import cottontail


def run():
    test_cli = cottontail.Subscriber('pubsub_test')

    test_cli.subscribe()
    test_cli.listen()

if __name__ == '__main__':
    run()