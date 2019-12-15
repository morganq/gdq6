import gameobj
from vector import Vector
import pyglet
import random
from maphelp import *
from collections import defaultdict
import math
import csv
from polygon import PolygonGroup

ROAD_COLORS = {
    'highway':(76,76,186,255),
    'main':(53,139,161,255),
    'basic':(106,111,142,255),
}
#ROAD_COLORS = {
#    'highway':(170,0,181,255),
#    'main':(129,73,255,255),
#    'basic':(106,111,142,255),
#}
ROAD_WIDTHS = {
    'highway':5.25,
    'main':3.25,
    'basic':1.75
}
BORDER_COLOR = (40,40,40, 255)

MAIN_STREET_NAMES = [
    'Main Street', 'Broadway Avenue', '1st Street', 'School Street', '2nd Street',
    'View Street', 'Park Avenue', 'Oak Street', 'Cedar Street', 'Maple Street', 'Washington Street',
    'Hill Street', 'Lake Street', 'Pine Street', 'Jackson Street', 'Airport Way', 'Spruce Street',
    'Sunset Avenue', 'West Street', 'Delaware Street', 'Bay Street', 'Church Street', 'Lakeview Avenue',
    'Hickory Street', 'Lincoln Street', 'Walnut Street', 'River Street'
]

class MapNode:
    def __init__(self, pt):
        self.pt = pt
        self.edges = set()
        self.blockers = []

class MapEdge:
    def __init__(self, node1, node2, road):
        self.node1 = node1
        self.node2 = node2
        self.road = road

    def other_node(self, node):
        if node == self.node1:
            return self.node2
        elif node == self.node2:
            return self.node1
        raise Exception("node supplied to other_node is not in this edge")

    def __repr__(self):
        return "Edge %s (%s) -> (%s)" % (self.road.kind, self.node1.pt, self.node2.pt)

class Road:
    def __init__(self, name, a, b, direction, kind):
        self.name = name
        self.a = a
        self.b = b
        self.direction = direction
        self.kind = kind
        self.edges = []

