import cottontail


def run():
    worker = cottontail.QueueWorker('queue')
    worker.subscribe('queue_test')
    worker.listen()


if __name__ == '__main__':
    run()