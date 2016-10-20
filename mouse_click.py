#!/bin/python

import pyautogui

from keyConstants import *
from tileRead import BoardDelimitationBox
from random import randrange, random
from time import sleep
from copy import copy

def generateSquareBox(boardcoord):
    #print(boardcoord)

    blocksize = [ (BoardDelimitationBox[x+2] -\
                   BoardDelimitationBox[x]) / 8 for x in range(2) ]

    squarespan = [ [boardcoord[x] * blocksize[x],
                    (boardcoord[x] + 1) * blocksize[x] ] for x in range(2) ]

    BOX = [ squarespan[k][v] +
           BoardDelimitationBox[k] for k,v in [(0,0), (1,0), (0,1), (1,1)] ]
    
    for k in range(len(BOX)):
        BOX[k] = round(BOX[k])

    # print(BOX)
    return BOX

def randomCoordInsideBox(BOX):
    # modified to ignore borders of the square!
    # this helps mantainging my heart beating rate stable xD;
    # also, fundamental to accuracy.
    # (referring to +boxSIZE//4 and -boxSIZE//4 on the randomization);
    boxSIZE = [BOX[x+2] - BOX[x] for x in range(2)]

        
    COORD = [ randrange(BOX[X]+ (boxSIZE[X]//3), BOX[X+2] - (boxSIZE[X]//3) ) for X in range(2) ]
              
    return COORD

def makeMoveOnScreen(moveCoord, offset):
    
    mouseClick(BoardDelimitationBox, offset)
    sleep(random()/2)
    # duplicate moveCoord array so it can be reused in case of failing to move piece on screen.
    moveCoord = copy(moveCoord)
    for x in range(2):
        moveCoord[x] = generateSquareBox(moveCoord[x])
        moveCoord[x] = randomCoordInsideBox(moveCoord[x])
        
        moveCoord[x][0] += offset[0]
        moveCoord[x][1] += offset[1]
    
    DragTime = random()/2 + 0.5
    pyautogui.moveTo(moveCoord[0][0], moveCoord[0][1])
    pyautogui.dragTo(moveCoord[1][0], moveCoord[1][1], DragTime, button='left')
    
def flickMouse(offset):
    NUM = randrange(3)
    for k in range(NUM):
        TARGET = randomCoordInsideBox(BoardDelimitationBox)
        pyautogui.moveTo(TARGET[0]+offset[0], TARGET[1]+offset[1], random() /2 )
        
def mouseClick(BOX, offset):
    coord = randomCoordInsideBox(BOX)
    pyautogui.click(x=coord[0]+offset[0],y=coord[1]+offset[1])
    
