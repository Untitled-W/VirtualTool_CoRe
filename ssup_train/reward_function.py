import numpy as np

def point_segment_distance(p, seg_start, seg_end):
    x0, y0 = p
    x1, y1 = seg_start
    x2, y2 = seg_end
    AB = np.array([x2 - x1, y2 - y1])
    AP = np.array([x0 - x1, y0 - y1])
    BP = np.array([x0 - x2, y0 - y2])
    AB_len_sq = np.dot(AB, AB)
    if AB_len_sq == 0:
        return np.linalg.norm(AP)
    t = np.dot(AP, AB) / AB_len_sq
    if t < 0:
        return np.linalg.norm(AP)
    elif t > 1:
        return np.linalg.norm(BP)
    else:
        projection = AB * t + np.array([x1, y1])
        return np.linalg.norm(np.array([x0, y0]) - projection)

def cross_product(A, B, P):
    x1, y1 = A
    x2, y2 = B
    xp, yp = P
    return (x2 - x1) * (yp - y1) - (y2 - y1) * (xp - x1)

def is_point_in_polygon(polygon, P):
    n = len(polygon)
    cross_signs = []
    for i in range(n):
        A = polygon[i]
        B = polygon[(i + 1) % n]
        cross = cross_product(A, B, P)
        if cross > 0:
            cross_signs.append(1)
        elif cross < 0:
            cross_signs.append(-1)
        else:
            cross_signs.append(0)
    if all(c == cross_signs[0] for c in cross_signs if c != 0):
        return True
    return False

def is_ball_intersects_polygon(vertices, ball_center, ball_radius):
    if is_point_in_polygon(vertices, ball_center):
        return 0
    edges = [(vertices[i], vertices[(i + 1) % 4]) for i in range(4)]
    min_distance = float('inf')
    for edge in edges:
        p1, p2 = edge
        dist = point_segment_distance(ball_center, p1, p2)
        if dist <= ball_radius:
            return 0
        min_distance = min(min_distance, dist)
    return min_distance - ball_radius

def reward_func(path, goal, ball_radius):
    path = np.array(path, dtype=np.float32)
    distances = np.zeros(path.shape[0], dtype=np.float32)
    for i in range(path.shape[0]):
        distances[i] = is_ball_intersects_polygon(goal, path[i], ball_radius)
    reward_value = 1 - distances.min() / distances[0]
    return reward_value