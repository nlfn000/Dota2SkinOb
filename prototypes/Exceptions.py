"""customized Exceptions."""


class UrlNotSetException(Exception):
    def __init__(self):
        err = '::Url not set for requestor.'
        Exception.__init__(self, err)


class IllegalJsonException(Exception):
    def __init__(self):
        err = '::failed to load json line.'
        Exception.__init__(self, err)


class FeedbackNotSetException(Exception):
    def __init__(self):
        err = '::Feedback not set for retrial.'
        Exception.__init__(self, err)


class FailedToCollectException(Exception):
    def __init__(self):
        err = '::Failed to collect proxies.'
        Exception.__init__(self, err)


class UncompressedLayerException(Exception):
    def __init__(self):
        err = '::Sub layer uncompressed.'
        Exception.__init__(self, err)
