from itertools import cycle
import random
import sys

import pygame
from neural_networks import NeuralNetworkGA

from pygame.locals import *

FPS = 200 # Default Value: 30
SCREENWIDTH  = 288 # 288
SCREENHEIGHT = 512 # 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        # amount by which base can maximum shift to left
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK
    global iteration, generation, networks, genFitness, populationSize

    # Neural network genetic algorithm parameters.
    networkArchitecture = [2, 6, 1]
    populationSize = 10
    selectionSizeRate = 0.4
    mutationRate = 0.25

    # Neural network genetic algorithm initialization.
    networks = NeuralNetworkGA.NeuralNetworkGA(networkArchitecture, populationSize, selectionSizeRate, mutationRate)

    # Global variables.
    iteration = 0
    generation = 0
    genFitness = []

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            """
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
            """
        # Automatic start for Neural Network Training.
        SOUNDS['wing'].play()
        return {
            'playery': playery + playerShmVals['val'],
            'basex': basex,
            'playerIndexGen': playerIndexGen,
        }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']
    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward accleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps

    global individual, nextPipes, individualFitness, iteration, generation, networks, genFitness, populationSize
    nextPipes = [upperPipes[0], lowerPipes[0]]

    # End of current generation fitness evaluation.
    if iteration % populationSize == 0 and iteration != 0:
        print("Population Fitness: "+ str(genFitness))
        print(" ")
        generation += 1
        print("Generation: " + str(generation))
        networks.updateFitness(genFitness)
        networks.evolve()
        genFitness = []
        iteration = 0

    print("Individual: " + str(iteration + 1))
    individual = networks.getPopulationIndividuals()[iteration]
    individualFitness = 0
    iteration += 1

    while True:
        # Player mid position.
        playerxMidPos = playerx + IMAGES['player'][0].get_height() / 2
        playeryMidPos = playery + IMAGES['player'][0].get_width() / 2

        # Next pipe gap center position.
        nextPipeGapCenter = nextPipes[1]['y'] - PIPEGAPSIZE / 2
        nextPipeWidthEnd = nextPipes[0]['x'] + IMAGES['pipe'][0].get_width()

        # Difference between player position and next pipe gap position.
        heightDifference = nextPipeGapCenter - playeryMidPos
        horizontalDistance = nextPipeWidthEnd - playerxMidPos

        # Screen grid representation.
        # grid = screenGrid(34, 4, playerxMidPos, playeryMidPos, nextPipes[0]['x'], nextPipeWidthEnd,
        #        nextPipes[1]['y'] - PIPEGAPSIZE, nextPipes[1]['y'])
        # showGrid(grid, (240, 5), 6)

        # Next pipe condition.
        if horizontalDistance <= 0:
            nextPipes = [upperPipes[1], lowerPipes[1]]

        # Fitness condition.
        if (playeryMidPos + IMAGES['player'][0].get_width() / 2 < int(nextPipes[1]['y'])
            and playeryMidPos - IMAGES['player'][0].get_width() / 2 > int(nextPipes[1]['y'] - PIPEGAPSIZE)):
            individualFitness += 1

        # User interaction.
        for event in pygame.event.get():
            # Quit game.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Show current fittest curve.
            if event.type == KEYDOWN and event.key == K_p:
                networks.fittestCurve()

            # Save the current neural network genetic algorithm.
            if event.type == KEYDOWN and event.key == K_s:
                networks.save("flappy01")

        # Neural network forward feeding.
        individual.forwardFeed([horizontalDistance / 431, heightDifference / 397])
        #individual.forwardFeed(gridToArray(grid))

        # Neural network flapping.
        if individual.getOutput()[0] > 0.5 and playery > 1:
            if playery > -2 * IMAGES['player'][0].get_height():
                playerVelY = playerFlapAcc
                playerFlapped = True
                SOUNDS['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        # collision
        if crashTest[0]:
            print("Fitness: " + str(individualFitness))
            genFitness.append(individualFitness)
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            #newPipe = getPipe(50)
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            """
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return
            """

        # Automatic restart.
        if playery + playerHeight >= BASEY - 1:
            return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    #gapY += 100 # Gap increasing
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]

