#!/bin/python
import chess
from time import sleep, time as Time
import os
import sys
import signal

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
               --secondary //load secondary reference screenshot. (virtual machine helper)

''')
    exit()
    
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from tileRead import *
from mouse_click import makeMoveOnScreen, flickMouse, mouseClick
from enginewrapper import Engine
from keyConstants import *

def CleanExit(signal, frame):
    print("\r  \n\n\tSession Over.\n\n")
    RunningEngine.destroy()
    exit(0)
signal.signal(signal.SIGINT, CleanExit)


if '--full' in sys.argv:
    print("engine will think for longer.")
    engineRunCommand += ['--xdeep', '1']
MovingModeEnabled = False if '--nomove' in sys.argv else True
KeepSquareImages = True if '--watch' in sys.argv else False
TestMode = True if '--test' in sys.argv else False
AutoNewGameMode = True if '--autonew' in sys.argv else False
NullMachine = True if '--null' in sys.argv else False
if '--old' in sys.argv:
    engineRunCommand[0] += "OLD"
    print("running %s instead" % engineRunCommand[0])

AllPieces = [ ['P','R','N','B','Q','K'],
              ['p','r','n','b','q','k'] ]

Colors = { 0:'White', 1: 'Black' }

requiredDirectories = ['screenshots', 'SquareImages']
for DIR in requiredDirectories:
    if not os.path.isdir(DIR):
        os.mkdir(DIR)
     
referenceInitialBoard = chess.Board()
BrowserAbsolutePosition = grabBrowserAbsolutePosition()
#print("B.A.P. %s" %BrowserAbsolutePosition)
#print("path %s" % os.path.realpath(__file__))
print("Board Position on Screen: %s" % BoardDelimitationBox)
      
G = fullScreenToBoard(PathToReferenceScreenshot)
GeneralBoardValue = EvaluateColoredBoard(G)

RunningEngine = Engine(engineRunCommand, True)

print('\n--chessbotcom--\n')
print("reference screenshot is: %s." % PathToReferenceScreenshot)
# print(' '.join(engineRunCommand))

def Game():
    PieceValueMap = setupTileReadingValues(BoardDelimitationBox)
    
    ComputerSide = None
    while ComputerSide == None:

        if not TestMode:
            takeScreenshot()
        while not validadeBoard():
            sleep(1)
            continue
        
        initial = ReadScreen(PieceValueMap)
        if initial[0] == 'r' and initial[7] == 'r':
            ComputerSide = 0
        elif initial[0] == 'R' and initial[7] == 'R':
            ComputerSide = 1
        else:
            sleep(2)
            
    print( "Computer playing as %s." % Colors[ComputerSide] )
    
    
    Board = chess.Board()
    WaitingEngineMove = False
    EngineThinkingStartTime = Time()
    
    print("board reader online.")
    

  
    RunningEngine.newGame()
    RunningEngine.send("load any")
    lastPieceCount = 32
    RunningEngine.send('new')
    if not ComputerSide:
        RunningEngine.send('white')
        RunningEngine.send('go')
        WaitingEngineMove = True
    else:
        RunningEngine.send('black')
    game = True
    while game: 
        
        MOVES, pieceCount = detectScreenBoardMovement(Board, PieceValueMap, ComputerSide)
            
        if CheckForNewGameImage(PIL.Image.open(PathToPresentBoardScreenshot)):
            if AutoNewGameMode:
                mouseClick(NewGameBox, BrowserAbsolutePosition)
                sleep(3)
                print("\nScreen to new game detected!")
                #if tryNewGame(Board, PieceValueMap, ComputerSide):
                return
            else:
                RunningEngine.destroy()
                exit()
        
        V = validadeBoard()
        if not V:
            print("invalid screenshot.")
            continue        
        if pieceCount > lastPieceCount or pieceCount < lastPieceCount-2:
            print( "invalid piece count. (%i against %i)" % (pieceCount,lastPieceCount) )
            continue

            
        if MOVES:
            #print("&" * 12)
            # moves saved as 'screen coordinates'
            print(MOVES)
            
            if len(MOVES) > 3: # bail and don't process if screenshot proves to be invalid.
                               # maybe website is waiting response for new game? check.
                               # try to start new game, and reboot.
                print("Bizarre board conformation!")


            castlingExclusion = {'h8f8': 'e8g8', 'a8c8': 'e8b8', 'a8d8': 'e8c8',
                                 'h1f1': 'e1g1', 'a1c1': 'e1b1', 'a1d1': 'e1c1'}
 

            for M in MOVES:
                if M[0] in AllPieces[1-ComputerSide]:
                    #filter castling:
                    if M[3] in castlingExclusion.keys():
                        if castlingExclusion[M[3]] in [ m[3] for m in MOVES]:
                            continue
                        
                    print("Move detected: %s" % showmove(M))
                    
                    if chess.Move.from_uci(M[3]) in list(Board.generate_legal_moves()):
                        Board.push(chess.Move.from_uci(M[3]))
                        RunningEngine.appendToComm(str(Board)+'\n')
                        RunningEngine.send(M[3])
                        WaitingEngineMove = True
                        print("\nWaiting engine movement...\n")
                        lastPieceCount = pieceCount
                        EngineThinkingStartTime = Time()
                    else:
                        print("ILLEGAL MOVE! %s" % M[3])
                        RunningEngine.send("dump")
                        print("Ignoring...")

                else:
                    print("Redoing movement %s." % M[3])
                    makeMovementFromContrastingBoard(M[3], ComputerSide, True)

        else:
            print("|" * 12)

        while WaitingEngineMove:
            sleep(0.3)

            print("\r... %.1fs" % (Time() - EngineThinkingStartTime), end=" ")
            enginemove = RunningEngine.readMove(Verbose=False)
            if enginemove:
                EngineThinkingTime = Time() - EngineThinkingStartTime
                print("\rEngine says %s !  :%is" % (enginemove, EngineThinkingTime)   )
                Board.push(chess.Move.from_uci(enginemove))
                RunningEngine.send("show")
                
                RunningEngine.appendToComm(str(Board))
                WaitingEngineMove = False
                if not MovingModeEnabled:
                    break

                PromoteMove = True if 'q' in enginemove else False
                makeMovementFromContrastingBoard(enginemove, ComputerSide, PromoteMove=PromoteMove)

        sleep(0.2)
        
def makeMovementFromContrastingBoard(movement, ComputerSide, Invert=False, PromoteMove=False):

    if not Invert:
        From = movement[:2]
        To = movement[2:]
    else:
        To = movement[:2]
        From = movement[2:]
        
    From = coordLabelToCoord(From)
    To = coordLabelToCoord(To)

    if ComputerSide:
        From = virtualAbsoluteCoordinateToXY(From)
        From = 63 - From
        From = virtualAbsoluteCoordinateToXY(From)
        To = virtualAbsoluteCoordinateToXY(To)
        To = 63 - To
        To = virtualAbsoluteCoordinateToXY(To)


    ScreenSquarePair = [From, To]
    #print(ScreenSquarePair)
    makeMoveOnScreen(ScreenSquarePair, BrowserAbsolutePosition, PromoteMove=PromoteMove)
    #print("Clicking %s" % ScreenSquarePair)
    
# returns int 0~63 from list [ 0~7, 0~7 ] and vice & versa.
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

    MountedBoard = AnalyzeBoard(B, PieceValueMap, KeepSquareImages)

    print(showMountedBoard(MountedBoard))
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
    
    # count pieces on the screen. a failsafe mechanism, as in chess
    # the number of pieces on the board never rises;
    try: # useless
        pieceCount = len([ x for x in ScreenBoard if x != "x"])
    except:
        print("Error counting pieces.")
        pieceCount = 0
    #print(pieceCount)
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
    MOVES = []
    if Difference:
        diffKeys = list(Difference.keys())
        pawns = [AllPieces[x][0] for x in range(2)]
        for k in range(len(diffKeys)):
            for v in range(len(diffKeys)):
                promotion = False
                A = Difference[diffKeys[k]][0]
                B = Difference[diffKeys[v]][1]
                
                # the piece moves from A to B;
                
                # not what we are looking for;
                if B == 'x':
                    continue
                
                # promotion processing;
                if A in pawns: 
                    pawnside = pawns.index(A)
                    if B in AllPieces[pawnside] and B != A:
                        promotion = True
                        #B = A+B
                        
                # move found;
                if A == B or promotion:
                    MOVES.append([B, diffKeys[k], diffKeys[v]])
                    Difference[diffKeys[k]] = ['x','x']
                    Difference[diffKeys[v]] = ['x','x']
                    
                    # create UCI string;
                    From = diffKeys[k]
                    From = virtualAbsoluteCoordinateToXY(From)
                    From = coordLabelToCoord(From)
                
                    To = diffKeys[v]
                    To = virtualAbsoluteCoordinateToXY(To)
                    To = coordLabelToCoord(To)
                
                    MOVES[-1].append(From+To)
                    if promotion:
                        MOVES[-1][3] += B.lower()

                        
    return MOVES, pieceCount
    
def tryNewGame(Board, PieceValueMap, ComputerSide):
    if not AutoNewGameMode:
        return False
    mouseClick(NewGameBox, BrowserAbsolutePosition)
    sleep(12)
    HypoteticalBoard= ReadScreen(PieceValueMap)
    print(":" * 12)
    HypoteticalNewComputerSide = 0 if HypoteticalBoard[0] == 'r' else 1
    
    MOVES_AgainstReferenceBoard, x = detectScreenBoardMovement(
    referenceInitialBoard, PieceValueMap, HypoteticalNewComputerSide)
    MOVES_AgainstReferenceBoard = len(MOVES_AgainstReferenceBoard)     
    MOVES_AgainstSelfBoard, x = detectScreenBoardMovement(
        Board, PieceValueMap, HypoteticalNewComputerSide)
    MOVES_AgainstSelfBoard = len(MOVES_AgainstSelfBoard) 
    
    if HypoteticalNewComputerSide != ComputerSide or\
       MOVES_AgainstReferenceBoard == 0 or\
       MOVES_AgainstReferenceBoard == 1:
       if MOVES_AgainstSelfBoard not in [0,1]:    
           return True
    return False

def validadeBoard():
    PreliminaryBoard = fullScreenToBoard(PathToPresentBoardScreenshot)
    PreliminaryBoardValue = EvaluateColoredBoard(PreliminaryBoard)


    BoardValidity = abs(PreliminaryBoardValue-GeneralBoardValue)
    print("Board validity = %i    fail @38" % BoardValidity)
    if BoardValidity > 38:
        print("Invalid board!", end=" ")
        return False
    return True

def showmove(movement):
    return '   '.join([str(x) for x in movement])
    
if __name__ == '__main__':
    PLAY = 10
    while PLAY:
        Game()
        PLAY -=1

