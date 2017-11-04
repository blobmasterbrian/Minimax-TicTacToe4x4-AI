# Brian Quinn - AI CS4613
# Tic Tac Toe Alpha-Beta Search AI using Minimax Algorithm
# Alpha-Beta pruning implemented

import math
import random
from sys import exit
from collections import defaultdict

# Pygame module imported for computer graphics.
# Pygame is a popular API to make visuals easier.
import pygame
from pygame.locals import *

# Framerate Constant (relatively unimportant for nature of the game)
FPS = 15

# Enum values for player/CPU
computer = 1
human = 2

# enum values for difficulty
easy = 49
medium = 3177
hard = 203374  # min nodes to exactly be unbeatable

# Enum values for spot locations
empty = 0
O = 3  # skipping 1 and 2 allows math shortcut for non-terminal node evaluation
X = 4

# Color Shortcuts
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
blue = (0, 0, 200)


# Base class for the players
class Player:
    # Player Init
    def __init__(self, type, symbol, name):
        self.type = type  # type of player
        self.symbol = symbol  # X or O
        self.name = name  # name

    # Board Setup
    def SetBoard(self, board):
        self.board = board

    # Move decision to be overridden
    def GetMove(self):
        pass

    # Process mouse click to be overridden
    def MouseClick(self, cell):
        pass

    # Get opponent symbol
    def OppositeSign(self, symbol):
        if symbol == O:
            return X
        return O


# Human class inherits from Player
class HumanPlayer(Player):
    # Human init
    def __init__(self, symbol, name):
        super().__init__(human, symbol, name)  # call Player constructor
        self.lastmove = -1

    # Waits until mouse click detected
    def GetMove(self):
        if(self.lastmove != -1):
            move = self.lastmove
            self.lastmove = -1
            return move

    # returns cell of mouse click
    def MouseClick(self, cell):
        if cell not in self.board.moves:  # check if cell already occupied
            self.lastmove = cell


# Computer class
class ComputerPlayer(Player):
    # Computer init
    def __init__(self, symbol, name, difficulty=hard):
        super().__init__(computer, symbol, name)  # call Player contructor
        self.lastmove = -1
        self.maxnodes = difficulty
        # primitives for statistics
        self.cutoff = False  # whether cutoff occurred
        # self.maxdepth = 0  # max depth reached
        self.currnodes = 0  # current number of nodes recursed
        self.maxprune = 0  # number of max prunings
        self.minprune = 0  # number of min prunings
        self.turn = 0


    # returns next computer move to make
    def GetMove(self):
        possiblemoves = [mv for mv in self.board.possiblecells if mv not in
        self.board.moves]  # determines possible moves

        # optimization hard coded as eval always chooses (0,0)
        if len(possiblemoves) == 16:
            self.turn += 1
            print("Static Optimized First Move.")
            return (0, 0)

        if len(possiblemoves) == 14 and (0, 1) in possiblemoves:
            self.turn += 1
            print("Static Optimized Second Move.")
            return (0, 1)
        elif len(possiblemoves) == 14:
            self.turn += 1
            print("Static Optimized Second Move.")
            return (0, 2)

        self.loop = 0  # number of possible move combinations

        # reset primitives for each move
        self.cutoff = False  # whether cutoff occurred
        maxdepth = 0  # max depth reached
        self.currnodes = 0  # current number of nodes recursed
        self.maxprune = 0  # number of max prunings
        self.minprune = 0  # number of min prunings

        # update turn
        self.turn += 1

        val, move, maxdepth = self.MaxValue(-1000, 1000)  # max utility via MaxValue func
        # print(str(self.loop) + "\tmoves")  # if you want to print move combos
        print("\nTurn", self.turn)
        if self.cutoff:
            print("Cutoff Reached")
        print("Maximum depth:", maxdepth)
        print("Number of nodes generated:", self.currnodes + 1)
        print("Number of max prunings:", self.maxprune)
        print("Number of min prunings:", self.minprune)
        return move

    # Determine value of terminal condition
    def GetScore(self):
        if self.board.Draw():
            return 0  # draw
        elif self.board.GetWinner() == self.symbol:
            return 1  # computer win
        return -1  # player win

    # returns maximum utility value
    def MaxValue(self, alpha, beta, height=0):
        self.currnodes += 1
        height += 1
        depth = height
        maxpos = None
        maxval = -1000  # utility value requested

        for move in self.board.getFreePositions():
            self.loop += 1  # increment possible move combinations
            self.board.Move(move, self.symbol)  # make corresponding move

            if self.currnodes >= self.maxnodes:
                self.cutoff = True
                playerlines1 = 0
                playerlines2 = 0
                playerlines3 = 0
                opponentlines1 = 0
                opponentlines2 = 0
                opponentlines3 = 0
                for line in self.board.alllines:
                    p1, p2, p3, p4 = line
                    val = self.board.board[p1] + self.board.board[p2] + self.board.board[p3] + self.board.board[p4]
                    val2 = self.board.board[p1] + self.board.board[p2] + self.board.board[p3] + self.board.board[p4]
                    for i in range(3):
                        if val == self.symbol * 3:
                            playerlines3 += 1
                            break
                        if val == self.symbol * 2:
                            playerlines2 += 1
                            break
                        if val == self.symbol:
                            playerlines1 += 1
                            break
                        val -= self.OppositeSign(self.symbol)

                    for i in range(3):
                        if val2 == self.OppositeSign(self.symbol) * 3:
                            opponentlines3 += 1
                            break
                        if val2 == self.OppositeSign(self.symbol) * 2:
                            opponentlines2 += 1
                            break
                        if val2 == self.OppositeSign(self.symbol):
                            opponentlines1 += 1
                            break
                        val2 -= self.symbol

                v = 6 * playerlines3 + 3 * playerlines2 + playerlines1\
                  - (6 * opponentlines3 + 3 * opponentlines2 + opponentlines1)
            else:
                if self.board.GameOver():  # evaluate terminal condition
                    v = self.GetScore()  # score of terminal condition
                else:  # switch to min choice
                    v, movepos, depth = self.MinValue(alpha, beta, height)  # call to min 'player'

            self.board.UndoMove()  # undo before decision made

            if v >= beta:
                return v, move, depth
            if v > alpha:
                alpha = v  # set alpha for next MinValue call

            if v > maxval:
                maxval = v  # set max possibile value
                maxpos = move  # set best move

            if v == 1:
                self.maxprune += 1
                break
        return maxval, maxpos, depth

    # returns minimum utility value
    def MinValue(self, alpha, beta, height=0):
        height += 1
        depth = height
        minpos = None
        minval = 1000  # utility value requested

        for move in self.board.getFreePositions():
            self.loop += 1  # increment possible move combinations
            self.board.Move(move, self.OppositeSign(self.symbol))  # make move

            if self.board.GameOver():  # evaluate terminal condition
                v = self.GetScore()  # score of terminal condition
            else:
                v, movepos, depth = self.MaxValue(alpha, beta, height)  # call to max 'player'

            self.board.UndoMove()  # undo before decision made

            if v < alpha:
                return v, move, depth
            if v < beta:
                beta = v  # set beta for next MaxValue call

            if v < minval:
                minval = v  # set min possible value
                minpos = move  # set best move
            if v == -1:
                self.minprune += 1
                break

        return minval, minpos, depth


