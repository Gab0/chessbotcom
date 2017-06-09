#!/bin/python

from subprocess import run, PIPE
import PIL.Image
import PIL.ImageChops
import time
import imagehash
import shutil

startingTime = time.time()
from keyConstants import *

def grabBrowserAbsolutePosition(browserName=WindowNameKeyword):
    C = ["xdotool", "search", "--name", browserName]
    ID = run(C, stdout=PIPE).stdout.decode("utf-8")
    C = ["xwininfo", "-id", ID]
    rawINFO = run(C, stdout=PIPE).stdout.decode("utf-8")

    INFO = {'absoluteX': 'Absolute upper-left X:', 'absoluteY': 'Absolute upper-left Y:',
            'relativeX': 'Relative upper-left X:', 'relativeY': 'Relative upper-left Y:'}
    
    for line in rawINFO.split('\n'):
        for K in INFO.keys():
            if type(INFO[K]) == int:
                continue
            if INFO[K] in line:
                INFO[K] = int(line.split(':')[1])

    for K in INFO.keys():
        assert(type(INFO[K]) == int)

    X = INFO['absoluteX'] - INFO['relativeX']
    Y = INFO['absoluteY'] - INFO['absoluteY']
        
    COORD = [X, Y]
    print(COORD)
    return COORD


def takeScreenshot(makeReference=False):

    FilePath = PathToPresentBoardScreenshot if not makeReference else PathToReferenceScreenshot
    
    command = ['wmctrl', '-l']
    winList = run(command, stdout=PIPE, stderr=PIPE)
    winList = winList.stdout.decode('utf-8').split('\n')
    winID = None
    #print(winList)
    for line in winList:
        if WindowNameKeyword in line:
            winID = line.split(' ')[0]
    if winID:
        #print(winID)
        command = [ 'import', '-border', '-frame', '-window', winID,
                    '-pause', '0.1', FilePath, FilePath ]
        run(command, stdout=PIPE, stderr=PIPE)

        screenshot_name = FilePath.split('.')
        A_name = screenshot_name[0] + '-0.' + screenshot_name[1]
        B_name = screenshot_name[0] + '-1.' + screenshot_name[1]
        # taking two separate screenshots guarates no piece is photographed while moving across the screen, which cause issues.
        A = PIL.Image.open(A_name)
        B = PIL.Image.open(B_name)
        if imagehash.phash(A) == imagehash.phash(B):
            shutil.copyfile(A_name, FilePath)
        else:
            print("Movement on screenshot detected. Ignoring.")
        
            

def createBlackPointPieceMap(iBPPM):
    PieceValueMap = {
        iBPPM[0]: 'r',
        iBPPM[1]: 'n',
        iBPPM[2]: 'b',
        iBPPM[3]: 'q',
        iBPPM[4]: 'k',
        iBPPM[5]: 'b',
        iBPPM[6]: 'n',
        iBPPM[7]: 'r',
        iBPPM[8]: 'p',
        iBPPM[9]: 'p',
        iBPPM[10]: 'p',
        iBPPM[11]: 'p',
        iBPPM[12]: 'p',
        iBPPM[13]: 'p',
        iBPPM[14]: 'p',
        iBPPM[15]: 'p',
        #
        iBPPM[32]: 'x',
        iBPPM[33]: 'x',
        #
        iBPPM[48]: 'P',
        iBPPM[49]: 'P',
        iBPPM[50]: 'P',
        iBPPM[51]: 'P',
        iBPPM[52]: 'P',
        iBPPM[53]: 'P',
        iBPPM[54]: 'P',
        iBPPM[55]: 'P',
        iBPPM[56]: 'R',
        iBPPM[57]: 'N',
        iBPPM[58]: 'B',
        iBPPM[59]: 'Q',
        iBPPM[60]: 'K',
        iBPPM[61]: 'B',
        iBPPM[62]: 'N',
        iBPPM[63]: 'R'
                     }
    
    return PieceValueMap
    
    

def fullScreenToBoard(screenpath):
    IMG = PIL.Image.open(screenpath)
    IMG = IMG.crop(BoardDelimitationBox)
    return IMG

def showMountedBoard(MountedBoardArray):
    BOARD = "\n"
    for i in range(8):
        for j in range(8):
            BOARD += MountedBoardArray[i*8+j]
            BOARD += " "
        BOARD += "\n"
    BOARD += "\n"

    return BOARD
    
def EvaluateSquare(IMG):
    score = imagehash.dhash(IMG)
    return score

def EvaluateColoredBoard(IMG):
    score = imagehash.phash(IMG)
    return score

def CheckForNewGameImage(IMG):
    NewGameCounter=0
    pixels = IMG.load()
    for k in range(IMG.width):
        for j in range(IMG.height):
            if pixels[k,j] == (230, 145, 44):
                NewGameCounter += 1
                if NewGameCounter > 210:
                    return True
    return False
def GameStillRunning(IMG):
    pass
 
