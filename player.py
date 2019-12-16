import pyglet
from vector import Vector
from maphelp import *
import mapgen as mapgenmodule
import pyttsx3
import math
from polygon import Circle, Polygon, Cross, SelectionCircle
from pathfinding import StreetSolver

DRAW_COLOR = (0,171,182)
SHOW_COLOR = (80,191,202)
#SELECTION_COLOR_1 = (0,125,68,255)
#SELECTION_COLOR_2 = (71,202,0,255)
#SELECTION_COLOR_3 = (140, 201, 67, 255)
SELECTION_COLOR_1 = (0,125,68,255)
SELECTION_COLOR_2 = (20,20,20,255)
SELECTION_COLOR_3 = (60,60,60,255)


NEAR_DIST = 20

class PlayerControl:
    def __init__(self, game):
        self.game = game

        self.speaker = pyttsx3.init()
        self.speaker.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
        self.speaker.setProperty('volume', 0.25)
        self.speaker.startLoop(False)  
        self.speak_time = 4
        self.last_words = ""

        self.game.window.set_mouse_visible(True)

        self._mouse_press_start = Vector(0,0)
        self.mouse_map_pos = Vector(0,0)

        self.selected_car = None
        self.selection_ring = None

        self.drawing = False
        self.draw_edges = []
        self.draw_edge_final_pt = Vector(0,0)
        self.draw_nodes = []
        self.next_node = None
        self.last_node = None
        self.draw_edge_sprites = []
        self.draw_node_sprites = []
        self.draw_edge_polygon = None

        self.image_ring = pyglet.image.load('resources/ring49_teal.png')
        self.image_ring.anchor_x = self.image_ring.width // 2
        self.image_ring.anchor_y = self.image_ring.width // 2

        self.image_edge = pyglet.image.load('resources/box33_teal.png')
        self.image_edge.anchor_x = self.image_edge.width // 2
        self.image_edge.anchor_y = self.image_edge.height

        self.image_node = pyglet.image.load('resources/circle39_teal.png')
        self.image_node.anchor_x = self.image_node.width // 2
        self.image_node.anchor_y = self.image_node.height // 2

        self.image_target = pyglet.image.load('resources/x.png')
        self.image_target.anchor_x = self.image_target.width // 2
        self.image_target.anchor_y = self.image_target.height // 2              

        self.inspect_edge = None
        self.inspect_label = None
        self.time = 0

    def set_mapgen(self, mapgen):
        self.mapgen = mapgen

        self.selection_ring = SelectionCircle(
            0, 0, 20,
            SELECTION_COLOR_1, 3,
            self.game.batches['gui'],
        )
        self.selection_ring.visible = False
        self.selection_ring.angle = 0

        self.draw_edge_polygon = Polygon(
            0,0,[Vector(0,0), Vector(0,0)],SELECTION_COLOR_2, 8,self.game.batches['path']
        )

        self.target_sprites = []

        self.inspect_label = pyglet.text.Label(
            "", font_name="Menlo", font_size=14, anchor_x="left", anchor_y="bottom",
            batch=self.game.batches['gui'], color=mapgenmodule.BORDER_COLOR,
            x = self.game.level.mapgen.x - 6,
            y = self.game.level.mapgen.y + self.game.level.mapgen.height + 9
            )

    def say(self, words, time_adjust = 0):
        if not self.speaker.isBusy() and self.speak_time <= time_adjust:
            if self.last_words != words:
                self.last_words = words
                self.speaker.say(words)
                self.speak_time = 12.0

    def update_speaker(self, delta_time):
        self.speaker.iterate()
        self.speak_time -= delta_time
        if self.selected_car:
            turns = self.selected_car.get_turns()

            if not self.drawing and not self.speaker.isBusy() and self.speak_time <= 0 and self.selected_car.given_directions:
                if turns:
                    turn = None
                    blocks = 0
                    for t in turns:
                        if t[1] in self.selected_car.target_nodes:
                            s = "Your destination is ahead."
                            self.say(s)
                            turn = None
                            break
                        if t[0]:
                            turn = t
                            break
                        blocks += 1
                    if turn:
                        feet = int((turn[1].pt - self.selected_car.map_pos).get_length() / 10) * 100
                        # feet
                        direction = turn[0]
                        road_name = turn[2]
                        if feet > 500:
                            quarter_miles = int(feet / 1320)
                            if quarter_miles == 0:
                                distance_words = "%d feet" % feet
                            elif quarter_miles == 1:
                                distance_words = "a quarter of a mile"
                            elif quarter_miles == 2:
                                distance_words = "half a mile"
                            elif quarter_miles == 3:
                                distance_words = "three quarters of a mile" 
                            elif quarter_miles < 7:
                                distance_words = "one mile"
                            else:
                                distance_words = "%d miles" % (math.ceil(quarter_miles/4))
                            s = "In %s, take a %s onto %s" % (distance_words, direction, road_name)
                            self.say(s)
                        elif blocks == 0:
                            s = "Take the next %s onto %s" % (direction, road_name)
                            self.say(s)

    def update_cursor(self):
        if self.drawing:
            self.game.set_cursor('crosshair')
        else:
            for car in self.game.level.cars:
                dv = car.map_pos - self.mouse_map_pos
                if car != self.selected_car and dv.get_sq_length() <= car.radius ** 2:
                    car.hover = True
                    self.game.set_cursor('hand')
                else:
                    car.hover = False
                    self.game.set_cursor(None)

    def update(self, delta_time):
        self.time += delta_time

        self.update_cursor()
        
        self.update_speaker(delta_time)
        self.selection_ring.visible = self.selected_car is not None
        self.draw_edge_polygon.visible = self.selected_car is not None
        if not self.selected_car:
            for spr in self.draw_node_sprites:
                spr.visible = False
            for spr in self.target_sprites:
                spr.visible = False                
        if self.selected_car:
            self.selection_ring.visible = True
            self.selection_ring.x = self.selected_car.x
            self.selection_ring.y = self.selected_car.y
            self.selection_ring.angle += delta_time * 6.2818
            self.selection_ring.radius = math.sin(self.time * 2) * 1.5 + (self.selected_car.radius + 5)

            for i,target in enumerate(self.selected_car.target_nodes):
                if i >= len(self.target_sprites):
                    self.target_sprites.append(Cross(
                        0, 0, 15, SELECTION_COLOR_1, 7,
                        self.game.batches['guiback'],
                    ))
                    self.target_sprites[i].t = 0
                spr = self.target_sprites[i]
                spr.visible = True
                spr.x = target.pt.x + self.game.level.mapgen.x
                spr.y = target.pt.y + self.game.level.mapgen.y
                spr.t = min(spr.t + delta_time * 3,1)
                spr.size = math.sin(spr.t * 2) ** 2 * 30
                spr.angle = math.sin(spr.t * 2) ** 2 * 1.9 + 3.14159/4

            for i in range(len(self.selected_car.target_nodes), len(self.target_sprites)):
                self.target_sprites[i].visible = False

            mode = "draw"
            # Show car path even without directions
            if not self.drawing:
                self.draw_edge_final_pt = None
                mode = "show"
                self.draw_edges = [self.selected_car.current_edge] + self.selected_car.directions
                last_node = self.selected_car.last_node
                self.draw_nodes = []
                for edge in self.draw_edges[:-1]:
                    if edge.node1 == last_node:
                        self.draw_nodes.append(edge.node2)
                        last_node = edge.node2
                    else:
                        self.draw_nodes.append(edge.node1)
                        last_node = edge.node1

            draw_edge_points = []
            for i,edge in enumerate(self.draw_edges):
                pt1 = None
                pt2 = None
                if i == 0:
                    pt1 = Vector(self.selected_car.x, self.selected_car.y) - Vector(self.game.level.mapgen.x, self.game.level.mapgen.y)
                else:
                    prev_node = self.draw_nodes[i-1]
                    if edge.node1 == prev_node:
                        pt1 = edge.node1.pt
                    else:
                        pt1 = edge.node2.pt

                if i == len(self.draw_edges) - 1:
                    pt2 = self.draw_edge_final_pt
                    if self.draw_edge_final_pt is None:
                        if i > 0:
                            prev_node = self.draw_nodes[i-1]
                            if edge.node1 == prev_node:
                                pt1 = edge.node1.pt
                            else:
                                pt1 = edge.node2.pt
                        else:
                            # weird case I don't understand
                            pt1 = edge.node1.pt
                        pt2 = edge.node1.pt
                else:
                    if edge.node1 == self.draw_nodes[i]:
                        pt2 = edge.node1.pt
                    else:
                        pt2 = edge.node2.pt

                mapvect = Vector(self.game.level.mapgen.x, self.game.level.mapgen.y)
                draw_edge_points.append(pt1 + mapvect)
                draw_edge_points.append(pt2 + mapvect)

            self.draw_edge_polygon.line_width = (6, 8)[mode == 'draw']
            self.draw_edge_polygon.color = (SELECTION_COLOR_3, SELECTION_COLOR_2)[mode == "draw"]
            self.draw_edge_polygon.set_points(draw_edge_points)

            for i,node in enumerate(self.draw_nodes):
                if i >= len(self.draw_node_sprites):
                    self.draw_node_sprites.append(
                        Circle(
                            0, 0, 4, SELECTION_COLOR_2, 6,
                            batch=self.game.batches['path'],
                        )
                    )
                    self.draw_node_sprites[-1].t = 0
                
                spr = self.draw_node_sprites[i]
                spr.x = node.pt.x + self.game.level.mapgen.x
                spr.y = node.pt.y + self.game.level.mapgen.y
                #spr.radius = (2, 4)[mode == "draw"]
                spr.color = (SELECTION_COLOR_3, SELECTION_COLOR_2)[mode == "draw"]
                spr.target_scale = (3,4)[mode == "draw"]
                if not spr.visible:
                    spr.visible = True
                    spr.t = 0

            for i in range(len(self.draw_nodes)):
                spr = self.draw_node_sprites[i]
                spr.radius = -(math.sin(min(spr.t, 1)*2) * 0.5 + 0.55) * spr.target_scale
                spr.t += delta_time * 4

            for i in range(len(self.draw_nodes), len(self.draw_node_sprites)):
                self.draw_node_sprites[i].visible = False

            # Check to see if the car has moved past the first edge
            if len(self.draw_edges) > 1:
                if self.selected_car.current_edge != self.draw_edges[0]:
                    if self.selected_car.current_edge == self.draw_edges[1]:
                        self.draw_edges.pop(0)
                        self.draw_nodes.pop(0)
                    else:
                        self.draw_edges = []
                        self.draw_nodes = []
            if len(self.draw_edges) > 1:
                self.selected_car.directions = self.draw_edges[1:]

    def mousemove(self, x, y, dx, dy):
        gotit = False
        map_pt = Vector(x - self.game.level.mapgen.x,y - self.game.level.mapgen.y)
        self.mouse_map_pos = map_pt
        for edge in self.game.level.mapgen.edges:
            dsq = dist_sq_from_line(map_pt, edge.node1.pt, edge.node2.pt)
            if dsq < NEAR_DIST ** 2:
                gotit = True
                self.inspect_edge = edge
                self.inspect_label.visible = True
                self.inspect_label.text = self.inspect_edge.road.name

        for node in self.game.level.mapgen.nodes:
            dsq = (node.pt - map_pt).get_sq_length()
            if dsq < NEAR_DIST ** 2:
                gotit = True
                self.inspect_label.visible = True
                road_names = set()
                for edge in node.edges:
                    road_names.add(edge.road.name)
                self.inspect_label.text = " and ".join(list(road_names))

        if not gotit:
            self.inspect_label.text = ""


    def mouserelease(self, x, y, button, modifiers):
        if self.drawing:
            self.drawing = False
            for spr in self.draw_node_sprites:
                spr.visible = False
            for spr in self.draw_edge_sprites:
                spr.visible = False

    def mousepress(self, x, y, button, modifiers):
        self._mouse_press_start = Vector(x,y)
        if button == 1:        
            mouse_pos = Vector(x,y)
            # Only counts as a click if you didn't move mouse much
            if (mouse_pos - self._mouse_press_start).get_sq_length() < 5 * 5:
                hit = False
                for car in self.game.level.cars:
                    dv = Vector(car.x, car.y) - Vector(x,y)
                    if dv.get_sq_length() <= car.radius ** 2:
                        hit = True
                        self.select(car)
                        break
                if not hit:
                    self.deselect()                   
                    self.speaker.stop()

            if self.selected_car:
                edge = self.selected_car.current_edge
                map_pt = Vector(x - self.game.level.mapgen.x,y - self.game.level.mapgen.y)
                dsq = dist_sq_from_line(map_pt, edge.node1.pt, edge.node2.pt)
                if dsq <= NEAR_DIST ** 2:
                    self.drawing = True
                    if self.selected_car.given_directions:
                        self.say("Recalculating", time_adjust=2)
                    self.draw_edges = [edge]
                    self.draw_nodes = []
                    self.draw_edge_final_pt = project_pt_to_line_seg(map_pt, edge.node1.pt, edge.node2.pt)
                    self.next_node = edge.other_node(self.selected_car.last_node)
                    print(self.next_node)

    def nearest_edge(self, pt, edges):
        closest = (None, 99999999999)
        for edge in edges:
            dist = dist_sq_from_line(pt, edge.node1.pt, edge.node2.pt)
            if closest[0] is None or dist < closest[1]:
                closest = (edge, dist)
        return closest


    def deselect(self):
        self.selected_car = None
        self.draw_nodes = []
        self.draw_edges = []
        self.draw_edge_final_pt = None   
        
    def select(self, car):
        self.selected_car = car
        self.draw_nodes = []
        self.draw_edges = []
        self.draw_edge_final_pt = None        
        for spr in self.target_sprites:
            spr.t = 0        

    def mousedrag(self, x, y, dx, dy, buttons, modifiers):
        self.mousemove(x,y,dx,dy)
        if self.drawing:
            map_pt = Vector(x - self.game.level.mapgen.x,y - self.game.level.mapgen.y)
            edges_we_care_about = list(self.next_node.edges)
            if self.draw_nodes:
                edges_we_care_about.extend(self.draw_nodes[-1].edges)
            nearest_edge, dsq = self.nearest_edge(map_pt, edges_we_care_about)

            handled_edge = False
            
            # Check if we changed roads for the current edge
            if self.draw_nodes:
                if nearest_edge in self.draw_nodes[-1].edges and nearest_edge not in self.draw_edges:
                    alt_edge = nearest_edge
                    if dsq <= NEAR_DIST ** 2:
                        other_node = alt_edge.other_node(self.draw_nodes[-1])
                        if not other_node.blockers:                                
                            self.draw_edges[-1] = alt_edge
                            self.next_node = other_node
                            #self.game.sound.play("click")
                            handled_edge = True

            # Check if we've moved to the next edge
            if not handled_edge and nearest_edge in self.next_node.edges and nearest_edge not in self.draw_edges:
                next_edge = nearest_edge
                if dsq <= NEAR_DIST ** 2:
                    other_node = next_edge.other_node(self.next_node)
                    if not other_node.blockers:
                        self.draw_nodes.append(self.next_node)
                        self.draw_edges.append(next_edge)
                        self.next_node = other_node
                        self.game.sound.play("click")
                        handled_edge = True
                        self.selected_car.given_directions = True

            # Check if we backtracked by looking at the edge 2 ago
            if not handled_edge and len(self.draw_edges) >= 2:
                for i in range(1, len(self.draw_edges) - 2):
                    old_edge = self.draw_edges[i]
                    dsq  = dist_sq_from_line(map_pt, old_edge.node1.pt, old_edge.node2.pt)
                    if dsq < NEAR_DIST ** 2:
                        self.next_node = self.draw_nodes[i-1]
                        self.draw_edges = self.draw_edges[:i]
                        self.draw_nodes = self.draw_nodes[:i-1]
                        handled_edge = True
                        #self.game.sound.play("place")
                        break

            # Find distance along current edge
            if self.draw_edges:
                edge = self.draw_edges[-1]
                self.draw_edge_final_pt = project_pt_to_line_seg(map_pt, edge.node1.pt, edge.node2.pt)
            
            if self.draw_nodes:
                path_tail = self.draw_nodes[-1]
            else:
                path_tail = self.selected_car.next_node
            
            # Find the nearest node
            mouse_node, dsq = self.nearest_node(map_pt)

            # Check if we moved far and need to pathfind
            if mouse_node != path_tail and len(self.selected_car.directions) > 1:
                path = StreetSolver(self.mapgen).astar(path_tail, mouse_node)
                last_node = None
                for n in list(path):
                    if last_node is not None:
                        for edge in last_node.edges:
                            if edge.other_node(last_node) == n:
                                self.selected_car.directions.append(edge)
                    else:
                        if self.selected_car.directions[-1].next_node(self.selected_car.directions[-2]) == n:
                            last_node = n
                    
                    
                print("---")
            