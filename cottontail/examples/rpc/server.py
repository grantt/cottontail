import cottontail


class TestRPCServer(cottontail.RPCServer):
    def _process_message(self, body):
        return [int(body)], {}

    def _execute_call(self, *args, **kwargs):
        return fib(args[0])


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


def run():
    test_cli = TestRPCServer()
    test_cli.subscribe('rpc')
    test_cli.listen()

if __name__ == '__main__':
    run()