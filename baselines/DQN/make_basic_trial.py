from pyGameWorld import PGWorld, ToolPicker
from pyGameWorld.viewer import demonstrateTPPlacement, drawWorld, drawTool
import json
import pygame as pg
import cv2
import os

# Make the basic world
pgw = PGWorld(dimensions=(600,600), gravity=200)
# Name, [left, bottom, right, top], color, density (0 is static)
pgw.addBox('Table', [0,0,300,200],(0,0,0),0)
# Name, points (counter-clockwise), width, color, density
pgw.addContainer('Goal', [[330,100],[330,5],[375,5],[375,100]], 10, (0,255,0), (0,0,0), 0)
# Name, position of center, radius, color, (density is 1 by default)
pgw.addBall('Ball',[100,215],15,(0,0,255))

# Sets up the condition that "Ball" must go into "Goal" and stay there for 2 seconds
pgw.attachSpecificInGoal("Goal","Ball",2.)
'''
world_img = pg.surfarray.array3d(drawWorld(pgw))
world_img = cv2.resize(world_img, (90, 90))
print(world_img.dtype)
cv2.imshow('window', world_img.transpose(1, 0, 2))
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
pgw_dict = pgw.toDict()

'''
# Save to a file
# Can reload with loadFromDict function in pyGameWorld

with open('basic_trial.json','w') as jfl:
    json.dump(pgw_dict, jfl)
'''

tools = {
    "obj1" : [[[-30,-15],[-30,15],[30,15],[0,-15]]],
    "obj2" : [[[-20,0],[0,20],[20,0],[0,-20]]],
    "obj3" : [[[-40,-5],[-40,5],[40,5],[40,-5]]]
    }

'''
for tool in tools.values():
    tool_img = drawTool(tool)
    tool_img = cv2.resize(tool_img, (30, 30))
    print(tool_img.dtype)
    cv2.imshow('window', tool_img.transpose(1, 0, 2))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
'''

# Turn this into a toolpicker game
# Takes in the "toDict" translation of a world and tool dictionary
tp = ToolPicker(
    {'world': pgw_dict,
     'tools': tools}
)

'''
# Save to a file
# Can reload with loadToolPicker in pyGameWorld

with open('basic_tp.json','w') as tpfl:
    json.dump({'world':pgw_dict, 'tools':tools}, tpfl)
'''

# Find the path of objects over 2s
# Comes out as a dict with the moveable object names
# (PLACED for the placed tool) with a list of positions over time each
path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1",position=(200,400),maxtime=20.)
print("Action was successful? ", success)

import numpy as np
def reward_function(path_dict, goal_verts):
    ball_path = path_dict['Ball']
    placed_path = path_dict['PLACED']
    ball_path = np.array(ball_path)
    placed_path = np.array(placed_path)
    #print(ball_path.shape, placed_path.shape)
    distance = np.zeros((ball_path.shape[0], 4), dtype=np.float32)
    x_min = goal_verts[0][0]
    x_max = goal_verts[0][0]
    y_min = goal_verts[0][1]
    y_max = goal_verts[0][1]
    for i in range(4):
        x_min = x_min if x_min < goal_verts[i][0] else goal_verts[i][0]
        x_max = x_max if x_max > goal_verts[i][0] else goal_verts[i][0]
        y_min = y_min if y_min < goal_verts[i][1] else goal_verts[i][1]
        y_max = y_max if y_max > goal_verts[i][1] else goal_verts[i][1]
        distance[:, i] = np.sqrt((ball_path[:, 0] - goal_verts[i][0]) ** 2 + (ball_path[:, 1] - goal_verts[i][1]) ** 2)
    distance = np.min(distance, axis=1)
    mask = np.logical_and(np.logical_and(ball_path[:, 0] > x_min, ball_path[:, 0] < x_max), np.logical_and(ball_path[:, 1] > y_min, ball_path[:, 1] < y_max))
    distance[mask] *= -1
    #distance = np.sqrt((ball_path[:, 0] - placed_path[:, 0]) ** 2 + (ball_path[:, 1] - placed_path[:, 1]) ** 2)
    #print(distance)
    orig_distance = distance[0]
    reward = 1 - np.min(distance) / orig_distance
    return reward
'''
# View that placement
for i in range(20):
    for j in range(20):
        path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1", position=(600 // 20 * i + 600 // 20 // 2, 600 // 20 * j + 600 // 20 // 2), maxtime=20.)
        print(success)
        if success is not None:
            print(reward_function(path_dict))
            demonstrateTPPlacement(tp, 'obj1', (600 // 20 * i + 600 // 20 // 2, 600 // 20 * j + 600 // 20 // 2))
'''
# Load level in from json file
# For levels used in experiment, check out Level_Definitions/
json_dir = "./Trials/Original/"
tnm = "Basic"

with open(json_dir+tnm+'.json','r') as f:
    btr = json.load(f)

goal_verts = btr['world']['objects']['Goal']['points']

tp = ToolPicker(btr)

for i in range(20):
    for j in range(20):
        path_dict, success, time_to_success = tp.observePlacementPath(toolname="obj1", position=(600 // 20 * i + 600 // 20 // 2, 600 // 20 * j + 600 // 20 // 2), maxtime=20.)
        print(success)
        if success is not None:
            print(reward_function(path_dict, goal_verts))
            demonstrateTPPlacement(tp, 'obj1', (600 // 20 * i + 600 // 20 // 2, 600 // 20 * j + 600 // 20 // 2))


# View that placement
demonstrateTPPlacement(tp, 'obj1', (200, 400))