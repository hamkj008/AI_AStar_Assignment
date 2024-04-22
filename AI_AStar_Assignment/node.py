from maps import Location

class Node:

    def __init__(self, location: Location, moveCost, h, g, f, parent):
        
        self.location = location        
        self.moveCost = moveCost
        self.h = h
        self.g = g
        self.f = f
        self.parent = parent
       

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            if self.f < other.f:            
                return True
            else:
                del self


    def __hash__(self):
        return hash(self.location)
    




