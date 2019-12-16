import astar

class StreetSolver(astar.AStar):
    def __init__(self, mapgen):
        self.mapgen = mapgen

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        return (n2.pt - n1.pt).get_length()

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return (n2.pt - n1.pt).get_length()

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        n = []
        for edge in node.edges:
            other = edge.other_node(node)
            if not other.blockers:
                n.append(other)
        return n
