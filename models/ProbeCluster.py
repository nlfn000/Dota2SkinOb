from models.Probe import Probe
from prototypes.Layer import CompressedLayer


class ProbeCluster(CompressedLayer):
    """
        clustered multi-threading probes.
        structure:
           >> [Probe]*n >>
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None,
                 scale=10, probe_type=Probe):
        super().__init__(input_layer, input, output, message_collector)
        probes = [probe_type(input=self.input, output=self.output, message_collector=self.message, id=str(i))
                  for i in range(scale)]
        self.layers = probes
