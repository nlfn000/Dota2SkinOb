from prototypes.ComponentLayer import ComponentLayer


class Resolver(ComponentLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _service(self):
        while True:
            response = self.input.get()  # must be replaced
            html = response.text
            self.output.put(html)
