from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Point2, Point3
from positions import Positions
import sys


class World(DirectObject):
    def __init__(self):
        window = ShowBase()
        self.config = {}
        execfile('config_test.py', self.config)
        self.depth = 55
        window.setBackgroundColor(115/255, 115/255, 115/255)
        pos = Positions().get_position(self.depth)
        b = 0
        for i, j in enumerate(pos):
            #b += 0.04  # covers all of the values
            b += 0.03
            print b
            #print i
            #print j
            square = window.loader.loadModel("models/plane")
            square.reparentTo(camera)
            square.setScale(1)
            square.setDepthTest(False)
            square.setTransparency(1)
            square.setTexture(window.loader.loadTexture("textures/calibration_square.png"), 1)
            # gray
            #square.setColor(150 / 255, 150 / 255, 150 / 255, 1.0)
            # yellow
            #square.setColor(175 / 255, 175 / 255, 130 / 255, 1.0)
            square.setColor(0.9, 0.9, b, 1.0)

            #square.setColor(175 / 255, 175 / 255, (i * 7) / 255, 1.0)
            print square.getColor()
            square.setPos(Point3(j))
            #print square.getPos()
        print 'done'

if __name__ == "__main__":
    print 'auto-running'
    W = World()
    run()
else:
    print 'not auto-running'