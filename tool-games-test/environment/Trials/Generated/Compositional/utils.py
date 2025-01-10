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
   
    Ball = file['world']['objects']['Ball']['position']
    ball_radius = np.random.randint(10, 25)
    delta = ball_radius - file['world']['objects']['Ball']['radius']
    Ball[1] += delta
    Ball[0] += delta
    
    file['world']['objects']['Ball']['radius'] = ball_radius
    file['world']['objects']['Ball']['position'] = Ball

    return file

def bridge_vertical_move(file, offset):
    goal_points = file['world']['objects']['Goal']['points']
    LW1_vertices = file['world']['objects']['LeftWall1']['vertices']
    LW2_vertices = file['world']['objects']['LeftWall2']['vertices']
    RW1_vertices = file['world']['objects']['RightWall1']['vertices']
    RW2_vertices = file['world']['objects']['RightWall2']['vertices']
    bridgeL_vertices = file['world']['objects']['BridgeL']['vertices']
    bridgeR_vertices = file['world']['objects']['BridgeR']['vertices']
    obj4 = file['tools']['obj4']
    obj5 = file['tools']['obj5']
    
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
            obj4[0][i][1] -= offset // 2
            obj5[0][i][1] -= offset // 2
        else:
            obj4[0][i][1] += offset // 2
            obj5[0][i][1] += offset // 2

    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['LeftWall1']['vertices'] = LW1_vertices
    file['world']['objects']['LeftWall2']['vertices'] = LW2_vertices
    file['world']['objects']['RightWall1']['vertices'] = RW1_vertices
    file['world']['objects']['RightWall2']['vertices'] = RW2_vertices
    file['world']['objects']['BridgeL']['vertices'] = bridgeL_vertices
    file['world']['objects']['BridgeR']['vertices'] = bridgeR_vertices
    file['tools']['obj4'] = obj4
    file['tools']['obj5'] = obj5

    return file

def bridge_horizon_move(file, offset):
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
        RW1_vertices[i][0] += offset
        LW2_vertices[i][0] += offset
        bridgeL_vertices[i][0] += offset
        bridgeR_vertices[i][0] += offset
    
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

def catapult_vertical_move(file, offset):
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Ball = file['world']['objects']['Ball']['position']
    
    Strut[1][1] += offset
    Strut[2][1] += offset
    Cradle[1][1] += offset
    Cradle[2][1] += offset
    Ball[1] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][1] += offset

    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Ball']['position'] = Ball

    return file

def catapult_horizon_move(file, offset):
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Ball = file['world']['objects']['Ball']['position']
    
    Ball[0] += offset
    for i in range(4):
        Strut[i][0] += offset
        Cradle[i][0] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][0] += offset
            
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Ball']['position'] = Ball
    
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
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    
    for i in range(4):
        Strut[i][0] = 600 - Strut[i][0]
        Cradle[i][0] = 600 - Cradle[i][0]
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][0] = 600 - Catapult[i][j][0]
    
    for i in range(2):
        Strut[i], Strut[3-i] = Strut[3-i], Strut[i]
        Cradle[i], Cradle[3-i] = Cradle[3-i], Cradle[i]
        
    for i in range(3):
        for j in range(2):
            Catapult[i][j], Catapult[i][3-j] = Catapult[i][3-j], Catapult[i][j]

    
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
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult

    return file

def check(data, img):
    world = loadFromDict(data['world'])
    s = drawWorld(world, backgroundOnly=False, lightenPlaced=False)
    # pg.image.save(s, img)