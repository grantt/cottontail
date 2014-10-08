import sys
import cottontail


class TestRPCClient(cottontail.RPCClient):
    def _compose_message(self, *fn_args, **fn_kwargs):
        return str(fn_args[0])


def run(num):
    test_cli = TestRPCClient()
    result = test_cli.call('rpc', num)
    print result,  '!!!!!'

if __name__ == '__main__':
    try:
        num = int(sys.argv[1])
    except Exception as e:
        raise e
    run(num)
