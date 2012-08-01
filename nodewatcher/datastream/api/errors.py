
class MetricNotFound(Exception):
  pass

class MultipleMetricsReturned(Exception):
  pass

class UnsupportedDownsampler(Exception):
  pass

class UnsupportedGranularity(Exception):
  pass

class ReservedTagNameError(Exception):
  pass
