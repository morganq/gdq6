import pyglet
from vector import Vector

class PolygonGroup(pyglet.graphics.Group):
    def __init__(self, obj, line_width):
        self.obj = obj
        self.line_width = line_width
        super().__init__()

    def set_state(self):
        pyglet.gl.glLineWidth(self.line_width)
        pyglet.gl.glPushMatrix()
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(self.obj.x + 0.5, self.obj.y + 0.5, 0)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

    def unset_state(self):
        pyglet.gl.glPopMatrix()
        pyglet.gl.glLineWidth(1)

class Polygon:
    def __init__(self, x, y, polygon, color, line_width, batch, draw_type=None):
        self.x = x
        self.y = y
        self.polygon = polygon
        self.scale = 1
        self._color = color
        self._line_width = line_width
        self._batch = batch
        self._group = PolygonGroup(self, self.line_width)
        self._vertex_list = None
        self._visible = True
        self._draw_type = draw_type or pyglet.gl.GL_LINES

        self._update_vertex_list(self.polygon)

    def _update_vertex_list(self, points):
        # Add a point at the beginning and end for line loop 
        if not self._visible:
            points = [Vector(0,0), Vector(0,0)]
        verts = []          
        num = len(points)
        for point in points:
            verts.extend([point.x, point.y])
        if not self._vertex_list:
            self._vertex_list = self._batch.add(
                num, self._draw_type, self._group,
                ("v2f", verts),
                ("c4B", self._color * num)
            )
        else:
            self._vertex_list.resize(num)
            self._vertex_list.vertices[:] = verts
            self._vertex_list.colors[:] = self.color * num

    def set_points(self, points):
        self.polygon = points
        self._update_vertex_list(self.polygon)

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        if value != self._line_width:
            self._group = PolygonGroup(self, value)
            self._batch.migrate(
                self._vertex_list,
                pyglet.gl.GL_LINES,
                self._group,
                self._batch)
        self._line_width = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._vertex_list.colors[:] = self.color * (len(self._vertex_list.colors) // 4)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        if value is True and self._visible is False:
            self._visible = value
            self._update_vertex_list(self.polygon)
        elif value is False and self._visible is True:
            self._visible = value
            self._update_vertex_list(self.polygon)
        

    def delete(self):
        self._vertex_list.delete()

class Circle(Polygon):
    def __init__(self, x, y, radius, color, line_width, batch, draw_type=None):
        self._radius = radius
        points = self.make_points()
        super().__init__(x, y, points, color, line_width, batch, draw_type=draw_type)

    def make_points(self):
        points = []
        segments = int(self._radius / 4) + 32
        last_pt = None
        for i in range(segments + 1):
            pt = Vector.from_circular(i * 6.2818 / segments, self._radius)
            if last_pt:
                points.append(last_pt)
                points.append(pt)
            last_pt = pt
        return points        

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if self._radius != value:
            self._radius = value
            self.set_points(self.make_points())

class SelectionCircle(Circle):
    def __init__(self, *args, **kwargs):
        self._angle = 0
        super().__init__(*args, **kwargs)

    def make_points(self):
        points = []
        segments = int(self._radius / 4) + 32
        last_pt = None
        for i in range(segments + 1):
            pt = Vector.from_circular(i * 5.5 / segments + self._angle, self._radius)
            if last_pt:
                points.append(last_pt)
                points.append(pt)
            last_pt = pt
        return points 

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if value != self._angle:
            self._angle = value
            self.set_points(self.make_points())        

class FilledCircle(Circle):
    def __init__(self, x, y, radius, color, line_width, batch):
        super().__init__(x, y, radius, color, line_width, batch, draw_type=pyglet.gl.GL_POLYGON)

    def make_points(self):
        points = []
        segments = int(self._radius / 4) + 32
        for i in range(segments + 1):
            pt = Vector.from_circular(i * 6.2818 / segments, self._radius)
            points.append(pt)
        return points

class Cross(Polygon):
    def __init__(self, x, y, size, color, line_width, batch):
        self._size = size
        self._angle = 0
        points = self.make_points()
        super().__init__(x, y, points, color, line_width, batch)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if value != self._angle:
            self._angle = value
            self.set_points(self.make_points())

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value != self._size:
            self._size = value
            self.set_points(self.make_points())            

    def make_points(self):
        v1 = Vector.from_circular(self._angle, self._size)
        v2 = -v1
        v3 = Vector.from_circular(self._angle + 3.14159 / 2, self._size)
        v4 = -v3
        return [v1, v2, v3, v4]