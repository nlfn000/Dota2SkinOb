from trashbin.Layer import Layer


class Resolver(Layer):
    """
        input: key & response
        output: resolved data
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)

    def _service(self):
        while True:
            key, response = self.input.get()  # must be replaced
            self.output.put(response)
