import queue

from trashbin.Layer import Layer


class Retryer(Layer):
    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)
        self.set(max_retry=5, hash_key='hash_name')
        self.output = self.input
        self.feedback = queue.Queue()
        self.retry_table = {}

    def _service(self):
        while True:
            task = self.feedback.get()
            _hash = task.get(self.indiv('hash_key'))
            self.log(1, f'-retry/{self.__class__.__name__}<{self.id}>:{_hash}')
            if _hash in self.retry_table.keys():
                self.retry_table[_hash] += 1
            else:
                self.retry_table[_hash] = 1
            if self.retry_table[_hash] > self.indiv('max_retry'):
                continue
            self.output.put(task)
