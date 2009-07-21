import librpg
import pygame

librpg.init()
librpg.graphics_config.config(tile_size=32, object_height=32, object_width=32)

from librpg.map import MapModel, Map
from librpg.mapobject import ScenarioMapObject
from librpg.util import Position
from librpg.party import Character, CharacterReserve
from librpg.movement import Slide

class Boulder(ScenarioMapObject):

    def __init__(self, map):
    
        ScenarioMapObject.__init__(self, map, 3)
        
    def activate(self, party_avatar, direction):
    
        self.schedule_movement(Slide(direction))


class BoulderMaze(MapModel):
    
    MAZE = [
    [1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,1,2,0,0,0,0],
    [0,1,1,2,2,2,1,2,1,0],
    [0,1,2,1,1,1,2,1,2,0],
    [0,2,1,1,1,2,1,1,2,0],
    [0,1,2,2,2,1,1,2,1,0],
    [0,2,2,1,1,1,2,2,1,0],
    [0,1,1,1,2,2,1,1,1,0],
    [0,0,0,0,1,1,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1]]

    def __init__(self):
    
        MapModel.__init__(self, 'bouldertest.map', ('lower_tileset32.png', 'lower_tileset32.bnd'), ('upper_tileset32.png', 'upper_tileset32.bnd'))
        
    def initialize(self, local_state):
        for line, y in zip(BoulderMaze.MAZE, xrange(len(BoulderMaze.MAZE))):
            for cell, x in zip(line, xrange(len(line))):
                if cell == 2:
                    self.add_object(Boulder(self), Position(x, y))

a = librpg.party.Character('Andy', 'char_alex32.png')
r = librpg.party.CharacterReserve([a])

model = BoulderMaze()
model.add_party(r.create_party(3, [a]), Position(4, 9))
Map(model).gameloop()
exit()