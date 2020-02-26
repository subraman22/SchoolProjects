
import time
import math


# Constants for the game environment

ROWS = 6
COLUMNS = 7

PIECE_EMPTY = ' '
PIECE_X = 'X'
PIECE_O = 'O'

DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)


def make_board():
    """
    Creates a 2D list for the board and fills it with empty pieces
    :return: Rows X columns board of empty pieces
    """
    board = []
    for i in range(ROWS):
        row = []
        for j in range(COLUMNS):
            row.append(PIECE_EMPTY)  # fill up the rows with empty spaces
        board.append(row)

    return board


def copy_board(board):
    """
    Returns a deep copy of the board to be used by Minimax
    :param board: board to be copied
    :return: a new, identical board
    """
    new_board = make_board()
    for row in range(ROWS):
        for column in range(COLUMNS):
            new_board[row][column] = board[row][column]

    return new_board


def print_board(board):
    """Prints the board to the screen"""
    for row in board:
        print('|' + '|'.join(row) + '|')


def drop_piece(board, column, piece):
    """
    Attempts to drop the piece in the chosen column and returns boolean whether it did or not
    :param board: active game board
    :param column: column chosen to drop piece in
    :param piece: Piece X or O depending on whose turn it is
    :return: True if piece dropped, False if it fails
    """
    for row in reversed(board):
        if row[column] == PIECE_EMPTY:
            row[column] = piece
            return True

    return False


def find_winner(board, length=4):
    """
    Checks the board for any winning streaks
    :param board: active game board
    :param length: Length of streak searching for. A win is 4 in a row
    :return: None if no winner, or the winning piece if there is one.
    """
    for row in range(ROWS):
        for column in range(COLUMNS):
            if board[row][column] == PIECE_EMPTY:
                continue
            if check_spot(board, row, column, length):
                return board[row][column]
    return None


def full_board(board):
    """
    Checks if the board is full
    :param board: Active game board
    :return: True if board is full, False if it's not
    """
    for row in range(ROWS):
        for column in range(COLUMNS):
            if board[row][column] == PIECE_EMPTY:
                return False
    return True


def check_spot(board, row, column, length):
    """
    Checks a spot for a specified chain length in all directions
    :param board: Active game board
    :param row: row of the piece to check
    :param column: column of the piece to check
    :param length: desired chain length
    :return: True if the piece is part of chain of specified length, False otherwise
    """
    for vertical, horizontal in DIRECTIONS:
        found_chain = True

        for i in range(1, length):  # checking length # of spots in every direction
            r = row + vertical * i
            c = column + horizontal * i

            if r not in range(ROWS) or c not in range(COLUMNS):  # no winner if the spot isn't on the board
                found_chain = False
                break

            if board[r][c] != board[row][column]:  # not a winner if the consecutive pieces are not identical
                found_chain = False
                break

        if found_chain:
            return True

    return False


def check_spot_unblocked(board, row, column, length):
    """
    Modified version of check_spot that checks a spot beyond. Only returns true if the chain has a possibility of
    extending
    :param board: Active game board
    :param row: row of the piece to check
    :param column: column of the piece to check
    :param length: desired chain length
    :return: True if the piece is part of UNBLOCKED chain of specified length, False otherwise
    """
    for vertical, horizontal in DIRECTIONS:
        found_chain = True

        for i in range(1, length):  # checking length # of spots in every direction
            r = row + vertical * i
            c = column + horizontal * i

            if r not in range(ROWS) or c not in range(COLUMNS):  # no winner if the spot isn't on the board
                found_chain = False
                break

            if board[r][c] != board[row][column]:  # not a winner if the consecutive pieces are not identical
                found_chain = False
                break

        next_row = row + (vertical * (length))
        next_col = column + (horizontal * (length))
        if next_row not in range(ROWS) or next_col not in range(COLUMNS):
            found_chain = False

        elif board[next_row][next_col] != PIECE_EMPTY:
            found_chain = False

        if found_chain:
            return True

    return False


def human_player():
    """Reads move from a human player and drops a piece in the specified column"""
    column_number = -1

    while column_number not in range(0, COLUMNS):
        try:
            column_input = input('Which column (0-6)? ')
            column_number = int(column_input)
        except ValueError:
            print("Input must be an integer, please try again")

    return column_number


