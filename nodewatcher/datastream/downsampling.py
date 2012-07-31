
class DownSampler(object):
  def __init__(self, id):
    self.id = id

class Min(DownSampler):
  def __init__(self):
    super(Min, self).__init__("min")

class Max(DownSampler):
  def __init__(self):
    super(Max, self).__init__("max")

class Avg(DownSampler):
  def __init__(self):
    super(Avg, self).__init__("avg")

BasicDownSampling = [Min, Max, Avg]