# Tic Tac Toe board interface
class BackEndBoard:
    # all cell tuples
    possiblecells = [(a, b) for a in range(0, 4) for b in range(0, 4)]
    # all direct lines/possible wins
    alllines = [[(a, b) for a in range(0, 4)] for b in range(0, 4)] +\
               [[(b, a) for a in range(0, 4)] for b in range(0, 4)] +\
               [[(0, 0), (1, 1), (2, 2), (3, 3)],
               [(0, 3), (1, 2), (2, 1), (3, 0)]]

    # back end init
    def __init__(self):
        self.moves = []  # list of moves
        self.gameover = False  # gameover flag
        self.draw = False  # draw to screen flag
        self.board = defaultdict(lambda: empty)  # internal board

    # returns playable positions
    def getFreePositions(self):
        return [x for x in self.possiblecells if x not in self.moves]

    # creates a move with board location as position and player shape as symbol
    def Move(self, position, symbol):
        if self.board[position] != empty:
            return False  # non valid move
        self.board[position] = symbol  # set symbol
        self.moves.append(position)  # add move to list
        self.CheckGameOver()  # check gameover state
        return True  # valid move

    # undoes move to allow minimax evaluation
    def UndoMove(self):
        if len(self.moves) == 0:
            return False  # cannot undo if no moves made
        self.board[self.moves.pop()] = empty  # remove symbol from board
        self.gameover = False  # game cannot be over if undo is made
        return True  # undo completed

    def GameOver(self):
        return self.gameover  # gameover state

    def Draw(self):
        return self.draw  # return draw to screen flag

    # return winner of game
    def GetWinner(self):
        if self.GameOver() and not self.Draw():
            return self.winner  # winner

    # checks for game over possibility
    def CheckGameOver(self):
        for line in self.alllines:
            p1, p2, p3, p4 = line  # get each line coordinate
            # check if board at each position holds same symbol
            if self.board[p1] != empty and\
               self.board[p1] == self.board[p2]\
               == self.board[p3] == self.board[p4]:
                self.gameover = True  # true if equal
                self.winner = self.board[p1]  # set winner
                self.draw = False  # deny draw
                break
        else:
            if len(self.moves) == 16:
                self.draw = True  # draw if all moves made
                self.gameover = True  # end game
            else:
                self.gameover = False  # do not end


