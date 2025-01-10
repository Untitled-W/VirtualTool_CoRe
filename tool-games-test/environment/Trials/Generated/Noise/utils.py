import numpy as np
import pygame as pg
from pyGameWorld.viewer import *
from pyGameWorld.world import *
import copy

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

def add_noise_ball(file):
   
    Ball = file['world']['objects']['Ball']['position']
    ball_radius = np.random.randint(10, 25)
    delta = ball_radius - file['world']['objects']['Ball']['radius']
    Ball[1] += delta
    Ball[0] += delta
    
    file['world']['objects']['Ball']['radius'] = ball_radius
    file['world']['objects']['Ball']['position'] = Ball

    return file

def add_noise_catapult_vertical(file, offset):

    NoiseStrut = copy.deepcopy(file['world']['objects']['Strut'])
    NoiseCradle = copy.deepcopy(file['world']['objects']['Cradle'])
    NoiseCatapult = copy.deepcopy(file['world']['objects']['Catapult'])
    
    file['world']['objects']['NoiseStrut'] = NoiseStrut
    file['world']['objects']['NoiseCradle'] = NoiseCradle
    file['world']['objects']['NoiseCatapult'] = NoiseCatapult

    Strut = NoiseStrut['vertices']
    Cradle = NoiseCradle['vertices']
    Catapult = NoiseCatapult['polys']
    
    for i in range(4):
        Strut[i][1] += offset
        Cradle[i][1] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][1] += offset
            
    file['world']['objects']['NoiseStrut']['vertices'] = Strut
    file['world']['objects']['NoiseCradle']['vertices'] = Cradle
    file['world']['objects']['NoiseCatapult']['polys'] = Catapult
    
    return file

def add_noise_catapult_horizon(file, offset):

    NoiseStrut = file['world']['objects']['NoiseStrut']
    NoiseCradle = file['world']['objects']['NoiseCradle']
    NoiseCatapult = file['world']['objects']['NoiseCatapult']

    Strut = NoiseStrut['vertices']
    Cradle = NoiseCradle['vertices']
    Catapult = NoiseCatapult['polys']
    
    for i in range(4):
        Strut[i][0] += offset
        Cradle[i][0] += offset
    
    for i in range(3):
        for j in range(4):
            Catapult[i][j][0] += offset
            
    file['world']['objects']['NoiseStrut']['vertices'] = Strut
    file['world']['objects']['NoiseCradle']['vertices'] = Cradle
    file['world']['objects']['NoiseCatapult']['polys'] = Catapult
    
    return file

def check(data, img):
    world = loadFromDict(data['world'])
    s = drawWorld(world, backgroundOnly=False, lightenPlaced=False)
    pg.image.save(s, img)