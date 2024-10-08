"""Games or Adversarial Search (Chapter 5)"""

import copy
import itertools
import random
from collections import namedtuple
import numpy as np
import time
from utils import vector_add
global timer1
timer1 = 0
global statedepth
statedepth = 0
GameState = namedtuple('GameState', 'to_move, utility, board, moves')
StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')


GameState = namedtuple('GameState', 'to_move, utility, board, moves, xpos, opos')

def gen_state(to_move='X', x_positions=[], o_positions=[], h=7, v=7):
    """Given whose turn it is to move, the positions of X's on the board, the
    positions of O's on the board, and, (optionally) number of rows, columns
    and how many consecutive X's or O's required to win, return the corresponding
    game state"""

    moves = set([(x, y) for x in range(0, h) for y in range(0, h)]) - set(x_positions) - set(o_positions)
    moves = list(moves)
    for i in range(h):  # removing the locations of all the black lines
            if (i == 0 or i == 6):
                if (i, 1) in moves:
                    moves.remove((i, 1))
                if (i, 2) in moves:
                    moves.remove((i, 2))
                if (i, 4) in moves:
                    moves.remove((i, 4))
                if (i, 5) in moves:
                    moves.remove((i, 5))
            if (i == 1 or i ==5):
                if (i, 0) in moves:
                    moves.remove((i, 0))
                if (i, 2) in moves:
                    moves.remove((i, 2))
                if (i, 4) in moves:
                    moves.remove((i, 4))
                if (i, 6) in moves:
                    moves.remove((i, 6))
            if (i == 2 or i ==4):
                if (i, 0) in moves:
                    moves.remove((i, 0))
                if (i, 1) in moves:
                    moves.remove((i, 1))
                if (i, 5) in moves:
                    moves.remove((i, 5))
                if (i, 6) in moves:
                    moves.remove((i, 6))
            if (i == 3):
                if (3, 3) in moves:
                    moves.remove((3, 3))
    board = {}
    for pos in x_positions:
        board[pos] = 'X'
    for pos in o_positions:
        board[pos] = 'O'
    return GameState(to_move=to_move, utility=1, board=board, moves=moves , xpos = x_positions, opos = o_positions)


# ______________________________________________________________________________
# MinMax Search


def minmax_decision(state, game):
    """Given a state in a game, calculate the best move by searching
    forward all the way to the terminal states. [Figure 5.3]"""
    timer1= time.time()
    player = game.to_move(state)

    def max_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a)))
        return v

    def min_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a)))
        return v

    # Body of minmax_decision:
    return max(game.actions(state), key=lambda a: min_value(game.result(state, a)))


# ______________________________________________________________________________


def expect_minmax(state, game, depth):
    """
    [Figure 5.11]
    Return the best move for a player after dice are thrown. The game tree
	includes chance nodes along with min and max nodes.
	"""
    global d
    d=0
    player = game.to_move(state)
    timer1=time.time()
    def max_value(state):
        global d
        v = -np.inf
        for a in game.actions(state):
            v = max(v, chance_node(state, a))
        d+=1
        return v

    def min_value(state):
        global d
        v = np.inf
        for a in game.actions(state):
            v = min(v, chance_node(state, a))
        d+=1
        return v

    def chance_node(state, action):
        global d
        global timer1
        timer1=time.time()
        res_state = game.result(state, action)
        if game.terminal_test2(res_state, depth, d) == True:
            return game.utility(res_state, player)
        sum_chances = 0
        num_chances = len(game.actions(state))
        for chance in state.moves:
            res_state = game.result(state, chance)
            util = 0
            if res_state.to_move == player:
                util = max_value(res_state)
            else:
                util = min_value(res_state)
            sum_chances += util * game.probability(chance, res_state, player)
        return sum_chances / num_chances

    # Body of expect_minmax:
    return max(game.actions(state), key=lambda a: chance_node(state, a), default=None)



def alpha_beta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""
    timer1=time.time()
    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_search:
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action

def cutoff_test1(state, game, depth):
    global statedepth
    if depth <= statedepth or game.terminal_test(state):  #checks if the depth is reached or the 5 second `
        return True
    return False