def ai_player(board, depth, max_player):
    """AI player that utilizes alpha_beta function to choose the best column"""
    best_move, column = alpha_beta(board, depth, -math.inf, math.inf, max_player)
    return column


def alpha_beta(board, depth, alpha, beta, max_player):
    """
    Minimax algorithm with alpha-beta pruning to decide which move is the best.
    :param board: active game board
    :param depth: number of moves to look ahead
    :param alpha: high cutoff for maximizing player
    :param beta: low cutoff for minimizing player
    :param max_player: True if maximizing player, False if minimizing player
    :return: Tuple of value, column for the best move possible and the column for that move
    """
    if find_winner(board) is not None or depth == 0:  # base case for cutting off and terminal nodes
        return heuristic(board), -1  # return -1 for column because we don't care about making a move in this case
    if max_player:
        column = -1
        val = -math.inf
        children = generate_children(board, max_player)
        for child in children:
            if child[1] is None:  # skip non-existent children.
                continue
            child_val, child_column = alpha_beta(child[1], depth - 1, alpha, beta, False)
            if child_val > val:
                val = child_val
                column = child[0]
            alpha = max(alpha, val)
            if alpha >= beta:
                break

    else:  # same code, but for minimizing player. Chooses the minimum value, and modifies beta.
        column = -1
        val = math.inf
        children = generate_children(board, max_player)
        for child in children:
            if child[1] is None:
                continue
            child_val, child_column = alpha_beta(child[1], depth - 1, alpha, beta, True)
            if child_val < val:
                val = child_val
                column = child[0]
            beta = min(beta, val)
            if alpha >= beta:
                break
    return val, column


def generate_children(board, max_player):
    """
    Creates a list of all possible children and the move that leads to that child. Children are deep copies
    using the copy_board function
    :param board: initial board before making moves
    :param max_player: Boolean for whose turn it is. True is X, False is O
    :return:
    """
    children = []
    if max_player:
        piece = PIECE_X
    else:
        piece = PIECE_O
    for i in range(COLUMNS):
        new_board = copy_board(board)
        if drop_piece(new_board, i, piece):
            children.append((i, new_board))
        else:
            children.append((i, None))  # if the move doesn't result in a valid child, return None for the board
    return children


def heuristic(board):
    """
    Heuristic function to evaluate how close a state is to the goal state. If there is a winner, it assigns +/- 10,000
    for a victory depending on who wins. Otherwise it loops through the board and checks each piece for chains of 2 and
    3. Chains of 3 are worth much more than chains of 2. This simple heuristic counts each streak multiple times
    :param board:
    :return:
    """
    h = 0
    col_weight = 1
    winner = find_winner(board)
    if winner is not None:
        if winner == PIECE_X:
            h = 10000
            return h
        else:
            h = -10000
            return h

    for row in range(ROWS):
        for col in range(COLUMNS):
            if board[row][col] == PIECE_EMPTY:
                continue
            if board[row][col] == PIECE_X:
                sign = 1
            else:
                sign = -1

            if check_spot_unblocked(board, row, col, 3):
                h += sign * col_weight * 500
            if check_spot_unblocked(board, row, col, 2):
                h += sign * col_weight * 50
    return h


if __name__ == '__main__':
    Players = (PIECE_X, PIECE_O)
    History = []
    Board = make_board()
    Winner = None
    Tries = 0
    Depth = 6

    print_board(Board)

    # Game Loop

    while not Winner:
        turn = len(History)

        if turn % 2 == 0:
            # print_board(Board)
            move = human_player()   # Player One
        else:
            move = ai_player(Board, 2, False)  # Player Two

        if drop_piece(Board, move, Players[turn % 2]):
            Tries = 0
            History.append(move)

        else:
            Tries += 1
            print("Column is full. Try again")

        if Tries > 3:
            print('Player {} is stuck!'.format((turn % 2) + 1))
            break

        print_board(Board)

        if full_board(Board):
            print("Board is full. Draw")
            break

        print(heuristic(Board))

        time.sleep(1)

        Winner = find_winner(Board)

    if heuristic(Board) == 10000:  # Piece X, human player wins
        print("Game over. You win!")

    elif heuristic(Board) == -10000:  # Piece O, computer AI wins
        print("Game over. Computer wins.")