def ProcessImage(IMG):
    WHITE = (255,255,255,255)
    pixels = IMG.load()
    for i in range(IMG.size[0]):
        for j in range(IMG.size[1]):
            try:
                if sum(pixels[i,j]) > BlackThreshold:
                    pixels[i,j] = WHITE
            except TypeError:
                print("Board Image processing failure. continuing...")
                
    bg = PIL.Image.new(IMG.mode, IMG.size, WHITE)
    diff = PIL.ImageChops.difference(IMG,bg)
    bbox = diff.getbbox()
    
    return IMG.crop(bbox)

# redundant?
def GenerateSquareImages(BoardImage):
    BoardSquares = SliceBoard(BoardImage)
    
    IDX=0
    for S in BoardSquares:

        BoardSquares[IDX] = ProcessImage(S)
        BoardSquares[IDX].save("ReferenceSquareImages/%i.png" % IDX)
        IDX+=1
    return BoardSquares

def SliceBoard(BOARD):
    bWidth, bHeight = BOARD.size
    if bWidth % 2: bWidth -=1
    if bHeight % 2: bHeight -=1

    xDotDistance = bWidth/8
    yDotDistance = bHeight/8

    Squares = []
    for y in range(8):
        for x in range(8):
            X = x * xDotDistance
            Y = y * yDotDistance
            box = (X, Y, X + xDotDistance, Y + yDotDistance)
            p = BOARD.crop(box)
            Squares.append(p)

    return Squares

def MakeReferenceMap(BoardSquares):
    
    iBPPM = []
    for S in range(len(BoardSquares)):
        c = EvaluateSquare(BoardSquares[S])
        iBPPM.append(c)

    return iBPPM

def AnalyzeBoard(BoardImage, PieceValueMap, KeepSquareImages=False):
    BoardSquares = SliceBoard(BoardImage)

    MountedBoard = [ 'x' for i in range(64) ]
    MapKeys = PieceValueMap.keys()
    for S in range(len(BoardSquares)):
        BoardSquares[S] = ProcessImage(BoardSquares[S])
        if KeepSquareImages:
            BoardSquares[S].save("SquareImages/%i.png" % S)
        Value = EvaluateSquare(BoardSquares[S])
        #print(Value)
        k = min(MapKeys, key=lambda x:abs((x - Value)/len(x.hash)**2))
        MountedBoard[S] = PieceValueMap[k]

    return MountedBoard
                
def setupTileReadingValues(BoardDelimitationBox):
    R = fullScreenToBoard(PathToReferenceScreenshot)

    squarelist = GenerateSquareImages(R)
    iBPPM = MakeReferenceMap(squarelist)
    PieceValueMap = createBlackPointPieceMap(iBPPM)

    return PieceValueMap

def detectBoardBox():
    IMG = PIL.Image.open(PathToReferenceScreenshot)
    pixels = IMG.load()
    first = [0,0]
    last = [0,0]
    for i in range(IMG.size[0]):
        for j in range(IMG.size[1]):

            if pixels[i,j] == WhiteSquareColor:
                if not first[0]:
                    first[0] = i
                if not first[1]:
                    first[1] = j

                last[0] = max(last[0], i)
                last[1] = max(last[1], j)


    return [ first[0], first[1], last[0], last[1] ]

def processImageToFragmentDetection(Fragment, bounds):
    if len(bounds) < 4:
        bounds = [0, 0] + list(bounds)

    DATA = []
    for x in range(bounds[0], bounds[2]):
        DATA.append([])
        for y in range(bounds[1], bounds[3]):
            W = sum(Fragment[x, y])
            if W > 300:
                DATA[-1].append(0)
            else:
                DATA[-1].append(1)

    return DATA

def detectSubImage(_FRAG, _IMAGE):
    print("Processing %s" % _FRAG)
    FRAG = PIL.Image.open(_FRAG)
    FRAGpx = FRAG.load()
    FRAGpx = processImageToFragmentDetection(FRAGpx, FRAG.size)
    
    IMG = PIL.Image.open(_IMAGE)
    IMGpx = IMG.load()
    IMGpx = processImageToFragmentDetection(IMGpx, WinnerSearchSpaceBox)

    for i in range(len(IMGpx) - len(FRAGpx)):
        for j in range(len(IMGpx[0]) - len(FRAGpx[0])):
            I=0
            J=0
            LineScore=0
            while True:
                A = IMGpx[i+I][j+J]
                B = FRAGpx[I][J]
                
                if A == B:
                    LineScore +=1
                J+=1
                if J >= FRAG.size[1]:
                    #print("%i %i" % ( I,J ) )
                    if LineScore/(J+1) > 0.7:
                        LineScore=0
                        J=0
                        I+=1
                        if I >= FRAG.size[0]:
                            return True
                    else:
                        break
    return False
    
BoardDelimitationBox = detectBoardBox()

#print('done. %i ' % (time.time() - startingTime))
