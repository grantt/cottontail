from client import CottontailExchange


def run():
    test_cli = CottontailExchange('test')

    for n in xrange(100):
        test_cli.publish('test_topic', str(n))

if __name__ == '__main__':
    run()