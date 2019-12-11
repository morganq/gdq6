from vector import Vector

def dot(v1, v2):
    return v1.x * v2.x + v1.y * v2.y

def cross(v1, v2):
    return v1.x * v2.y - v1.y * v2.x

def intersect(pt, direction, line_segment_a, line_segment_b):
    p = pt
    r = direction
    q = line_segment_a
    s = (line_segment_b - line_segment_a).get_normalized()

    crs = cross(r,s)
    crqp = cross((q-p), r)
    if crs == 0:
        return None, 0, 0
    t = cross((q-p), s) / cross(r,s)
    u = cross((q-p), r) / cross(r,s)
    if u < 0:
        return None, 0, 0
    if u > (line_segment_b - line_segment_a).get_length():
        return None, 0, 0
    return p + r * t, t, u

def dist_sq_from_line(pt, line_a, line_b):
    l2 = (line_b - line_a).get_sq_length()
    if l2 == 0:
        return (line_a - pt).get_length()
    t = max(0, min(1, dot(pt - line_a, line_b - line_a) / l2))
    projection = line_a + (line_b - line_a) * t
    return (projection - pt).get_sq_length()

def project_pt_to_line_seg(pt, line_a, line_b):
    l2 = (line_b - line_a).get_sq_length()
    if l2 == 0:
        return (line_a - pt).get_length()
    t = max(0, min(1, dot(pt - line_a, line_b - line_a) / l2))
    return line_a + (line_b - line_a) * t