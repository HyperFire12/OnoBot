class OSRSItem:
  def __init__(self, name, id):
    self.name = name
    self.id = id

  def changePrice(self, low, high):
    self.low = low
    self.high = high
    self.margin = int((self.high*.99)-self.low)