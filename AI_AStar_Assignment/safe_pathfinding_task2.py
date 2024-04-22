import click
from typing import Optional
from events import log, log_enqueue_state, log_ignore_state, log_visit_state
from maps import Location, Map
from parsing import validate_location, validate_map

from methods import *
from queue import PriorityQueue
from q2node import q2Node



def find_shortest_safe_path(start: Location, goal: Location, 
                            terrain_map: Map, terrain_threshold: int,
                            success_map: Map, success_threshold: float) \
                            -> tuple[Optional[int],Optional[float],Optional[list[Location]]]:
    """Finds the path with lowest total cost that also satisfies 
       the minimum success probability threshold (Task 2).
       Returns (cost,prob_success,list(locations)) when a path is found.
       Returns (None,None,None) if no path is found."""

    # This is the entry point for your code for Task 2.
    # Please create additional functions and classes etc as needed 
    # to structure your implementation. 
    # Avoid implementing the entire algorithm in one long chunk.


    frontier = PriorityQueue()

    # Create the initial starting node to be added to the frontier
    h = calculateManhattanDistance(start, goal)
    startNode = q2Node(location= start, h= h, moveCost= 0, g= 0, f= getFtotalCost(g=0, h=h), prob=1, parent= None, tag= "Keep")

    # Frontier sorts by totalFCost(includes heuristic) as the priority, success probability as second priority, and location as third priority.
    frontier.put((startNode.f, (1 - startNode.prob), startNode.location, startNode))
    log_enqueue_state(startNode.location, startNode.g, startNode.prob)
    
    explored = set()

    pathList = []



    # Start the search
    while(frontier.qsize() > 0):

        # Retrieve a node from the frontier
        temp = frontier.get()

        # Strip out the priority queue sorting elements
        currentNode = temp[3]

        # Keep tag means that only valid nodes are processed
        if currentNode.tag == "Keep":

            # Goal test
            if currentNode.location == goal:

                # Goal has been found
                finalList = []
                pathList = []

                # Work backwards from the goal node to retrieve the entire path that lead to the goal
                pathList = getParents(currentNode, pathList)

                # Need to extract the locations from the nodes in the path to return a location list
                for node in pathList:
                    finalList.append(node.location)

                # Reverse the list so that the expected order of visited locations is correct.
                finalList.reverse()

                return currentNode.g, currentNode.prob, finalList



            # Expand the node and add it to the explored list                         
            explored.add(currentNode)
            log_visit_state(currentNode.location, currentNode.g, currentNode.prob)
    
            # Get the neighbouring children
            child_nodes = getQ2Neighbours(currentNode, goal, terrain_map, terrain_threshold, success_map)



            # Process the children
            for child in child_nodes:
  
                placeable = True        

                # If an item in the explored list shares the same location as the child,
                # the equality check in the q2Node class will filter the explored list accordingly.
                if child in explored:
                    placeable = False

                for f in frontier.queue:
                    if child.location == f[3].location:

                        # If the child has a higher f cost and the same or lower probability of success
                        # then it is a more treacherous path and should be ignored.
                        if child.f >= f[3].f and child.prob <= f[3].prob:
                            placeable = False
                            log_ignore_state(child.location, child.g, child.prob)
                            break
                    
                        # The incoming child has a superior path with lower f cost and higher or equal chance of success.
                        # The frontier queue item can't be directly deleted so a remove tag means that it is ignored.
                        elif child.f < f[3].f and child.prob >= f[3].prob:
                            f[3].tag = "REMOVE"                                                        

                if placeable:
                    # The child can only be placed in the frontier if it satisfies the success threshold.
                    if child.prob >= success_threshold:
                        frontier.put((child.f, (1 - child.prob), child.location, child))
                        log_enqueue_state(child.location, child.g, child.prob)
    
    return None, None, None


@click.command(no_args_is_help=True)
@click.argument('start', required=True, callback=validate_location)
@click.argument('goal', required=True, callback=validate_location)
@click.argument("terrain_map", required=True, type=click.Path(exists=True), callback=validate_map)
@click.argument("terrain_threshold", required=True, type=click.IntRange(min=0,max=1000))
@click.argument("success_map", required=True, type=click.Path(exists=True), callback=validate_map)
@click.argument("success_threshold", required=True, type=click.FloatRange(min=0.0,max=1.0))
def main(start: Location, goal: Location, 
         terrain_map: Map, success_map: Map, 
         terrain_threshold: int, success_threshold: float) -> None:
    """Example usage:

        \b
        python safe_pathfinding_task2.py 3,2 0,3 resources/terrain01.txt 50 resources/enemy01.txt 1.0
    """
    path = find_shortest_safe_path(start, goal, terrain_map, terrain_threshold, success_map, success_threshold)
    if path:
        log(f"The path is {path[2]} with cost {path[0]} and success probability {path[1]}")
    else:
        log('No path found')

if __name__ == '__main__':
    main()
