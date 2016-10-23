#!/bin/python
import sys
#BoardDelimitationBox = [ 111, 186, 916 ,990 ]
NewGameBox = [ 521 ,451 ,721 ,467 ]

BlackThreshold = 10


engineRunCommand = ["../e-vchess/engine/e-vchess", "-l", '-t', '-MD', '../e-vchess/machines']    

WindowNameKeyword = "Live Chess"

WhiteSquareColor = (240,217,181)

PathToPresentBoardScreenshot = 'screenshots/current_board.png'

PathToReferenceScreenshot = 'screenshots/reference_guest.png'\
                            if '--secondary' in sys.argv else\
                            'screenshots/reference.png'
