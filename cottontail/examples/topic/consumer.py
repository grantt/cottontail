import sys
import cottontail


def run(topic):
    test_cli = cottontail.CottontailMessenger('test_topic', exchange_type=cottontail.EXCHANGE_TOPIC)

    test_cli.subscribe(topic)
    test_cli.listen()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        topic = sys.argv[1]
    else:
        topic = '#'

    run(topic)