def getPipe(gapY):
    """returns pipe with an specified vertical gap position"""
    # y of gap between upper and lower pipe
    #gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]

def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

#---------------------------Screen grid---------------------------#
def playerVerticalGrid(gridSize, numberOfPixels, playeryMidPos):
    """Returns an array of a grid representation of the screen of the vertical player position."""
    pixelsArray = [0] * numberOfPixels
    for i in range(numberOfPixels):
        # Player Position
        if (playeryMidPos >= i*gridSize and playeryMidPos < (i+1)*gridSize):
            pixelsArray[i] = 0.5
        # Ground Position
        if (BASEY - IMAGES['player'][0].get_height() / 2 - 1 <= i * gridSize):
            pixelsArray[i] = 1
    return pixelsArray

def pipeVerticalGrid(gridSize, numberOfPixels, upperPipey, lowerPipey):
    """Returns an array of a grid representation of the screen of the vertical pipes position."""
    pixelsArray = [1] * numberOfPixels
    for i in range(numberOfPixels):
        # Gap position
        if (upperPipey <= i * gridSize and lowerPipey >= (i + 1) * gridSize):
            pixelsArray[i] = 0
        # Ground Position
        if (BASEY - IMAGES['player'][0].get_height() / 2 - 1 <= i * gridSize):
            pixelsArray[i] = 1
    return pixelsArray

def emptyVerticalGrid(gridSize, numberOfPixels):
    """Returns an array of a grid representation of the screen of the vertical environment position."""
    pixelsArray = [0] * numberOfPixels
    for i in range(numberOfPixels):
        # Ground Position
        if (BASEY - IMAGES['player'][0].get_height() / 2 - 1 <= i * gridSize):
            pixelsArray[i] = 1
    return pixelsArray

def playerInGapGrid(playerVerticalArray, pipeVerticalArray):
    """Returns an array of a grid representation of the screen of the vertical player and pipes position."""
    playerInGapArray = pipeVerticalArray
    for i in range(len(playerVerticalArray)):
        if playerVerticalArray[i] == 0.5:
            playerInGapArray[i] = 0.5
    return playerInGapArray

def screenGrid(gridSize, numberOfCols, playerxMidPos, playeryMidPos, pipex0, pipex1, upperPipey, lowerPipey):
    """Returns a matrix of a grid representation of the screen showing all the objects in it."""
    grid = []
    numberOfPixels = int(445 / gridSize)
    for i in range(numberOfCols):
        # Player vertical grid
        if i == 0:
            if pipex0 <= i*gridSize + playerxMidPos and pipex1 >= i*gridSize + playerxMidPos:
                verticalGrid = playerInGapGrid(playerVerticalGrid(gridSize, numberOfPixels, playeryMidPos), pipeVerticalGrid(gridSize, numberOfPixels, upperPipey, lowerPipey))
            else:
                verticalGrid = playerVerticalGrid(gridSize, numberOfPixels, playeryMidPos)
        # Pipe vertical grid
        elif pipex0 <= i*gridSize + playerxMidPos and pipex1 >= i*gridSize + playerxMidPos:
            verticalGrid = pipeVerticalGrid(gridSize, numberOfPixels, upperPipey, lowerPipey)
        # Empty vertical grid
        else:
            verticalGrid = emptyVerticalGrid(gridSize, numberOfPixels)
        grid.append(verticalGrid)
    return grid

def color(pixel):
    """Returns a pixel color according of the pixel value."""
    if pixel == 0:
        return (0, 0, 0)
    elif pixel == 0.5:
        return (0, 255, 0)
    elif pixel == 1:
        return (255, 0, 0)

def showGrid(grid, init_pos, width):
    """Show the current grid on the screen."""
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            x = init_pos[0] + 2*width * i
            y = init_pos[1] + 2*width * j
            clr = color(grid[i][j])
            pygame.draw.circle(SCREEN, clr, [x, y], width)
    pygame.display.update()

def gridToArray(grid):
    """Converts the current grid matrix into an a simple 1 dimensional array."""
    array = []
    for i in range(len(grid)):
        array += grid[i]
    return array

if __name__ == '__main__':
    main()
