from client import CottontailExchange


def run():
    test_cli = CottontailExchange('test')

    test_cli.subscribe('test_topic')
    test_cli.listen()

if __name__ == '__main__':
    run()