from vector import Vector

def dot(v1, v2):
    return v1.x * v2.x + v1.y * v2.y

def cross(v1, v2):
    return v1.x * v2.y - v1.y * v2.x

def intersect(pt, direction, line_segment_a, line_segment_b):
    norm = Vector(-direction.y, direction.x)
    d1 = dot(norm, line_segment_a - pt)
    d2 = dot(norm, line_segment_b - pt)
    if (d1 >= 0 and d2 >= 0) or (d1 < 0 and d2 < 0):
        return False, 0

    p = pt
    r = direction
    q = line_segment_a
    s = (line_segment_b - line_segment_a).get_normalized()

    t = cross((q-p), s) / cross(r,s)
    return p + r * t, t

def dist_sq_from_line(pt, line_a, line_b):
    l2 = (line_b - line_a).get_sq_length()
    if l2 == 0:
        return (line_a - pt).get_length()
    t = max(0, min(1, dot(pt - line_a, line_b - line_a) / l2))
    projection = line_a + (line_b - line_a) * t
    return (projection - pt).get_sq_length()