def alpha_beta_cutoff_search(state, game, d=4, cutoff_test=cutoff_test1, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    global dd
    dd = d
    player = game.to_move(state)
    global statedepth
    statedepth = 0
    timer1=time.time()
    # Functions used by alpha_beta
    def max_value(state, alpha, beta, depth):
        global statedepth
        global dd
        if cutoff_test1(state,game,dd)==True:
            return eval_fn(state)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        statedepth+=1
        return v

    def min_value(state, alpha, beta, depth):
        global statedepth
        global dd
        if cutoff_test1(state, game, d)==True:
            return eval_fn(state)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        statedepth+=1
        return v

    # Body of alpha_beta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state)))
    cutoff_test = cutoff_test1(state, game, d)
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


# ______________________________________________________________________________
# Players for Games

def query_player(game, state):
    """Make a move by querying standard input."""
    print("current state:")
    game.display(state)
    print("available moves: {}".format(game.actions(state)))
    print("")
    move = None
    if game.actions(state):
        move_string = input('Your move? ')
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print('no legal moves: passing turn to next player')
    return move


def random_player(game, state):
    """A player that chooses a legal move at random."""
    return random.choice(game.actions(state)) if game.actions(state) else None


def alpha_beta_player(game, state):
    return alpha_beta_search(state, game)


def minmax_player(game,state):
    return minmax_decision(state,game)


def expect_minmax_player(game, state):
    return expect_minmax(state, game)


# ______________________________________________________________________________
# Some Sample Games


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


class StochasticGame(Game):
    """A stochastic game includes uncertain events which influence
    the moves of players at each state. To create a stochastic game, subclass
    this class and implement chances and outcome along with the other
    unimplemented game class methods."""

    def chances(self, state):
        """Return a list of all possible uncertain events at a state."""
        raise NotImplementedError

    def outcome(self, state, chance):
        """Return the state which is the outcome of a chance trial."""
        raise NotImplementedError

    def probability(self, chance):
        """Return the probability of occurrence of a chance."""
        raise NotImplementedError

    def play_game(self, *players):
        """Play an n-person, move-alternating stochastic game."""
        state = self.initial
        while True:
            for player in players:
                chance = random.choice(self.chances(state))
                state = self.outcome(state, chance)
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


class Fig52Game(Game):
    """The game represented in [Figure 5.2]. Serves as a simple test case."""

    succs = dict(A=dict(a1='B', a2='C', a3='D'),
                 B=dict(b1='B1', b2='B2', b3='B3'),
                 C=dict(c1='C1', c2='C2', c3='C3'),
                 D=dict(d1='D1', d2='D2', d3='D3'))
    utils = dict(B1=3, B2=12, B3=8, C1=2, C2=4, C3=6, D1=14, D2=5, D3=2)
    initial = 'A'

    def actions(self, state):
        return list(self.succs.get(state, {}).keys())

    def result(self, state, move):
        return self.succs[state][move]

    def utility(self, state, player):
        if player == 'MAX':
            return self.utils[state]
        else:
            return -self.utils[state]

    def terminal_test(self, state):
        return state not in ('A', 'B', 'C', 'D')

    def to_move(self, state):
        return 'MIN' if state in 'BCD' else 'MAX'


class Fig52Extended(Game):
    """Similar to Fig52Game but bigger. Useful for visualisation"""

    succs = {i: dict(l=i * 3 + 1, m=i * 3 + 2, r=i * 3 + 3) for i in range(13)}
    utils = dict()

    def actions(self, state):
        return sorted(list(self.succs.get(state, {}).keys()))

    def result(self, state, move):
        return self.succs[state][move]

    def utility(self, state, player):
        if player == 'MAX':
            return self.utils[state]
        else:
            return -self.utils[state]

    def terminal_test(self, state):
        return state not in range(13)

    def to_move(self, state):
        return 'MIN' if state in {1, 2, 3} else 'MAX'


class TicTacToe(Game):
    """Play TicTacToe on an h x v board, with Max (first player) playing 'X'.
    A state has the player to_move, a cached utility, a list of moves in
    the form of a list of (x, y) positions, and a board, in the form of
    a dict of {(x, y): Player} entries, where Player is 'X' or 'O'."""

    def __init__(self, h=3, v=3, k=3):
        self.h = h
        self.v = v
        self.k = k
        moves = [(x, y) for x in range(1, h + 1)
                 for y in range(1, v + 1)]
        self.initial = GameState(to_move='X', utility=0, board={}, moves=moves)

    def actions(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def result(self, state, move):
        if move not in state.moves:
            return state  # Illegal move has no effect
        board = state.game.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.game
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, board, move, player):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""
        if (self.k_in_row(board, move, player, (0, 1)) or
                self.k_in_row(board, move, player, (1, 0)) or
                self.k_in_row(board, move, player, (1, -1)) or
                self.k_in_row(board, move, player, (1, 1))):
            return +1 if player == 'X' else -1
        else:
            return 0

    def k_in_row(self, board, move, player, delta_x_y):
        """Return true if there is a line through move on board for player."""
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k


class ConnectFour(TicTacToe):
    """A TicTacToe-like game in which you can only make a move on the bottom
    row, or in a square directly above an occupied square.  Traditionally
    played on a 7x6 board and requiring 4 in a row."""

    def __init__(self, h=7, v=6, k=4):
        TicTacToe.__init__(self, h, v, k)

    def actions(self, state):
        return [(x, y) for (x, y) in state.moves
                if x == self.h or (x + 1 , y ) in state.game]

class Gomoku(TicTacToe):
    """Also known as Five in a row."""

    def __init__(self, h=15, v=16, k=5):
        TicTacToe.__init__(self, h, v, k)

class NMensMorris(Game):
    '''
           A simple Gameboard for 9MensMorris game class. This class contains all game specifics logic like
           what next move to take, if a point (completing a row or diagonal or column) been achieved, if
           game is terminated, and so on. For deciding on next move, there are 3 phases to the game:
            •	Placing pieces on vacant points (9 turns each)
            •	Moving placed pieces to adjacent points.
            •	Moving pieces to any vacant point (when the player has been reduced to 3 men)

            This class governs all the logic of the game. This means it has to check validity of each player's
            move, as well as deciding on next move for the AI player. This class receives the game state,
            in form of the list of rows of cells on the board.

        '''
    def __init__(self, h=7, v=7, k=7):
        self.h = h
        self.v = v
        self.k = k
        board = []  # an array of 7 rows, each row an array of element from set {'X', 'O', '-'}.
                    #. 'X' means occupied by Human player, 'O' is occupied by AI, '-' means still vacant
        self.initial = GameState(to_move='X', utility=1, board={}, moves={}, xpos ={}, opos={})

    def actions(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def result(self, state, move):
        if move not in state.moves:
            return state #no effect on illegal moves
        #board = copy.deepcopy(state.board)
        board= state.board.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board,moves = moves, xpos =[], opos=[])

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility

    def is_legal_move(self, board, start, end, player):
        """ can be used to check if a move from start to end positions by player. This function can
        be called for example by get_all_moves() for checking validity of on-board piece moves
        """
        pass

    def get_all_moves(self, state, player):
        """All possible moves for a player. Depending of the state of the game, it can
        include all positions to put a new piece, or all position to move the current pieces.
        The design and format is for students' to do"""
        return state.moves

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""
        global timer1
        timer2 = time.time()
        diff = timer2-timer1
        return diff >=5

    def terminal_test2(self, state, depth1, d):
        """A state is terminal if it is won or there are no empty squares."""
        global timer1
        timer2 = time.time()
        diff = timer2-timer1
        return diff >=5  or depth1 < d

    def terminal_test1(self, state):
        return len(state.moves) == 0 or state.utility !=0

    def display(self, state):
        board = state.game
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, board, move, player):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""
        if (self.k_in_row(board, move, player, (0, 1))or         #checking for one on right
            self.k_in_row(board, move, player, (1, 0))or         #checking for one above
            self.k_in_row(board, move, player, (-1, 0))or        #checking for one on left
            self.k_in_row(board, move, player, (0, -1))):        #checking for on below
            return +1 if player == 'X' else -1
        else:
            return 0

    def probability(self, chance, state, player):
        num1 = 0
        den1 = 1
        num = 0
        den = 1
        if player == 'X':
            for i in range(len(state.xpos)):
                a, b = state.xpos[i]
                c, d = chance
                num1 = 12 - (abs(a - c) + abs(b - d))
                num += num1
                den1 = 12
                den += den1
        else:
            for i in range(len(state.opos)):
                a, b = state.opos[i]
                c, d = chance
                num1 = 12 - (abs(a - c) + abs(b - d))
                den1 = 12
                num += num1
                den += den1
        return num / den

    def k_in_row(self, board, move, player, delta_x_y):
        """Return true if there is a line through move on board for player."""
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k



