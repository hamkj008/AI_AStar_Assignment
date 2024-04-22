from maps import Location

class q2Node:

    def __init__(self, location: Location, moveCost, h, g, f, prob, parent, tag):
        
        self.location = location        
        self.moveCost = moveCost
        self.h = h
        self.g = g
        self.f = f
        self.prob = prob
        self.parent = parent
        self.tag = tag


    def __eq__(self, other) -> bool:
        if isinstance(other, q2Node):
            if self.f <= other.f and self.prob >= other.prob:
                return True
            elif self.f > other.f and self.prob <= other.prob:
                del self


    def __hash__(self):
        return hash(self.location)

