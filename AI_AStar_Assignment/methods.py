from maps import Map, Location
from node import Node
from q2node import q2Node


# Heuristic function - Manhattan Distance
# This heuristic was chosen becasue it is both admissible and consistant.
# It is admissible because it will never overestimate the distance to the goal.
# This is important, because otherwise the heuristic may erroneously believe it is too far away,
# disregarding the optimal path.
# It is also consistent (monotonic) because h(x) <= h(y) + cost(x, y)
# For example, in terrain map 1, the manhattan distance from the start (3,2) to the goal is 4, h(x) = 4
# and the manhattan distance of a direct successor y (3, 3) is 3, h(y) = 3.
# The move cost from (3, 2) to (3, 3) is 20.
# Therefore: 4 <= 3 + 20    4 <= 23. 
# This ensures that the heuristic will decrease in value as the search gets closer to the goal.


# Returns the manhattan distance for a source location to a goal.
def calculateManhattanDistance(source: Location, goal: Location) -> int:
    return abs(source[0] - goal[0]) + abs(source[1] - goal[1])


# Returns the value of a location
def getLocationCost(source: Location, map: Map) -> int:
   return map[source[0], source[1]]


# Returns the cost to move from a source location to a target location
# which is both their values combined 
def getMoveCost(source: Location, target: Location, map: Map) -> int:
    beginCost = map[source[0], source[1]]
    endCost = map[target[0], target[1]]

    return beginCost + endCost


# The complete path cost of a location. It adds the total path cost (g), 
# which is the sum of all the move costs, to the heuristic cost (h), to produce f. 
# This value is the primary reason for selection in the priority queue.
def getFtotalCost(g, h):
    return h + g


# Accepts a node and backtracks through all the parents of the node,
# summing the move costs to produce the total path cost for the location.
def getGpathCost(node, g):

    while(node.moveCost != 0):    
         g += node.moveCost
         node = node.parent

    return g



# Accepts a node and a list and will backtrack through the all the parent nodes 
# appending them to the list. Returns the list with the parent nodes which constitutes the 
# total path to the node.
def getParents(node, parents):

    while(node.parent != None): 
        parents.append(node)
        node = node.parent

    parents.append(node)

    return parents



# For question 1, finds all the neighbours of a node in four directions if they are valid.
# Invalid neighbours will exceed the terrain threshold or exceed the boundaries of the map.
# Once valid locations have been determined, a node is created to store the location
# and the other required parameters for question 1.
# Returns a list of children nodes belonging to the source node.
def getNeighbours(sourceNode: Node, goal: Location, map: Map, threshold): 
    
    children: Node = []

    # Find the boundaries of the map
    rowSize = map.shape[0]
    colSize = map.shape[1]


    # Get Valid Neighbouring Locations
    locations = [
        getNewLocation(type= "north", source= sourceNode.location, maxSize= rowSize, map= map, threshold= threshold),
        getNewLocation(type= "south", source= sourceNode.location, maxSize= rowSize, map= map, threshold= threshold),
        getNewLocation(type= "east", source= sourceNode.location, maxSize= colSize, map= map, threshold= threshold),
        getNewLocation(type= "west", source= sourceNode.location, maxSize= colSize, map= map, threshold= threshold) ]

    # Add the data to the node
    for newLocation in locations:
        g = 0

        if newLocation != None:
            node = Node(location=None, moveCost=0, h=0, g=0, f=0, parent=None)
            node.location = newLocation
            node.h = calculateManhattanDistance(newLocation, goal)
            node.moveCost = getMoveCost(sourceNode.location, newLocation, map)
            node.parent = sourceNode
            node.g = getGpathCost(node, g)
            node.f = getFtotalCost(g= node.g, h= node.h)

            children.append(node)

    return children




# Accepts a source location and a direction and performs the validation required 
# to determine if there is a valid map location in that direction. 
# If the boundaries of the map are exceeded, or the terrain threshold is exceeded, the direction is not valid
# Used by getNeighbours to find valid children.
def getNewLocation(type, source: Location, maxSize, map: Map, threshold) -> Location:

    newLocation = None

    row = source[0]
    col = source[1]


    if type == "north":
    # Check if the target is valid within the map boundaries
        if (row - 1) >= 0:
            newLocation = row - 1, col           

    if type == "south":
    # Check if the target is valid within the map boundaries
        if (row + 1) < maxSize:
            newLocation = row + 1, col

    if type == "east":
    # Check if the target is valid within the map boundaries
        if (col + 1) < maxSize:
            newLocation = row, col + 1
    
    if type == "west":
    # Check if the target is valid within the map boundaries
        if (col - 1) >= 0:
            newLocation = row, col - 1

    # Check if the terrain difficulty is within the threshold
    if newLocation:
        if getLocationCost(newLocation, map) > threshold or getLocationCost(source, map) > threshold:
            newLocation = None

    return newLocation




# For question 2, will determine the probability of success for a path
# based on an enemy presence map, according to the given formula.
def getSuccessProbability(path, map):
    
    result = 1

    for node in path:
        enemyPresence = getLocationCost(node.location, map)

        prob = 1 - (enemyPresence / 100)
        result *= prob

    return result



# For question 2, finds all the neighbours of a node in four directions if they are valid.
# Invalid neighbours will exceed the terrain threshold or exceed the boundaries of the map.
# Once valid locations have been determined, a node is created to store the location,
# the other required parameters, and the additional parameters required for question 2.
# Returns a list of children nodes belonging to the source node.
def getQ2Neighbours(sourceNode: q2Node, goal: Location, map: Map, threshold, success_map: Map): 
    
    children: q2Node = []

    # Find the boundaries of the map
    rowSize = map.shape[0]
    colSize = map.shape[1]


    # Get Valid Neighbouring Locations
    locations = [
        getNewLocation(type= "north", source= sourceNode.location, maxSize= rowSize, map= map, threshold= threshold),
        getNewLocation(type= "south", source= sourceNode.location, maxSize= rowSize, map= map, threshold= threshold),
        getNewLocation(type= "east", source= sourceNode.location, maxSize= colSize, map= map, threshold= threshold),
        getNewLocation(type= "west", source= sourceNode.location, maxSize= colSize, map= map, threshold= threshold) ]


    # Add the data to the node
    for newLocation in locations:

        path = []
        if newLocation != None:

            node = q2Node(location=None, moveCost=0, h=0, g=0, f=0, parent=None, prob=0, tag="Keep")
            node.location = newLocation
            node.h = calculateManhattanDistance(newLocation, goal)
            node.moveCost = getMoveCost(sourceNode.location, newLocation, map)
            node.parent = sourceNode
            node.g = getGpathCost(node, node.g)
            node.f = getFtotalCost(g= node.g, h= node.h)
               
            path = getParents(node, path)
            node.prob = getSuccessProbability(path, success_map)

            children.append(node)            

    return children