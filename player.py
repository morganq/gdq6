import pyglet
from vector import Vector
from maphelp import *

test_colors = {
    0:(255,0,0),
    1:(255,128,0),
    2:(255,255,0),
    3:(0,255,0),
    4:(0,0,255),
    5:(255,0,255),
}

DRAW_COLOR = (0,171,182)
SHOW_COLOR = (80,191,202)

NEAR_DIST = 7

class PlayerControl:
    def __init__(self, game):
        self.game = game
        #image = pyglet.image.load('resources/cursor.png')
        #cursor = pyglet.window.ImageMouseCursor(image, 0, 0)
        #self.game.window.set_mouse_cursor(cursor)
        #self.game.window.set_exclusive_mouse(True)
        self.game.window.set_mouse_visible(True)

        self._mouse_press_start = Vector(0,0)

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

        self.image_ring = pyglet.image.load('resources/ring48.png')
        self.image_ring.anchor_x = self.image_ring.width // 2
        self.image_ring.anchor_y = self.image_ring.height // 2

        self.image_edge = pyglet.image.load('resources/box32.png')
        self.image_edge.anchor_x = self.image_edge.width // 2
        self.image_edge.anchor_y = self.image_edge.height

        self.image_node = pyglet.image.load('resources/circle32.png')
        self.image_node.anchor_x = self.image_node.width // 2
        self.image_node.anchor_y = self.image_node.height // 2      

        self.next_node_sprite = None

    def set_mapgen(self, mapgen):
        self.mapgen = mapgen

        self.selection_ring = pyglet.sprite.Sprite(
            self.image_ring, x=0.5, y=0.5,
            batch=self.game.batches['gui'],
            subpixel=True
        )
        self.selection_ring.color = (68,210,210)
        self.selection_ring.scale = 0.75
        self.selection_ring.visible = False

        self.next_node_sprite = pyglet.sprite.Sprite(
            self.image_node,
            batch = self.game.batches['gui'],
            subpixel = True
        )
        self.next_node_sprite.color = (255,255,255)


    def update(self, delta_time):

        self.selection_ring.visible = self.selected_car is not None
        if self.selected_car:
            self.selection_ring.visible = True
            self.selection_ring.x = self.selected_car.x
            self.selection_ring.y = self.selected_car.y

            if self.next_node:
                self.next_node_sprite.x = self.next_node.pt.x + self.game.level.mapgen.x
                self.next_node_sprite.y = self.next_node.pt.y + self.game.level.mapgen.y
                self.next_node_sprite.visible = False
            else:
                self.next_node_sprite.visible = False

            mode = "draw"
            # Show car path even without directions
            if not self.drawing and self.selected_car.directions:
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


            for i,edge in enumerate(self.draw_edges):
                if i >= len(self.draw_edge_sprites):
                    self.draw_edge_sprites.append(
                        pyglet.sprite.Sprite(
                            self.image_edge,
                            batch=self.game.batches['gui'],
                            subpixel=True
                        )
                    )
                
                spr = self.draw_edge_sprites[i]
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
                        prev_node = self.draw_nodes[i-1]
                        if edge.node1 == prev_node:
                            pt1 = edge.node1.pt
                        else:
                            pt1 = edge.node2.pt                        
                        pt2 = edge.node1.pt
                else:
                    if edge.node1 == self.draw_nodes[i]:
                        pt2 = edge.node1.pt
                    else:
                        pt2 = edge.node2.pt

                spr.x = pt1.x + self.game.level.mapgen.x
                spr.y = pt1.y + self.game.level.mapgen.y
                angle, length = (pt2 - pt1).get_circular()
                spr.scale_y = length / 32
                spr.rotation = (angle - 3.14159/2) * 180 / 3.14159
                spr.scale_x = (0.2, 0.4)[mode == "draw"]
                spr.color = (SHOW_COLOR, DRAW_COLOR)[mode == "draw"]
                spr.visible = True

            for i in range(len(self.draw_edges), len(self.draw_edge_sprites)):
                self.draw_edge_sprites[i].visible = False

            for i,node in enumerate(self.draw_nodes):
                if i >= len(self.draw_node_sprites):
                    self.draw_node_sprites.append(
                        pyglet.sprite.Sprite(
                            self.image_node,
                            batch=self.game.batches['gui'],
                            subpixel=True
                        )
                    )
                
                spr = self.draw_node_sprites[i]
                spr.x = node.pt.x + self.game.level.mapgen.x
                spr.y = node.pt.y + self.game.level.mapgen.y
                spr.color = (SHOW_COLOR, DRAW_COLOR)[mode == "draw"]
                spr.scale = (0.3, 0.5)[mode == "draw"]
                spr.visible = True

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
        print("RECEIVING EVENTS", x, y)

    def mouserelease(self, x, y, button, modifiers):
        # Selecting a car
        if button == 1:
            mouse_pos = Vector(x,y)
            # Only counts as a click if you didn't move mouse much
            if (mouse_pos - self._mouse_press_start).get_sq_length() < 5 * 5:
                hit = False
                for car in self.game.level.cars:
                    dv = Vector(car.x, car.y) - Vector(x,y)
                    if dv.get_sq_length() <= car.radius ** 2:
                        hit = True
                        self.selected_car = car
                        self.draw_nodes = []
                        self.draw_edges = []
                        self.draw_edge_final_pt = None
                        break
                if not hit:
                    self.selected_car = None
            self.drawing = False
            for spr in self.draw_node_sprites:
                spr.visible = False
            for spr in self.draw_edge_sprites:
                spr.visible = False


    def mousepress(self, x, y, button, modifiers):
        self._mouse_press_start = Vector(x,y)
        if self.selected_car:
            edge = self.selected_car.current_edge
            map_pt = Vector(x - self.game.level.mapgen.x,y - self.game.level.mapgen.y)
            dsq = dist_sq_from_line(map_pt, edge.node1.pt, edge.node2.pt)
            if dsq <= NEAR_DIST ** 2:
                self.drawing = True
                self.draw_edges = [edge]
                self.draw_nodes = []
                self.draw_edge_final_pt = project_pt_to_line_seg(map_pt, edge.node1.pt, edge.node2.pt)
                if edge.node1 == self.selected_car.last_node:
                    self.next_node = edge.node2
                else:
                    self.next_node = edge.node1

    def mousedrag(self, x, y, dx, dy, buttons, modifiers):
        if self.drawing:
            map_pt = Vector(x - self.game.level.mapgen.x,y - self.game.level.mapgen.y)
            # Check if we changed roads for the current edge
            if self.draw_nodes:
                for alt_edge in self.draw_nodes[-1].edges:
                    if alt_edge not in self.draw_edges:
                        dsq  = dist_sq_from_line(map_pt, alt_edge.node1.pt, alt_edge.node2.pt)
                        if dsq <= NEAR_DIST ** 2:
                            self.draw_edges[-1] = alt_edge
                            if alt_edge.node1 == self.draw_nodes[-1]:
                                self.next_node = alt_edge.node2
                            elif alt_edge.node2 == self.draw_nodes[-1]:
                                self.next_node = alt_edge.node1
                            else:
                                print("BROKEN ALT EDGE")
                            break
            # Check if we've moved to the next edge
            for next_edge in self.next_node.edges:
                if next_edge not in self.draw_edges:
                    dsq  = dist_sq_from_line(map_pt, next_edge.node1.pt, next_edge.node2.pt)
                    if dsq <= NEAR_DIST ** 2:
                        self.draw_nodes.append(self.next_node)
                        self.draw_edges.append(next_edge)
                        if next_edge.node1 == self.next_node:
                            self.next_node = next_edge.node2
                        elif next_edge.node2 == self.next_node:
                            self.next_node = next_edge.node1
                        else:
                            print("BROKEN NEW EDGE")
                        break

            # Check if we backtracked by looking at the edge 2 ago
            if len(self.draw_edges) >= 2:
                for i in range(1, len(self.draw_edges) - 2):
                    old_edge = self.draw_edges[i]
                    dsq  = dist_sq_from_line(map_pt, old_edge.node1.pt, old_edge.node2.pt)
                    if dsq <= NEAR_DIST ** 2:
                        self.next_node = self.draw_nodes[i-1]
                        self.draw_edges = self.draw_edges[:i]
                        self.draw_nodes = self.draw_nodes[:i-1]
                        
                        break

            # Find distance along current edge
            if self.draw_edges:
                edge = self.draw_edges[-1]
                self.draw_edge_final_pt = project_pt_to_line_seg(map_pt, edge.node1.pt, edge.node2.pt)
