import numpy as np
import pygame as pg
from pyGameWorld.viewer import *
from pyGameWorld.world import *

def drawWorld(world, backgroundOnly=False, lightenPlaced=False):
    s = pg.Surface(world.dims)
    s.fill(world.bk_col)

    def makept(p):
        return [int(i) for i in world._invert(p)]

    for b in world.blockers.values():
        drawpts = [makept(p) for p in b.vertices]
        pg.draw.polygon(s, b.color, drawpts)

    for o in world.objects.values():
        if not backgroundOnly or o.isStatic():
            if lightenPlaced and o.name == 'PLACED':
                _draw_obj(o, s, makept, .5)
            else:
                _draw_obj(o, s, makept)

    return s

def random_ball_size(file):
   
    ball_radius = np.random.randint(10, 25)
    file['world']['objects']['Ball']['radius'] = ball_radius

    return file

def vertical_move(file, offset):
    goal_points = file['world']['objects']['Goal']['points']
    LW1_vertices = file['world']['objects']['LeftWall1']['vertices']
    LW2_vertices = file['world']['objects']['LeftWall2']['vertices']
    RW1_vertices = file['world']['objects']['RightWall1']['vertices']
    RW2_vertices = file['world']['objects']['RightWall2']['vertices']
    bridgeL_vertices = file['world']['objects']['BridgeL']['vertices']
    bridgeR_vertices = file['world']['objects']['BridgeR']['vertices']
    obj1 = file['tools']['obj1']
    obj2 = file['tools']['obj2']
    
    goal_points[0][1] += offset
    goal_points[3][1] += offset
    LW1_vertices[1][1] += offset
    LW1_vertices[2][1] += offset
    LW2_vertices[0][1] += offset
    LW2_vertices[1][1] += offset
    LW2_vertices[2][1] += offset
    LW2_vertices[3][1] += offset
    RW1_vertices[1][1] += offset
    RW1_vertices[2][1] += offset
    RW2_vertices[0][1] += offset
    RW2_vertices[1][1] += offset
    RW2_vertices[2][1] += offset
    RW2_vertices[3][1] += offset
    bridgeL_vertices[0][1] += offset
    bridgeL_vertices[1][1] += offset
    bridgeL_vertices[2][1] += offset
    bridgeL_vertices[3][1] += offset
    bridgeR_vertices[0][1] += offset
    bridgeR_vertices[1][1] += offset
    bridgeR_vertices[2][1] += offset
    bridgeR_vertices[3][1] += offset
    
    for i in range(4):
        if i % 4 == 0 or i % 4 == 3:
            obj1[0][i][1] -= offset // 2
            obj2[0][i][1] -= offset // 2
        else:
            obj1[0][i][1] += offset // 2
            obj2[0][i][1] += offset // 2

    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['LeftWall1']['vertices'] = LW1_vertices
    file['world']['objects']['LeftWall2']['vertices'] = LW2_vertices
    file['world']['objects']['RightWall1']['vertices'] = RW1_vertices
    file['world']['objects']['RightWall2']['vertices'] = RW2_vertices
    file['world']['objects']['BridgeL']['vertices'] = bridgeL_vertices
    file['world']['objects']['BridgeR']['vertices'] = bridgeR_vertices
    file['tools']['obj1'] = obj1
    file['tools']['obj2'] = obj2

    return file

def horizon_move(file, offset):
    goal_points = file['world']['objects']['Goal']['points']
    LW1_vertices = file['world']['objects']['LeftWall1']['vertices']
    LW2_vertices = file['world']['objects']['LeftWall2']['vertices']
    RW1_vertices = file['world']['objects']['RightWall1']['vertices']
    RW2_vertices = file['world']['objects']['RightWall2']['vertices']
    bridgeL_vertices = file['world']['objects']['BridgeL']['vertices']
    bridgeR_vertices = file['world']['objects']['BridgeR']['vertices']
    
    goal_points[2][0] += offset
    goal_points[3][0] += offset
    for i in range(4):
        LW1_vertices[i][0] += offset
        LW2_vertices[i][0] += offset
        bridgeL_vertices[i][0] += offset
        bridgeR_vertices[i][0] += offset
    
    RW1_vertices[0][0] += offset
    RW1_vertices[1][0] += offset
    RW2_vertices[0][0] += offset
    RW2_vertices[1][0] += offset

    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['LeftWall1']['vertices'] = LW1_vertices
    file['world']['objects']['LeftWall2']['vertices'] = LW2_vertices
    file['world']['objects']['RightWall1']['vertices'] = RW1_vertices
    file['world']['objects']['RightWall2']['vertices'] = RW2_vertices
    file['world']['objects']['BridgeL']['vertices'] = bridgeL_vertices
    file['world']['objects']['BridgeR']['vertices'] = bridgeR_vertices

    return file

def flip(file):
    goal_points = file['world']['objects']['Goal']['points']
    LW1_vertices = file['world']['objects']['LeftWall1']['vertices']
    LW2_vertices = file['world']['objects']['LeftWall2']['vertices']
    RW1_vertices = file['world']['objects']['RightWall1']['vertices']
    RW2_vertices = file['world']['objects']['RightWall2']['vertices']
    bridgeL_vertices = file['world']['objects']['BridgeL']['vertices']
    bridgeR_vertices = file['world']['objects']['BridgeR']['vertices']
    ball_position = file['world']['objects']['Ball']['position']
    
    for i in range(4):
        goal_points[i][0] = 600 - goal_points[i][0]
        LW1_vertices[i][0] = 600 - LW1_vertices[i][0]
        LW2_vertices[i][0] = 600 - LW2_vertices[i][0]
        RW1_vertices[i][0] = 600 - RW1_vertices[i][0]
        RW2_vertices[i][0] = 600 - RW2_vertices[i][0]
        bridgeL_vertices[i][0] = 600 - bridgeL_vertices[i][0]
        bridgeR_vertices[i][0] = 600 - bridgeR_vertices[i][0]
    
    ball_position[0] = 600 - ball_position[0]
    
    for i in range(2):
        goal_points[i], goal_points[3-i] = goal_points[3-i], goal_points[i]
        LW1_vertices[i], LW1_vertices[3-i] = LW1_vertices[3-i], LW1_vertices[i]
        LW2_vertices[i], LW2_vertices[3-i] = LW2_vertices[3-i], LW2_vertices[i]
        RW1_vertices[i], RW1_vertices[3-i] = RW1_vertices[3-i], RW1_vertices[i]
        RW2_vertices[i], RW2_vertices[3-i] = RW2_vertices[3-i], RW2_vertices[i]
        bridgeL_vertices[i], bridgeL_vertices[3-i] = bridgeL_vertices[3-i], bridgeL_vertices[i]
        bridgeR_vertices[i], bridgeR_vertices[3-i] = bridgeR_vertices[3-i], bridgeR_vertices[i]


    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['LeftWall1']['vertices'] = LW1_vertices
    file['world']['objects']['LeftWall2']['vertices'] = LW2_vertices
    file['world']['objects']['RightWall1']['vertices'] = RW1_vertices
    file['world']['objects']['RightWall2']['vertices'] = RW2_vertices
    file['world']['objects']['BridgeL']['vertices'] = bridgeL_vertices
    file['world']['objects']['BridgeR']['vertices'] = bridgeR_vertices

    return file

def check(data, img):
    world = loadFromDict(data['world'])
    s = drawWorld(world, backgroundOnly=False, lightenPlaced=False)
    pg.image.save(s, img)