import pygame
import random
import sys
from pygame.locals import *
import time


class SlidingGame:
    # stack to store moves
    class ActionStack:
        def __init__(self):
            self.stack = []
            self.top = -1

        def push(self, item):
            self.stack.append(item)
            self.top += 1

        def pop(self):
            self.top -= 1
            return self.stack.pop()

        def peek(self):
            return self.stack[-1]

        def to_list(self):
            return self.stack

        def add(self, target):
            self.stack += target.stack
            self.top += len(target)
            return self

        def clear_stack(self):
            self.stack = []
            self.top = -1

        def __len__(self):
            return self.top + 1

    def __init__(self, width=4, height=4, difficulty="normal"):
        # Create the constants for game
        self.board_width = width  # number of columns in the board
        self.board_height = height  # number of rows in the board
        self.tile_size = 80
        self.window_width = 640
        self.window_height = 480
        self.FPS = 30
        self.BLANK = None
        # moves setting for difficulty
        if difficulty == "impossible":
            self.difficulty = 200
        elif difficulty == "expert":
            self.difficulty = 120
        elif difficulty == "hard":
            self.difficulty = 100
        elif difficulty == "normal":
            self.difficulty = 80
        elif difficulty == "easy+":
            self.difficulty = 60
        elif difficulty == "easy":
            self.difficulty = 40
        elif difficulty == "very easy":
            self.difficulty = 20
        elif difficulty == "idiot":
            self.difficulty = 5

        # color settings (set it to use it easier)
        #                 R    G    B
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BRIGHT_BLUE = (0, 50, 255)
        self.DARKTURQUOISE = (3, 54, 73)
        self.GREEN = (0, 204, 0)

        # set colors of UI elements
        self.bg_color = self.DARKTURQUOISE
        self.tile_color = self.GREEN
        self.text_color = self.WHITE
        self.border_color = self.BRIGHT_BLUE
        self.font_size = 20

        self.button_color = self.WHITE
        self.button_text_color = self.BLACK
        self.message_color = self.WHITE

        self.x_margin = int((self.window_width - (self.tile_size * self.board_width + (self.board_width - 1))) / 2)
        self.y_margin = int((self.window_height - (self.tile_size * self.board_height + (self.board_height - 1))) / 2)

        # set moves "data"
        self.UP = 'up'
        self.DOWN = 'down'
        self.LEFT = 'left'
        self.RIGHT = 'right'

        # pygame initialise core values
        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((self.window_width, self.window_height))  # main surface
        pygame.display.set_caption('Slide Puzzle')  # set title
        self.basic_font = pygame.font.Font('freesansbold.ttf', self.font_size)

        # Store the option buttons and their rectangles in OPTIONS.
        self.undo_surf, self.undo_rect = self.makeText('Undo', self.text_color, self.tile_color,
                                                       self.window_width - 120,
                                                       self.window_height - 120)
        self.reset_surf, self.reset_rect = self.makeText('Reset', self.text_color, self.tile_color,
                                                         self.window_width - 120,
                                                         self.window_height - 90)
        self.new_surf, self.new_rect = self.makeText('New Game', self.text_color, self.tile_color,
                                                     self.window_width - 120,
                                                     self.window_height - 60)
        self.solve_surf, self.solve_rect = self.makeText('Solve', self.text_color, self.tile_color,
                                                         self.window_width - 120,
                                                         self.window_height - 30)

    # main function
    def main(self):

        mainBoard, solutionSeq = self.generateNewPuzzle(self.difficulty)
        SOLVEDBOARD = self.getStartingBoard()  # a solved board is the same as the board in a start state.
        allMoves = self.ActionStack()  # stack of moves made from the solved configuration

        while True:  # main game loop
            slideTo = None  # the direction, if any, a tile should slide
            msg = 'Click tile or press arrow keys to slide.'  # contains the message to show in the upper left corner.
            if mainBoard == SOLVEDBOARD:
                msg = 'Solved!'

            self.drawBoard(mainBoard, msg)  # draw the main board

            self.checkForQuit()
            for event in pygame.event.get():  # event handling loop
                if event.type == MOUSEBUTTONUP:
                    spotx, spoty = self.getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                    if (spotx, spoty) == (None, None):
                        # check if the user clicked on an option button
                        if self.reset_rect.collidepoint(event.pos):  # if the reset surface is pressed
                            self.resetAnimation(mainBoard, allMoves)  # clicked on Reset button
                            allMoves.clear_stack() # clear the stack
                        elif self.new_rect.collidepoint(event.pos):  # if the new surface is pressed
                            allMoves.clear_stack()  # clear stack
                            mainBoard, solutionSeq = self.generateNewPuzzle(
                                self.difficulty)  # clicked on New Game button
                        elif self.solve_rect.collidepoint(event.pos):  # if the solve surface is pressed
                            self.resetAnimation(mainBoard, solutionSeq.add(allMoves))
                            # clicked on Solve button
                            allMoves.clear_stack()  # clear stack
                        elif self.undo_rect.collidepoint(event.pos):  # if the undo surface is pressed
                            self.undo(mainBoard, allMoves) # call undo method
                    else:
                        # check if the clicked tile was next to the blank spot
                        # set slideTo to directions
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
                    # use keyboard to control the game
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
                allMoves.push(slideTo)  # record the slide
            pygame.display.update()
            self.fps_clock.tick(self.FPS)

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

    def getBlankPosition(self, board):
        # Return the x and y of board coordinates of the blank space.
        for x in range(self.board_width):
            for y in range(self.board_height):
                if board[x][y] == self.BLANK:
                    return (x, y)

    def makeMove(self, board, move):
        # This function does not check if the move is valid.
        blankx, blanky = self.getBlankPosition(board)
        # make a move
        if move == self.UP:
            board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
        elif move == self.DOWN:
            board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
        elif move == self.LEFT:
            board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
        elif move == self.RIGHT:
            board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

    def isValidMove(self, board, move): # check for a valid move
        blankx, blanky = self.getBlankPosition(board)
        return (move == self.UP and blanky != len(board[0]) - 1) or \
               (move == self.DOWN and blanky != 0) or \
               (move == self.LEFT and blankx != len(board) - 1) or \
               (move == self.RIGHT and blankx != 0)

    def getRandomMove(self, board, lastMove=None):
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

    def getLeftTopOfTile(self, tileX, tileY):
        left = self.x_margin + (tileX * self.tile_size) + (tileX - 1)
        top = self.y_margin + (tileY * self.tile_size) + (tileY - 1)
        return (left, top)

    def getSpotClicked(self, board, x, y):
        # from the x & y pixel coordinates, get the x & y board coordinates
        for tileX in range(len(board)):
            for tileY in range(len(board[0])):
                left, top = self.getLeftTopOfTile(tileX, tileY)
                tileRect = pygame.Rect(left, top, self.tile_size, self.tile_size)
                if tileRect.collidepoint(x, y):
                    return (tileX, tileY)
        return (None, None)

    def drawTile(self, tilex, tiley, number, adjx=0, adjy=0):
        # draw a tile at board coordinates tilex and tiley, optionally a few
        # pixels over (determined by adjx and adjy)
        left, top = self.getLeftTopOfTile(tilex, tiley)
        pygame.draw.rect(self.display_surf, self.tile_color, (left + adjx, top + adjy, self.tile_size, self.tile_size))
        textSurf = self.basic_font.render(str(number), True, self.text_color)
        textRect = textSurf.get_rect()
        textRect.center = left + int(self.tile_size / 2) + adjx, top + int(self.tile_size / 2) + adjy
        self.display_surf.blit(textSurf, textRect)

    def makeText(self, text, color, bgcolor, top, left):
        # create the Surface and Rect objects for some text.
        textSurf = self.basic_font.render(text, True, color, bgcolor)
        textRect = textSurf.get_rect()
        textRect.topleft = (top, left)
        return (textSurf, textRect)

    def drawBoard(self, board, message):
        self.display_surf.fill(self.bg_color)
        if message:
            textSurf, textRect = self.makeText(message, self.message_color, self.bg_color, 5, 5)
            self.display_surf.blit(textSurf, textRect)

        for tilex in range(len(board)):
            for tiley in range(len(board[0])):
                if board[tilex][tiley]:
                    self.drawTile(tilex, tiley, board[tilex][tiley])

        left, top = self.getLeftTopOfTile(0, 0)
        width = self.board_width * self.tile_size
        height = self.board_height * self.tile_size
        pygame.draw.rect(self.display_surf, self.border_color, (left - 5, top - 5, width + 11, height + 11), 4)

        self.display_surf.blit(self.reset_surf, self.reset_rect)
        self.display_surf.blit(self.new_surf, self.new_rect)
        self.display_surf.blit(self.solve_surf, self.solve_rect)
        self.display_surf.blit(self.undo_surf, self.undo_rect)

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
        baseSurf = self.display_surf.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        moveLeft, moveTop = self.getLeftTopOfTile(movex, movey)
        pygame.draw.rect(baseSurf, self.bg_color, (moveLeft, moveTop, self.tile_size, self.tile_size))

        for i in range(0, self.tile_size, animationSpeed):
            # animate the tile sliding over
            self.checkForQuit()
            self.display_surf.blit(baseSurf, (0, 0))
            if direction == self.UP:
                self.drawTile(movex, movey, board[movex][movey], 0, -i)
            if direction == self.DOWN:
                self.drawTile(movex, movey, board[movex][movey], 0, i)
            if direction == self.LEFT:
                self.drawTile(movex, movey, board[movex][movey], -i, 0)
            if direction == self.RIGHT:
                self.drawTile(movex, movey, board[movex][movey], i, 0)

            pygame.display.update()
            self.fps_clock.tick(self.FPS)

    def generateNewPuzzle(self, numSlides):
        # From a starting configuration, make numSlides number of moves (and
        # animate these moves).
        sequence = self.ActionStack()
        board = self.getStartingBoard()
        self.drawBoard(board, '')
        pygame.display.update()
        pygame.time.wait(500)  # pause 500 milliseconds for effect
        lastMove = None
        if numSlides >= 100:
            for i in range(numSlides):
                move = self.getRandomMove(board, lastMove)
                self.slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(self.tile_size))
                self.makeMove(board, move)
                sequence.push(move)
                lastMove = move
            return board, sequence
        elif numSlides < 100:
            for i in range(numSlides):
                move = self.getRandomMove(board, lastMove)
                self.slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(self.tile_size / 3))
                self.makeMove(board, move)
                sequence.push(move)
                lastMove = move
            return board, sequence

    def resetAnimation(self, board, allMoves):
        # make all of the moves in allMoves in reverse.
        try:
            for i in range(len(allMoves)):
                move = allMoves.pop()
                print(move)
                if move == self.UP:
                    oppositeMove = self.DOWN
                elif move == self.DOWN:
                    oppositeMove = self.UP
                elif move == self.RIGHT:
                    oppositeMove = self.LEFT
                elif move == self.LEFT:
                    oppositeMove = self.RIGHT
                self.slideAnimation(board, oppositeMove, '', animationSpeed=int(self.tile_size / 2))
                self.makeMove(board, oppositeMove)
        except IndexError:
            self.drawBoard(board, "Already solved")
    def undo(self, board, allMoves):
        # make the latest moves in allMoves in reverse
        try:
            move = allMoves.pop()
            print(move)
            if move == self.UP:
                oppositeMove = self.DOWN
            elif move == self.DOWN:
                oppositeMove = self.UP
            elif move == self.RIGHT:
                oppositeMove = self.LEFT
            elif move == self.LEFT:
                oppositeMove = self.RIGHT
            self.slideAnimation(board, oppositeMove, '', animationSpeed=int(self.tile_size / 2))
            self.makeMove(board, oppositeMove)
        except IndexError:
            self.drawBoard(board, "No Move to undo")