class Map(gameobj.GameObject):
    def __init__(self, game, batch, width, height, x=0, y=0):
        self.batch = batch
        self.width = width
        self.height = height
        self.nodes = set()
        self.non_border_nodes = set()
        self.edges = []
        self.base_x = x
        self.base_y = y

        self.borders = []
        self.lines = []
        self.roads = []

        self.street_names = []
        self.gen_street_names()

        self.groups = {}
        self._vertex_lists = {}
        self._steps = [
            self.gen_border,
            self.gen_highway,
        ]
        for i in range(random.randint(3,7)):
            self._steps.append(self.gen_main_road)

        for i in range(200):
            self._steps.append(self.gen_basic_road)

        self._step_timer = 0.25

        while self._steps:
            self._take_step()      

        for edge in self.edges:
            dd = (edge.node1.pt - edge.node2.pt).get_normalized()
            self.lines.append((edge.node1.pt, edge.node2.pt, ROAD_COLORS[edge.road.kind], ROAD_WIDTHS[edge.road.kind]))
            self.nodes.add(edge.node1)
            self.nodes.add(edge.node2)
            edge.node1.edges.add(edge)
            edge.node2.edges.add(edge)

        #for node in self.nodes:
            #self._draw_square(node.pt, (0,0,128,255))

        self._update_vertex_list()              
        
        nodes = set()
        for edge in self.edges:
            nodes.add(edge.node1)
            nodes.add(edge.node2)
        self.nodes = list(nodes)
        for node in self.nodes:
            if len(node.edges) > 1:
                self.non_border_nodes.add(node)
        self.non_border_nodes = list(self.non_border_nodes)

        self.shake_time = 0

        super().__init__(game, x, y)

    def shake(self):
        self.shake_time = 0.25

    def gen_street_names(self):
        with open("resources/streetnames.csv") as f:
            r = csv.reader(f)
            for row in r:
                name = row[0]
                if name.startswith("0"):
                    name = name[1:]
                if name.startswith("UNNAMED"):
                    continue
                name = name.replace(" LN", " LANE")
                name = name.replace(" AVE", " AVENUE")
                name = name.replace(" PLZ", " PLAZA")
                name = name.replace(" PL", " PLACE")
                name = name.replace(" ALY", " ALLEY")
                name = name.replace(" TER", " TERRACE")
                name = name.title()
                self.street_names.append(name)
        self.main_street_names = list(MAIN_STREET_NAMES)

    def fetch_road_name(self, kind):
        if kind == 'basic':
            i = random.randint(0, len(self.street_names)-1)
            return self.street_names.pop(i)
        elif kind == 'main':
            i = random.randint(0, len(self.main_street_names)-1)
            return self.main_street_names.pop(i)

    def _take_step(self):
        step = self._steps.pop(0)
        step()
        self.lines = []
        thick = 2
        dist = 6
        self.lines.append((Vector(0,0), Vector(self.width,0), BORDER_COLOR, thick))
        self.lines.append((Vector(-dist,-dist), Vector(self.width+dist,-dist), BORDER_COLOR, thick))
        self.lines.append((Vector(self.width,0), Vector(self.width,self.height), BORDER_COLOR, thick))
        self.lines.append((Vector(self.width+dist,-dist), Vector(self.width+dist,self.height+dist), BORDER_COLOR, thick))        
        self.lines.append((Vector(self.width,self.height), Vector(0,self.height), BORDER_COLOR, thick))
        self.lines.append((Vector(self.width+dist,self.height+dist), Vector(-dist,self.height+dist), BORDER_COLOR, thick))
        self.lines.append((Vector(0,self.height), Vector(0,0), BORDER_COLOR, thick))
        self.lines.append((Vector(-dist,self.height+dist), Vector(-dist,-dist), BORDER_COLOR, thick))


    def _draw_square(self, pt, color):
        SIZE = .5
        self.lines.append((pt + Vector(-SIZE, -SIZE), pt + Vector(SIZE, -SIZE), color,1))
        self.lines.append((pt + Vector(SIZE, -SIZE), pt + Vector(SIZE, SIZE), color,1))
        self.lines.append((pt + Vector(SIZE, SIZE), pt + Vector(-SIZE, SIZE), color,1))
        self.lines.append((pt + Vector(-SIZE, SIZE), pt + Vector(-SIZE, -SIZE), color,1))

    def _update_vertex_list(self):
        line_lists = defaultdict(list)
        for a,b,c,lw in self.lines:
            line_lists[lw].append((a,b,c))
        line_lists_tuples = list(line_lists.items())
        line_lists_tuples.sort(key = lambda x:x[0], reverse=False)
        for width,line_list in line_lists_tuples:
            verts = []
            colors = []            
            num = len(line_list) * 2
            for a,b,color in line_list:
                verts.extend([a.x,a.y,b.x,b.y])
                colors.extend(color)
                colors.extend(color)

            if width not in self._vertex_lists:
                self._vertex_lists[width] = self.batch.add(
                    num,
                    pyglet.gl.GL_LINES,
                    PolygonGroup(self, width),
                    ('v2f', tuple(verts)),
                    ('c4B', colors)
                )
            else:
                self._vertex_lists[width].resize(num)
                self._vertex_lists[width].vertices[:] = verts
                self._vertex_lists[width].colors[:] = colors

    def update(self, delta_time):
        self._step_timer -= delta_time
        if self._step_timer <= 0 and self._steps:
            self._step_timer += 0
            self._take_step()
        if self.shake_time > 0:
            self.shake_time -= delta_time
            self.x = self.base_x + random.randint(-3,3)
            self.y = self.base_y + random.randint(-3,3)
        else:
            self.x = self.base_x
            self.y = self.base_y


    def gen_border(self):
        self.borders=[
            (Vector(0,0), Vector(self.width, 0)),
            (Vector(self.width,0), Vector(self.width, self.height)),
            (Vector(self.width,self.height), Vector(0, self.height)),
            (Vector(0,self.height), Vector(0, 0))
        ]

    def gen_highway(self):
        central_point = Vector(
            random.random() * self.width / 2 + self.width / 4,
            random.random() * self.height / 2 + self.height / 4,
        )
        direction = Vector.from_circular(random.random() * 3.1415, 1)
        linepts = [None, None]
        for border in self.borders:
            p, t, u = intersect(central_point, direction, border[0], border[1])
            if p:
                if t <= 0:
                    linepts[0] = p
                else:
                    linepts[1] = p
        road_name = "%s %d" % (random.choice(['Highway', 'Route']), random.randint(1,999))
        road = Road(road_name, linepts[0], linepts[1], direction, "highway")
        self.roads.append(road)

        nd1 = MapNode(linepts[0])
        nd2 = MapNode(linepts[1])
        edge = MapEdge(nd1, nd2, road)
        road.edges = [edge]
        self.edges.append(edge)

    def gen_main_road(self):
        TOO_CLOSE = 100
        for i in range(5):
            d = 0
            attempts = 0
            point = None
            while d < TOO_CLOSE ** 2 and attempts < 100:
                point = Vector(
                    random.random() * self.width,
                    random.random() * self.height
                )
                mains = filter(lambda x:x.kind in ["main", "highway"], self.roads)
                for main in mains:
                    d = dist_sq_from_line(point, main.a, main.b)

                attempts += 1

            direction = Vector.from_circular(random.random() * 3.1415, 1)
            success = self.try_add_road(point, direction, "main")
            if success:
                return

    def gen_basic_road(self):
        TOO_CLOSE = 1
        closest_road_direction = None
        d = 0
        attempts = 0
        point = None
        while d < TOO_CLOSE ** 2 and attempts < 100:
            d = 999999999
            point = Vector(
                random.random() * self.width,
                random.random() * self.height
            )
            mains = filter(lambda x:x.kind == "main", self.roads)
            for main in mains:
                cd = dist_sq_from_line(point, main.a, main.b)
                if cd < d:
                    d = cd
                    closest_road_direction = main.direction

            attempts += 1

        if random.random() > 0.9:
            closest_road_direction = Vector.from_circular(random.random()*3.14159, 1)
        elif random.random() > 0.5:
            closest_road_direction = Vector(-closest_road_direction.y, closest_road_direction.x)
        success = self.try_add_road(point, closest_road_direction, "basic")
        if success:
            return      

    def try_add_road(self, point, direction, kind):
        MIN_DIST = 20
        intersecting_roads = []
        intersectable = [(e.node1.pt, e.node2.pt, e) for e in self.edges]
        intersectable.extend([(a,b,None) for i,(a,b) in enumerate(self.borders)])
        for a,b,edge in intersectable:
            p, t, u = intersect(point, direction, a,b)
            if p:
                intersecting_roads.append((p,t,edge,u))

        pos_pt = None
        neg_pt = None

        roads_pos = sorted(filter(lambda x:x[1]>=0, intersecting_roads), key=lambda x:x[1])
        roads_neg = sorted(filter(lambda x:x[1] <0, intersecting_roads), key=lambda x:-x[1])

        finished_intersections = set()

        if kind == "basic":
            if random.random() > 0.66:
                roads_pos = roads_pos[0:1]
            if random.random() > 0.66:
                roads_neg = roads_neg[0:1]

        for p, t, edge, u in roads_pos:
            closest = 999999999
            for road in self.roads:
                if edge and road == edge.road:
                    continue                
                dist = dist_sq_from_line(p, road.a, road.b)                
                closest = min(closest, dist)

            if closest > MIN_DIST ** 2:
                finished_intersections.add((t,p,edge, u))
                pos_pt = p
                if neg_pt is None:
                    neg_pt = p
            else:
                break

        for p, t, edge, u in roads_neg:
            closest = 999999999
            for road in self.roads:
                if edge and road == edge.road:
                    continue                
                dist = dist_sq_from_line(p, road.a, road.b)
                closest = min(closest, dist)

            if closest > MIN_DIST ** 2:
                finished_intersections.add((t,p,edge,u))
                neg_pt = p
                if pos_pt is None:
                    pos_pt = p
            else:
                break                    

        if pos_pt and neg_pt and pos_pt != neg_pt:
            c = {
                'main': (255,128,128,255),
                'basic': (128,128,128,255),
            }
            road = Road(self.fetch_road_name(kind), neg_pt, pos_pt, direction, kind)
            self.roads.append(road)

            prev = None
            for t,pt,other_edge,u in sorted(finished_intersections, key=lambda x:x[0]):
                cur_node = MapNode(pt)
                if prev:
                    n1 = prev
                    n2 = cur_node
                    dd = (pt - prev.pt).get_normalized()
                    e = MapEdge(n1, n2, road)
                    road.edges.append(e)
                    self.edges.append(e)

                if other_edge is not None:
                    self.edges.remove(other_edge)
                    other_e1 = MapEdge(other_edge.node1, cur_node, other_edge.road)
                    other_e2 = MapEdge(cur_node, other_edge.node2, other_edge.road)
                    self.edges.extend([other_e1, other_e2])
                    other_edge.road.edges.remove(other_edge)
                    other_edge.road.edges.extend([other_e1, other_e2])
                prev = cur_node

            return True
        else:
            return False