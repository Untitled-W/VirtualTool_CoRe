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

def vertical_move(file, offset):
    goal_points = file['world']['objects']['Goal']['points']
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Ball = file['world']['objects']['Ball']['position']
    
    goal_points[0][1] += offset
    goal_points[3][1] += offset
    Strut[1][1] += offset
    Strut[2][1] += offset
    Cradle[1][1] += offset
    Cradle[2][1] += offset
    Ball[1] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][1] += offset


    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Ball']['position'] = Ball

    return file

def horizon_move(file, offset):
    goal_points = file['world']['objects']['Goal']['points']
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Ball = file['world']['objects']['Ball']['position']
    
    Ball[0] += offset
    goal_points[0][0] += offset
    goal_points[1][0] += offset
    for i in range(4):
        Strut[i][0] += offset
        Cradle[i][0] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][0] += offset
            
    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Ball']['position'] = Ball
    
    return file

def flip(file):
    goal_points = file['world']['objects']['Goal']['points']
    Strut = file['world']['objects']['Strut']['vertices']
    Cradle = file['world']['objects']['Cradle']['vertices']
    Catapult = file['world']['objects']['Catapult']['polys']
    Ball = file['world']['objects']['Ball']['position']
    
    for i in range(4):
        goal_points[i][0] = 600 - goal_points[i][0]
        Strut[i][0] = 600 - Strut[i][0]
        Cradle[i][0] = 600 - Cradle[i][0]
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][0] = 600 - Catapult[i][j][0]
    
    Ball[0] = 600 - Ball[0]
    
    for i in range(2):
        goal_points[i], goal_points[3-i] = goal_points[3-i], goal_points[i]
        Strut[i], Strut[3-i] = Strut[3-i], Strut[i]
        Cradle[i], Cradle[3-i] = Cradle[3-i], Cradle[i]
        
    for i in range(3):
        for j in range(2):
            Catapult[i][j], Catapult[i][3-j] = Catapult[i][3-j], Catapult[i][j]

    file['world']['objects']['Goal']['points'] = goal_points
    file['world']['objects']['Strut']['vertices'] = Strut
    file['world']['objects']['Cradle']['vertices'] = Cradle
    file['world']['objects']['Catapult']['polys'] = Catapult
    file['world']['objects']['Ball']['position'] = Ball
    
    return file

def check(data, img):
    world = loadFromDict(data['world'])
    s = drawWorld(world, backgroundOnly=False, lightenPlaced=False)
    pg.image.save(s, img)