#!/bin/python
import chess
from time import sleep
import os
import sys

if '--help' in sys.argv:
    print('''

chessbotcom v0.2;

        arguments:
               --test //load a dummy screenshot instead of processing realtime screen.
               --full //run e-vchess engine in longer thinking mode, using xDEEP.
               --help //this
               --watch //save square images from each evaluation of the board.
               --nomove //skip mouse movements.
               --autonew //automatically starts new games, endless play.

''')
    exit()
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from tileRead import *
from mouse_click import makeMoveOnScreen, flickMouse, mouseClick
from enginewrapper import Engine
from keyConstants import *

AllPieces = [ ['P','R','N','B','Q','K'],
              ['p','r','n','b','q','k'] ]


print(sys.argv[0])

requiredDirectories = ['screenshots', 'SquareImages']
for DIR in requiredDirectories:
    if not os.path.isdir(DIR):
        os.mkdir(DIR)
     
referenceInitialBoard = chess.Board()
BrowserAbsolutePosition = grabBrowserAbsolutePosition()
#print("path %s" % os.path.realpath(__file__))
#print("Board Position on Screen: %s" % BoardDelimitationBox)
      
G = fullScreenToBoard(PathToReferenceScreenshot)
GeneralBoardValue = EvaluateColoredBoard(G)

MovingModeEnabled = False if '--nomove' in sys.argv else True
KeepSquareImages = True if '--watch' in sys.argv else False
TestMode = True if '--test' in sys.argv else False
AutoNewGameMode = True if '--autonew' in sys.argv else False

def Game():
    global PLAY
    PLAY = 0
    PieceValueMap = setupTileReadingValues(BoardDelimitationBox)
    Board = chess.Board()
    WaitingEngineMove = False
    print("initial setup done.")
    #chess.set_piece_at(56, chess.Piece.from_symbol('Q'))
    if not TestMode:
        takeScreenshot()
    if '--full' in sys.argv:
        engineRunCommand += ['--xdeep', '1']
    engineRunCommand = EnginePath
    RunningEngine = Engine(engineRunCommand)
    sleep(1)
  
    initial = ReadScreen(PieceValueMap)
    
    ComputerSide = 0 if initial[0] == 'r' else 1


    print("Computer playing as %i" % ComputerSide)



    RunningEngine.send('new')
    if not ComputerSide:
        RunningEngine.send('white')
        RunningEngine.send('go')
        WaitingEngineMove = True
    game = True
    while game: 
        PreliminaryBoard = fullScreenToBoard(PathToPresentBoardScreenshot)
        PreliminaryBoardValue = EvaluateColoredBoard(PreliminaryBoard)
        
        if not TestMode:
            BoardValidity = abs(PreliminaryBoardValue-GeneralBoardValue)
            print("Board validity = %i    fail @38" % BoardValidity)
            if BoardValidity > 38:
                print("Invalid board!", end=" ")
                if AutoNewGameMode:
                    print("Testing for new game.", end= " ")
                    if tryNewGame(Board,PieceValueMap, ComputerSide):
                        print("New game detected! Rebooting...")
                        PLAY = 1
                        return
                    else:
                        print("No new game.")

        MOVES = detectScreenBoardMovement(Board, PieceValueMap, ComputerSide)
   
        if MOVES:
            print("&" * 12)
            # moves saved as 'screen coordinates'
            print(MOVES)
            
            if len(MOVES) > 2: # bail and don't process if screenshot proves to be invalid.
                               #maybe website is waiting response for new game? check.
                               #try to start new game, and reboot.
                print("Bizarre board conformation!")


            castlingExclusion = {'h8f8': 'e8g8', 'a8c8': 'e8b8', 'a8d8': 'e8c8',
                                 'h1f1': 'e1g1', 'a1c1': 'e1b1', 'a1d1': 'e1c1'}
            for M in range(len(MOVES)):
                    
                From = MOVES[M][1]
                #From = screenCoordinateToVirtualBoard(M[0], ComputerSide)
                From = virtualAbsoluteCoordinateToXY(From)
                #print(From)
                From = coordLabelToCoord(From)
                
                To = MOVES[M][2]
                #To = screenCoordinateToVirtualBoard(To, ComputerSide)
                To = virtualAbsoluteCoordinateToXY(To)
                To = coordLabelToCoord(To)
                
                MOVES[M].append(From+To)

            for M in MOVES:
                if M[0] in AllPieces[1-ComputerSide]:
                    #filter castling:
                    if M[3] in castlingExclusion.keys():
                        if castlingExclusion[M[3]] in [ m[3] for m in MOVES]:
                            continue
                        
                    print("Move detected: %s" % ('   '.join([str(x) for x in M])))

                    if chess.Move.from_uci(M[3]) in list(Board.generate_legal_moves()):
                        Board.push(chess.Move.from_uci(M[3]))
                        RunningEngine.send(M[3])
                        WaitingEngineMove = True
                    else:
                        print("ILLEGAL MOVE! %s" % M[3])
                        print("Ignoring...")
                        if tryNewGame(Board, PieceValueMap, ComputerSide):
                            PLAY = 1
                            return
                        continue
        else:
            print("|" * 12)

        while WaitingEngineMove:
            sleep(1)
            enginemove = RunningEngine.readMove(Verbose=False)
            if enginemove:
                print("Engine says %s !" % enginemove)
                Board.push(chess.Move.from_uci(enginemove))
                WaitingEngineMove = False
                if not MovingModeEnabled:
                    break
                From = enginemove[:2]
                From = coordLabelToCoord(From)
                
                To = enginemove[2:]
                To = coordLabelToCoord(To)

                if ComputerSide:
                    From = virtualAbsoluteCoordinateToXY(From)
                    From = 63 - From
                    From = virtualAbsoluteCoordinateToXY(From)
                    To = virtualAbsoluteCoordinateToXY(To)
                    To = 63 - To
                    To = virtualAbsoluteCoordinateToXY(To)
                

                ScreenSquarePair = [From, To]
                print(ScreenSquarePair)
                makeMoveOnScreen(ScreenSquarePair, BrowserAbsolutePosition)
                print("Clicking %s" % ScreenSquarePair)
                
                
                while True:
                    TestingScreenMovelist = detectScreenBoardMovement(Board, PieceValueMap, ComputerSide)
                    if not TestingScreenMovelist:
                        break
                    MovingPiecePool = [ x[0] for x in TestingScreenMovelist ]
                    ERROR = 0
                    for p in MovingPiecePool:
                        if p in AllPieces[ComputerSide]:
                            ERROR = 1

                    if ERROR:
                        print("Repeating movement.")
                        flickMouse(BrowserAbsolutePosition)
                        makeMoveOnScreen(ScreenSquarePair, BrowserAbsolutePosition)
                        sleep(0.2)
                    else:
                        print("Move sucesfully done.")
                        break
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Session Ends.")
            exit()
        
