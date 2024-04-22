import click
from typing import Optional
from events import log, log_enqueue_state, log_ignore_state, log_visit_state
from maps import Location, Map
from parsing import validate_location, validate_map

from methods import *
from queue import PriorityQueue
from node import Node



def find_shortest_path(start: Location, goal: Location, 
                       terrain_map: Map, terrain_threshold: int) \
                   -> tuple[Optional[int],Optional[list[Location]]]:
    """Finds the path with lowest total cost (Task 1)
       Returns (cost,list(locations)) when a path is found.
       Returns (None,None) if no path is found."""

    # This is the entry point for your code for Task 1.
    # Please create additional functions and classes etc as needed 
    # to structure your implementation. 
    # Avoid implementing the entire algorithm in one long chunk.
    
    frontier = PriorityQueue()

    # Create the initial starting node.
    h = calculateManhattanDistance(start, goal)
    startNode = Node(location= start, h= h, moveCost= 0, g= 0, f= getFtotalCost(g=0, h=h), parent= None)

    # Used as a second priority in case elements share the same first priority.
    tieBreak = 0

    # Frontier initialized with start node. 
    # Frontier sorts by totalFCost(includes heuristic) as the priority, tieBreak as second priority
    frontier.put((startNode.f, tieBreak, startNode))
    log_enqueue_state(startNode.location, startNode.g)


    explored = set()



    while(frontier.qsize() > 0):

        # Retrieve a node from the frontier
        temp = frontier.get()
        # Strip out the priority queue sorting element
        currentLocation = temp[2]
        log_visit_state(currentLocation.location, currentLocation.g)

        # Goal test
        if currentLocation.location == goal:
            # A goal has been found

            finalList = []
            pathList = []

            # Work backwards from the goal node to retrieve the entire path that lead to the goal
            pathList = getParents(currentLocation, pathList)
            
            # Need to extract the locations from the nodes in the path to return a location list
            for item in pathList:
                finalList.append(item.location)

            # Reverse the list so that the expected order of visited locations is correct.
            finalList.reverse()

            return currentLocation.g, finalList
         
        
        explored.add(currentLocation)

    
        # Expand the node, find the neighbouring children. 
        child_nodes = getNeighbours(currentLocation, goal, terrain_map, terrain_threshold)

        # Process the children
        for child in child_nodes:

            # Boolean stops unwanted nodes from being placed
            placeable = True

            # Check the child has not already been explored. If not, it can be placed in the frontier.
            # If it has, and the incoming child has a lower f cost than the explored item, the explored item will be deleted. 
            # Otherwise it is a worse path and should be ignored
            if child in explored:
                placeable = False
                log_ignore_state(child.location, child.g)           


            # Check the child is not already in the frontier. If not, it can be placed in the frontier.
            for item in frontier.queue:

                # If it is, and the incoming child has a lower f cost than the frontier item, the frontier item will be deleted. 
                # Otherwise it is a worse path and should be ignored
                if child.location == item[2].location:
     
                    if child.f < item[2].f:
                        frontier.queue.remove(item)

                    else:
                        placeable = False
                        log_ignore_state(child.location, child.g)


            # The child is eligible to be placed in the frontier
            if placeable:
                tieBreak += 1
                frontier.put((child.f, tieBreak, child))
                log_enqueue_state(child.location, child.g)

    return None, None        


@click.command(no_args_is_help=True)
@click.argument('start', required=True, callback=validate_location)
@click.argument('goal', required=True, callback=validate_location)
@click.argument("terrain_map", required=True, type=click.Path(exists=True), callback=validate_map)
@click.argument("terrain_threshold", required=True, type=click.IntRange(min=0,max=1000))
def main(start: Location, goal: Location, terrain_map: Map, terrain_threshold: int) -> None:
    """Example usage:

    \b
    python pathfinding_task1.py 3,2 0,3 resources/terrain01.txt 50
    """
    path = find_shortest_path(start, goal, terrain_map, terrain_threshold)
    if path:
        log(f"The path is {path[1]} with cost {path[0]}.")
    else:
        log('No path found')

if __name__ == '__main__':
    main()