class Backgammon(StochasticGame):
    """A two player game where the goal of each player is to move all the
	checkers off the board. The moves for each state are determined by
	rolling a pair of dice."""

    def __init__(self):
        """Initial state of the game"""
        point = {'W': 0, 'B': 0}
        board = [point.copy() for index in range(24)]
        board[0]['B'] = board[23]['W'] = 2
        board[5]['W'] = board[18]['B'] = 5
        board[7]['W'] = board[16]['B'] = 3
        board[11]['B'] = board[12]['W'] = 5
        self.allow_bear_off = {'W': False, 'B': False}
        self.direction = {'W': -1, 'B': 1}
        self.initial = StochasticGameState(to_move='W',
                                           utility=0,
                                           board=board,
                                           moves=self.get_all_moves(board, 'W'), chance=None)

    def actions(self, state):
        """Return a list of legal moves for a state."""
        player = state.to_move
        moves = state.moves
        if len(moves) == 1 and len(moves[0]) == 1:
            return moves
        legal_moves = []
        for move in moves:
            board = copy.deepcopy(state.game)
            if self.is_legal_move(board, move, state.chance, player):
                legal_moves.append(move)
        return legal_moves

    def result(self, state, move):
        board = copy.deepcopy(state.game)
        player = state.to_move
        self.move_checker(board, move[0], state.chance[0], player)
        if len(move) == 2:
            self.move_checker(board, move[1], state.chance[1], player)
        to_move = ('W' if player == 'B' else 'B')
        return StochasticGameState(to_move=to_move,
                                   utility=self.compute_utility(board, move, player),
                                   board=board,
                                   moves=self.get_all_moves(board, to_move), chance=None)

    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'W' else -state.utility

    def terminal_test(self, state):
        """A state is terminal if one player wins."""
        return state.utility != 0

    def get_all_moves(self, board, player):
        """All possible moves for a player i.e. all possible ways of
        choosing two checkers of a player from the board for a move
        at a given state."""
        all_points = board
        taken_points = [index for index, point in enumerate(all_points)
                        if point[player] > 0]
        if self.checkers_at_home(board, player) == 1:
            return [(taken_points[0],)]
        moves = list(itertools.permutations(taken_points, 2))
        moves = moves + [(index, index) for index, point in enumerate(all_points)
                         if point[player] >= 2]
        return moves

    def display(self, state):
        """Display state of the game."""
        board = state.game
        player = state.to_move
        print("current state : ")
        for index, point in enumerate(board):
            print("point : ", index, "	W : ", point['W'], "    B : ", point['B'])
        print("to play : ", player)

    def compute_utility(self, board, move, player):
        """If 'W' wins with this move, return 1; if 'B' wins return -1; else return 0."""
        util = {'W': 1, 'B': -1}
        for idx in range(0, 24):
            if board[idx][player] > 0:
                return 0
        return util[player]

    def checkers_at_home(self, board, player):
        """Return the no. of checkers at home for a player."""
        sum_range = range(0, 7) if player == 'W' else range(17, 24)
        count = 0
        for idx in sum_range:
            count = count + board[idx][player]
        return count

    def is_legal_move(self, board, start, steps, player):
        """Move is a tuple which contains starting points of checkers to be
		moved during a player's turn. An on-board move is legal if both the destinations
		are open. A bear-off move is the one where a checker is moved off-board.
        It is legal only after a player has moved all his checkers to his home."""
        dest1, dest2 = vector_add(start, steps)
        dest_range = range(0, 24)
        move1_legal = move2_legal = False
        if dest1 in dest_range:
            if self.is_point_open(player, board[dest1]):
                self.move_checker(board, start[0], steps[0], player)
                move1_legal = True
        else:
            if self.allow_bear_off[player]:
                self.move_checker(board, start[0], steps[0], player)
                move1_legal = True
        if not move1_legal:
            return False
        if dest2 in dest_range:
            if self.is_point_open(player, board[dest2]):
                move2_legal = True
        else:
            if self.allow_bear_off[player]:
                move2_legal = True
        return move1_legal and move2_legal

    def move_checker(self, board, start, steps, player):
        """Move a checker from starting point by a given number of steps"""
        dest = start + steps
        dest_range = range(0, 24)
        board[start][player] -= 1
        if dest in dest_range:
            board[dest][player] += 1
            if self.checkers_at_home(board, player) == 15:
                self.allow_bear_off[player] = True

    def is_point_open(self, player, point):
        """A point is open for a player if the no. of opponent's
        checkers already present on it is 0 or 1. A player can
        move a checker to a point only if it is open."""
        opponent = 'B' if player == 'W' else 'W'
        return point[opponent] <= 1

    def chances(self, state):
        """Return a list of all possible dice rolls at a state."""
        dice_rolls = list(itertools.combinations_with_replacement([1, 2, 3, 4, 5, 6], 2))
        return dice_rolls

    def outcome(self, state, chance):
        """Return the state which is the outcome of a dice roll."""
        dice = tuple(map((self.direction[state.to_move]).__mul__, chance))
        return StochasticGameState(to_move=state.to_move,
                                   utility=state.utility,
                                   board=state.game,
                                   moves=state.moves, chance=dice)

    def probability(self, chance):
        """Return the probability of occurrence of a dice roll."""
        return 1 / 36 if chance[0] == chance[1] else 1 / 18
