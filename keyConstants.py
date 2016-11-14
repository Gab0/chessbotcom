#!/bin/python
import sys
#BoardDelimitationBox = [ 111, 186, 916 ,990 ]
NewGameBox = [ 520 ,449 ,723 ,456 ]

BlackThreshold = 10


engineRunCommand = ["../e-vchess/engine/e-vchess",
                    "-l", '-MD', "../e-vchess/machines/top_machines",
                    "--showinfo"]


WindowNameKeyword = "Live Chess"

WhiteSquareColor = (240,217,181)

PathToPresentBoardScreenshot = 'screenshots/current_board.png'

PathToReferenceScreenshot = 'screenshots/reference_guest.png'\
                            if '--secondary' in sys.argv else\
                            'screenshots/reference.png'