# Visual board class
class FrontBoard:
    # color numbers defined ealier
    gridcolor = black
    colorO = red
    colorX = blue

    # front end init
    def __init__(self, boardsize=500):
        self.players = []  # player list
        self.boardsize = boardsize  # size of board
        self.gameboard = BackEndBoard()  # set backend for calculations
        self.font = pygame.font.Font(None, 50)  # default text/text size

    # resets and clears board
    def reset(self):
        self.gameboard = BackEndBoard()  # new backend
        for player in self.players:
            player.SetBoard(self.gameboard)  # set players boards
        self.player1, self.player2 = self.player2, self.player1  # change order

    # print winner/loser
    def printstatus(self, screen):
        textstr = ''  # output string
        if game.gameboard.GameOver():
            if game.gameboard.Draw():
                textstr = "Draw."
            else:
                textstr = self.player1.name + " wins."
        else:
            textstr = self.player1.name + "'s turn"
        text = self.font.render(textstr, 1, black)  # render settings
        textpos = text.get_rect(centerx=screen.get_width() / 2,
                  y=self.boardsize - 5)  # text position
        screen.blit(text, textpos)  # text to screen

    # add players to self
    def AddPlayer(self, player):
        player.SetBoard(self.gameboard)  # set players board
        self.players.append(player)  # player list
        if(len(self.players) > 1):
            self.player1 = self.players[0]  # individual setting
            self.player2 = self.players[1]  # individual setting

    # actuall board drawing
    def draw(self, screen):
        tolerance = 20  # limit edges before edge of screen

        # drawing each line of the grid
        pygame.draw.line(screen, self.gridcolor,
                        (self.boardsize / 4, tolerance),
                        (self.boardsize / 4, self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        ((2 * self.boardsize) / 4, tolerance),
                        ((2 * self.boardsize) / 4,
                        self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        ((3 * self.boardsize) / 4, tolerance),
                        ((3 * self.boardsize) / 4,
                        self.boardsize - tolerance), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (self.boardsize) / 4), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (2 * self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (2 * self.boardsize) / 4), 10)
        pygame.draw.line(screen, self.gridcolor,
                        (tolerance, (3 * self.boardsize) / 4),
                        (self.boardsize - tolerance,
                        (3 * self.boardsize) / 4), 10)

        # draw each X or O
        for move in self.gameboard.moves:
            mx, my = move  # move x and y coordinates
            quarter = int(self.boardsize / 4)  # 1/4 of board size

            if self.gameboard.board[move] == O:
                # draw a O in that position
                pos = mx * quarter + int(quarter / 2), my * quarter +\
                      int(quarter / 2)
                pygame.draw.circle(screen, self.colorO, pos,
                                   int(quarter / 4) + 10, 8)
            elif self.gameboard.board[move] == X:
                # draw an X in that position
                tl = mx * quarter + int(quarter / 5), my * quarter +\
                     int(quarter / 5)

                tr = (mx + 1) * quarter - int(quarter / 5),\
                     my * quarter + int(quarter / 5)

                bl = mx * quarter + int(quarter / 5),\
                     (my + 1) * quarter - int(quarter / 5)

                br = (mx + 1) * quarter - int(quarter / 5),\
                     (my + 1) * quarter - int(quarter / 5)

                pygame.draw.line(screen, self.colorX, tl, br, 10)
                pygame.draw.line(screen, self.colorX, tr, bl, 10)

    # find the position of the mouse click
    def MouseClick(self, position):
        mx, my = position  # x and y coordinates
        if my < self.boardsize:  # if on board
            quarter = int(self.boardsize / 4)
            cx = int(math.floor(mx / quarter))
            cy = int(math.floor(my / quarter))
            cell = cx, cy  # convert to cell coordinates
            self.player1.MouseClick(cell)  # pass to player
        elif self.gameboard.GameOver():
            self.reset()  # reset board

    # update board screen
    def update(self):
        if not self.gameboard.GameOver():
            nextpos = self.player1.GetMove()
            if nextpos is not None:
                # place players symbol
                self.gameboard.Move(nextpos, self.player1.symbol)
                if not self.gameboard.GameOver():
                    # switch players for next turn
                    self.player1, self.player2 = self.player2, self.player1


# main function
if(__name__ == "__main__"):
    difficulty = input("Please select difficulty (easy, medium, hard): ").lower()
    move = int(input("Please select your turn (1,2): "))
    pygame.init()  # initialization required by module
    boardsize = 500  # board size
    # screen display
    screen = pygame.display.set_mode((boardsize, boardsize + 35))
    pygame.display.set_caption('Tic Tac Toe')  # toolbar name
    gameover = False  # gameover starts false
    clock = pygame.time.Clock()  # clock for FPS
    game = FrontBoard()  # creation of board

    if difficulty == "hard":
        if move == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", hard))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", hard))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    elif difficulty == "medium":
        if move == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", medium))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", medium))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    elif difficulty == "easy":
        if move == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer", easy))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer", easy))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    else:
        if move == 1:
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 1
            game.AddPlayer(ComputerPlayer(X, "Computer"))  # player 2
        else:
            game.AddPlayer(ComputerPlayer(X, "Computer"))  # player 1
            game.AddPlayer(HumanPlayer(O, "Player"))  # player 2
    while not gameover:
        clock.tick(FPS)  # frame settings
        screen.fill(white)  # screen background
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                game.MouseClick(event.pos)  # mouse click event
        game.update()  # update game
        game.draw(screen)  # update display
        game.printstatus(screen)  # print prompt
        pygame.display.update()  # render display update
