class SegmentData:
    slope: double
    length: double
    regime: string
    time: double

    def __init__(self, slope, length, regime, time):
        self.slope = slope
        self.length = length
        self.regime = regime
        self.time = time
