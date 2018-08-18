from models.Probe import Probe
from prototypes.Layer import CompressedLayer


class ProbeCluster(CompressedLayer):
    """
        clustered multi-threading probes.
        structure:
           >> [Probe]*n >>
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None,
                 scale=10, probe_type=Probe, proxy_pool=None):
        super().__init__(input_layer=input_layer, input=input, output=output, message_collector=message_collector)
        probes = [probe_type(input=self.input, output=self.output, proxy_pool=proxy_pool,
                             message_collector=message_collector, id=str(i)) for i in range(scale)]
        self.layers = probes