def virtualAbsoluteCoordinateToXY(coord):
    if type(coord) == list:
        C = coord[1] * 8
        C += coord[0]
        return C
    elif type(coord) == int:
        X = coord % 8
        Y = (coord - X) // 8
        return [X,Y]
    else:
        raise

# returns absolute number.
def screenCoordinateToVirtualBoard(I):
    j = I % 8
    i = (I-j)//8
    i = 7 - i

    return i * 8 + j

def ReadScreen(PieceValueMap):
    if TestMode:
        B = fullScreenToBoard('screenshots/referencebe2e4.png')
    else:
        B = fullScreenToBoard(PathToPresentBoardScreenshot)
    #B = ProcessImage(B)
    #B.show()
    MountedBoard = AnalyzeBoard(B, PieceValueMap, KeepSquareImages)

    showMountedBoard(MountedBoard)
    return MountedBoard
    
def coordLabelToCoord(letternum):
    L = "abcdefgh"

    if type(letternum) == str:
        X = L.index(letternum[0])
        Y = 8 - int(letternum[1])

        assert(0<=X<8)
        assert(0<=Y<8)
        return [X,Y]

    else:
        X = L[letternum[0]]
        Y = 8 - letternum[1]
        return "%s%i" % (X,Y)

def detectScreenBoardMovement(Board, PieceValueMap, ComputerSide):
    takeScreenshot()
    ScreenBoard = ReadScreen(PieceValueMap)
    # rotate ScreenBoard if playing black so its on bottom:
    if ComputerSide:
        ScreenBoard = list(reversed(ScreenBoard))
    Difference = {}
    for k in range(64):
        boardpiece = str(Board.piece_at(screenCoordinateToVirtualBoard(k)))
        screenpiece = ScreenBoard[k]
        if boardpiece == 'None':
            boardpiece = 'x'

        if boardpiece != screenpiece:
            Difference.update({k:[boardpiece, screenpiece]})
    if Difference:
        MOVES = []
        diffKeys = list(Difference.keys())
        for k in range(len(diffKeys)):
            for v in range(len(diffKeys)):
                A = Difference[diffKeys[k]][0]
                B = Difference[diffKeys[v]][1]
                if B == 'x':
                    continue
                if A == B:
                    MOVES.append([B, diffKeys[k], diffKeys[v]])
                    Difference[diffKeys[k]] = ['x','x']
                    Difference[diffKeys[v]] = ['x','x']
        return MOVES
    
def tryNewGame(Board, PieceValueMap, ComputerSide):
    if not AutoNewGameMode:
        return False
    mouseClick(NewGameBox, BrowserAbsolutePosition)
    sleep(6)
    HypoteticalBoard= ReadScreen(PieceValueMap)
    print(":" * 12)
    HypoteticalNewComputerSide = 0 if HypoteticalBoard[0] == 'r' else 1
    
    MOVES_AgainstReferenceBoard = detectScreenBoardMovement(
    referenceInitialBoard, PieceValueMap, HypoteticalNewComputerSide)
    MOVES_AgainstReferenceBoard = len(MOVES_AgainstReferenceBoard) if MOVES_AgainstReferenceBoard else 0
    
    MOVES_AgainstSelfBoard = detectScreenBoardMovement(
        Board, PieceValueMap, HypoteticalNewComputerSide)
    MOVES_AgainstSelfBoard = len(MOVES_AgainstSelfBoard) if MOVES_AgainstSelfBoard else 0
    
    if HypoteticalNewComputerSide != ComputerSide or\
       MOVES_AgainstReferenceBoard == 0 or\
       MOVES_AgainstReferenceBoard == 1:
       if MOVES_AgainstSelfBoard not in [0,1]:    
           return True
    return False
    
if __name__ == '__main__':


    
    PLAY = 1
    while PLAY:
        Game()
