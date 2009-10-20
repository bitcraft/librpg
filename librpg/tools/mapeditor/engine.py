
import pygame
from pygame.locals import *

import settings as set

from map import *
from tile import *

class Engine(object):
    def __init__(self, startmap_xml):
        
        
    def run():
        pygame.init()
        screen = pygame.display.set_mode((set.resW,set.resH), set.displayFlags, set.resDepth)
        
        while True:
            
            if QUIT in [e.type for e in pygame.event.get()]:
                break
            
            m.draw(screen, 0, 0)
            pygame.display.flip()
