"""customized Exceptions."""


class UrlNotSetException(Exception):
    def __init__(self):
        err = '::Url not set for requestor.'
        Exception.__init__(self, err)


class FailedToCollectException(Exception):
    def __init__(self):
        err = '::Failed to collect proxies.'
        Exception.__init__(self, err)


class UncompressedLayerException(Exception):
    def __init__(self):
        err = '::Sub layer uncompressed.'
        Exception.__init__(self, err)
