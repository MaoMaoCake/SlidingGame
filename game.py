import pygame, sys, random
from pygame.locals import *


class SlidingGame:
    def __init__(self, width=4, height=4, swaps=0):
        # Create the constants (go ahead and experiment with different values)
        self.board_width = width  # number of columns in the board
        self.board_height = height  # number of rows in the board
        self.TILESIZE = 80
        self.WINDOWWIDTH = 640
        self.WINDOWHEIGHT = 480
        self.FPS = 30
        self.BLANK = None

        #color setttings
        #                 R    G    B
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BRIGHTBLUE = (0, 50, 255)
        self.DARKTURQUOISE = (3, 54, 73)
        self.GREEN = (0, 204, 0)

        self.BGCOLOR = self.DARKTURQUOISE
        self.TILECOLOR = self.GREEN
        self.TEXTCOLOR = self.WHITE
        self.BORDERCOLOR = self.BRIGHTBLUE
        self.BASICFONTSIZE = 20

        self.BUTTONCOLOR = self.WHITE
        self.BUTTONTEXTCOLOR = self.BLACK
        self.MESSAGECOLOR = self.WHITE

        self.XMARGIN = int((self.WINDOWWIDTH - (self.TILESIZE * self.board_width + (self.board_width - 1))) / 2)
        self.YMARGIN = int((self.WINDOWHEIGHT - (self.TILESIZE * self.board_height + (self.board_height - 1))) / 2)

        self.UP = 'up'
        self.DOWN = 'down'
        self.LEFT = 'left'
        self.RIGHT = 'right'

    def main(self):
        global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        pygame.display.set_caption('Slide Puzzle')
        BASICFONT = pygame.font.Font('freesansbold.ttf', self.BASICFONTSIZE)

        # Store the option buttons and their rectangles in OPTIONS.
        RESET_SURF, RESET_RECT = self.makeText('Reset', self.TEXTCOLOR, self.TILECOLOR, self.WINDOWWIDTH - 120, self.WINDOWHEIGHT - 90)
        NEW_SURF, NEW_RECT = self.makeText('New Game', self.TEXTCOLOR, self.TILECOLOR, self.WINDOWWIDTH - 120, self.WINDOWHEIGHT - 60)
        SOLVE_SURF, SOLVE_RECT = self.makeText('Solve', self.TEXTCOLOR, self.TILECOLOR, self.WINDOWWIDTH - 120, self.WINDOWHEIGHT - 30)

        mainBoard, solutionSeq = self.generateNewPuzzle(80)
        SOLVEDBOARD = self.getStartingBoard()  # a solved board is the same as the board in a start state.
        allMoves = []  # list of moves made from the solved configuration

        while True:  # main game loop
            slideTo = None  # the direction, if any, a tile should slide
            msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
            if mainBoard == SOLVEDBOARD:
                msg = 'Solved!'

            self.drawBoard(mainBoard, msg)

            self.checkForQuit()
            for event in pygame.event.get():  # event handling loop
                if event.type == MOUSEBUTTONUP:
                    spotx, spoty = self.getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                    if (spotx, spoty) == (None, None):
                        # check if the user clicked on an option button
                        if RESET_RECT.collidepoint(event.pos):
                            self.resetAnimation(mainBoard, allMoves)  # clicked on Reset button
                            allMoves = []
                        elif NEW_RECT.collidepoint(event.pos):
                            mainBoard, solutionSeq = self.generateNewPuzzle(80)  # clicked on New Game button
                            allMoves = []
                        elif SOLVE_RECT.collidepoint(event.pos):
                            self.resetAnimation(mainBoard, solutionSeq + allMoves)  # clicked on Solve button
                            allMoves = []
                    else:
                        # check if the clicked tile was next to the blank spot

                        blankx, blanky = self.getBlankPosition(mainBoard)
                        if spotx == blankx + 1 and spoty == blanky:
                            slideTo = self.LEFT
                        elif spotx == blankx - 1 and spoty == blanky:
                            slideTo = self.RIGHT
                        elif spotx == blankx and spoty == blanky + 1:
                            slideTo = self.UP
                        elif spotx == blankx and spoty == blanky - 1:
                            slideTo = self.DOWN

                elif event.type == KEYUP:
                    # check if the user pressed a key to slide a tile
                    if event.key in (K_LEFT, K_a) and self.isValidMove(mainBoard, self.LEFT):
                        slideTo = self.LEFT
                    elif event.key in (K_RIGHT, K_d) and self.isValidMove(mainBoard, self.RIGHT):
                        slideTo = self.RIGHT
                    elif event.key in (K_UP, K_w) and self.isValidMove(mainBoard, self.UP):
                        slideTo = self.UP
                    elif event.key in (K_DOWN, K_s) and self.isValidMove(mainBoard, self.DOWN):
                        slideTo = self.DOWN

            if slideTo:
                self.slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.',
                               8)  # show slide on screen
                self.makeMove(mainBoard, slideTo)
                allMoves.append(slideTo)  # record the slide
            pygame.display.update()
            FPSCLOCK.tick(self.FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def checkForQuit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            self.terminate()  # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate()  # terminate if the KEYUP event was for the Esc key
            pygame.event.post(event)  # put the other KEYUP event objects back

    def getStartingBoard(self):
        # Return a board data structure with tiles in the solved state.
        # For example, if board_width and self.board_height are both 3, this function
        # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
        counter = 1
        board = []
        for x in range(self.board_width):
            column = []
            for y in range(self.board_height):
                column.append(counter)
                counter += self.board_width
            board.append(column)
            counter -= self.board_width * (self.board_height - 1) + self.board_width - 1

        board[self.board_width - 1][self.board_height - 1] = self.BLANK
        return board

    def getBlankPosition(self,board):
        # Return the x and y of board coordinates of the blank space.
        for x in range(self.board_width):
            for y in range(self.board_height):
                if board[x][y] == self.BLANK:
                    return (x, y)

    def makeMove(self,board, move):
        # This function does not check if the move is valid.
        blankx, blanky = self.getBlankPosition(board)

        if move == self.UP:
            board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
        elif move == self.DOWN:
            board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
        elif move == self.LEFT:
            board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
        elif move == self.RIGHT:
            board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

    def isValidMove(self,board, move):
        blankx, blanky = self.getBlankPosition(board)
        return (move == self.UP and blanky != len(board[0]) - 1) or \
               (move == self.DOWN and blanky != 0) or \
               (move == self.LEFT and blankx != len(board) - 1) or \
               (move == self.RIGHT and blankx != 0)

    def getRandomMove(self,board, lastMove=None):
        # start with a full list of all four moves
        validMoves = [self.UP, self.DOWN, self.LEFT, self.RIGHT]

        # remove moves from the list as they are disqualified
        if lastMove == self.UP or not self.isValidMove(board, self.DOWN):
            validMoves.remove(self.DOWN)
        if lastMove == self.DOWN or not self.isValidMove(board, self.UP):
            validMoves.remove(self.UP)
        if lastMove == self.LEFT or not self.isValidMove(board, self.RIGHT):
            validMoves.remove(self.RIGHT)
        if lastMove == self.RIGHT or not self.isValidMove(board, self.LEFT):
            validMoves.remove(self.LEFT)

        # return a random move from the list of remaining moves
        return random.choice(validMoves)

    def getLeftTopOfTile(self,tileX, tileY):
        left = self.XMARGIN + (tileX * self.TILESIZE) + (tileX - 1)
        top = self.YMARGIN + (tileY * self.TILESIZE) + (tileY - 1)
        return (left, top)

    def getSpotClicked(self, board, x, y):
        # from the x & y pixel coordinates, get the x & y board coordinates
        for tileX in range(len(board)):
            for tileY in range(len(board[0])):
                left, top = self.getLeftTopOfTile(tileX, tileY)
                tileRect = pygame.Rect(left, top, self.TILESIZE, self.TILESIZE)
                if tileRect.collidepoint(x, y):
                    return (tileX, tileY)
        return (None, None)

    def drawTile(self, tilex, tiley, number, adjx=0, adjy=0):
        # draw a tile at board coordinates tilex and tiley, optionally a few
        # pixels over (determined by adjx and adjy)
        left, top = self.getLeftTopOfTile(tilex, tiley)
        pygame.draw.rect(DISPLAYSURF, self.TILECOLOR, (left + adjx, top + adjy, self.TILESIZE, self.TILESIZE))
        textSurf = BASICFONT.render(str(number), True, self.TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(self.TILESIZE / 2) + adjx, top + int(self.TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)

    def makeText(self, text, color, bgcolor, top, left):
        # create the Surface and Rect objects for some text.
        textSurf = BASICFONT.render(text, True, color, bgcolor)
        textRect = textSurf.get_rect()
        textRect.topleft = (top, left)
        return (textSurf, textRect)

    def drawBoard(self, board, message):
        DISPLAYSURF.fill(self.BGCOLOR)
        if message:
            textSurf, textRect = self.makeText(message, self.MESSAGECOLOR, self.BGCOLOR, 5, 5)
            DISPLAYSURF.blit(textSurf, textRect)

        for tilex in range(len(board)):
            for tiley in range(len(board[0])):
                if board[tilex][tiley]:
                    self.drawTile(tilex, tiley, board[tilex][tiley])

        left, top = self.getLeftTopOfTile(0, 0)
        width = self.board_width * self.TILESIZE
        height = self.board_height * self.TILESIZE
        pygame.draw.rect(DISPLAYSURF, self.BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

        DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

    def slideAnimation(self, board, direction, message, animationSpeed):
        # Note: This function does not check if the move is valid.

        blankx, blanky = self.getBlankPosition(board)
        if direction == self.UP:
            movex = blankx
            movey = blanky + 1
        elif direction == self.DOWN:
            movex = blankx
            movey = blanky - 1
        elif direction == self.LEFT:
            movex = blankx + 1
            movey = blanky
        elif direction == self.RIGHT:
            movex = blankx - 1
            movey = blanky

        # prepare the base surface
        self.drawBoard(board, message)
        baseSurf = DISPLAYSURF.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        moveLeft, moveTop = self.getLeftTopOfTile(movex, movey)
        pygame.draw.rect(baseSurf, self.BGCOLOR, (moveLeft, moveTop, self.TILESIZE, self.TILESIZE))

        for i in range(0, self.TILESIZE, animationSpeed):
            # animate the tile sliding over
            self.checkForQuit()
            DISPLAYSURF.blit(baseSurf, (0, 0))
            if direction == self.UP:
                self.drawTile(movex, movey, board[movex][movey], 0, -i)
            if direction == self.DOWN:
                self.drawTile(movex, movey, board[movex][movey], 0, i)
            if direction == self.LEFT:
                self.drawTile(movex, movey, board[movex][movey], -i, 0)
            if direction == self.RIGHT:
                self.drawTile(movex, movey, board[movex][movey], i, 0)

            pygame.display.update()
            FPSCLOCK.tick(self.FPS)

    def generateNewPuzzle(self, numSlides):
        # From a starting configuration, make numSlides number of moves (and
        # animate these moves).
        sequence = []
        board = self.getStartingBoard()
        self.drawBoard(board, '')
        pygame.display.update()
        pygame.time.wait(500)  # pause 500 milliseconds for effect
        lastMove = None
        for i in range(numSlides):
            move = self.getRandomMove(board, lastMove)
            self.slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(self.TILESIZE / 3))
            self.makeMove(board, move)
            sequence.append(move)
            lastMove = move
        return (board, sequence)

    def resetAnimation(self, board, allMoves):
        # make all of the moves in allMoves in reverse.
        revAllMoves = allMoves[:]  # gets a copy of the list
        revAllMoves.reverse()

        for move in revAllMoves:
            if move == self.UP:
                oppositeMove = self.DOWN
            elif move == self.DOWN:
                oppositeMove = self.UP
            elif move == self.RIGHT:
                oppositeMove = self.LEFT
            elif move == self.LEFT:
                oppositeMove = self.RIGHT
            self.slideAnimation(board, oppositeMove, '', animationSpeed=int(self.TILESIZE / 2))
            self.makeMove(board, oppositeMove)
