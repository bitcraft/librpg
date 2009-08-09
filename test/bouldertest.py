import sys
sys.path.append('..')

import librpg
import pygame

librpg.init()
librpg.config.graphics_config.config(tile_size=32, object_height=32, object_width=32)

from librpg.map import MapModel, Map
from librpg.mapobject import ScenarioMapObject, MapObject
from librpg.util import Position
from librpg.party import Character, CharacterReserve
from librpg.movement import Slide
from librpg.dialog import MessageDialog

class Boulder(ScenarioMapObject):

    def __init__(self, map):
    
        ScenarioMapObject.__init__(self, map, 0, 3)
        
    def activate(self, party_avatar, direction):
    
        self.schedule_movement(Slide(direction))


class Victory(ScenarioMapObject):

    def __init__(self, map):
    
        ScenarioMapObject.__init__(self, map, 0, 0)
        
    def collide_with_party(self, party_avatar, direction):
    
        self.map.pause(30)
        self.map.schedule_message(MessageDialog('Gratz! You won!'))


class BoulderMaze(MapModel):
    
    MAZE = [
    [1,1,1,1,3,3,1,1,1,1],
    [0,0,0,0,1,2,0,0,0,0],
    [0,1,1,2,2,1,1,2,1,0],
    [0,1,2,1,1,1,2,1,2,0],
    [0,2,1,1,1,2,1,1,2,0],
    [0,1,2,2,2,1,1,2,1,0],
    [0,2,2,1,1,1,2,2,1,0],
    [0,1,1,1,2,2,1,1,1,0],
    [0,0,0,0,1,1,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1]]

    def __init__(self):
    
        MapModel.__init__(self, 'bouldertest.map', ('lower_tileset32.png', 'lower_tileset32.bnd'), [('upper_tileset32.png', 'upper_tileset32.bnd')])
        
    def initialize(self, local_state):
    
        for y, line in enumerate(BoulderMaze.MAZE):
            for x, cell in enumerate(line):
                if cell == 2:
                    self.add_object(Boulder(self), Position(x, y))
                elif cell == 3:
                    self.add_object(Victory(self), Position(x, y))


a = librpg.party.Character('Andy', 'char_alex32.png')
r = librpg.party.CharacterReserve([a])

model = BoulderMaze()
model.add_party(r.create_party(3, [a]), Position(4, 9))
Map(model).gameloop()
exit()
