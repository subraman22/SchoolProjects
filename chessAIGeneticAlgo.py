# CS 5100
# Author: Rajesh Sakhamuru, Rohan Subramaniam
# Version: 12/13/2019

from copy import deepcopy
from math import sqrt
from random import randint
from random import random

# based on https://repl.it/@f9we/chess


################################################################################
# Chess Using Turtle Graphics.
################################################################################
class Chess:
    """Plays Chess Game. This initializes what needs to be done. However it is
    in the Input class that deals with driving the game.
    
    Attributes:
        board: Object of ChessBoard.
        pen: Pen to Turtle.
        piece: Object of ChessPiece.
        update: Update the screen after disabling tracer for faster draw.
        user_input: Object of Input.
        window: Turtle Screen used for Input class to hook the mouse.
        mouse_x: x of mouse. If None, then haven't done anything yet.
        mouse_y: y of mouse. If None, then haven't done anything yet.
    """
    SQUARE_SIZE = 50  # ULTIMATELY DECIDES ON SIZE OF EVERYTHING (Lowest is 30)

    def __init__(self):
        import turtle
        self.pen = turtle.Turtle()
        self.window = turtle.Screen()
        self.window.colormode(255)
        self.board = ChessBoard(self.pen, Chess.SQUARE_SIZE)
        self.piece = ChessPiece(self.board)
        self.update = turtle.update
        print("Please click anywhere on the board to begin\nGenetic Algorithm optimization of chess heuristic.")
        self.user_input = Input(self.board, self.piece, self.window,
                                self.update)
        turtle.tracer(0, 0)
        self.pen.speed(0)
        self.pen.ht()
        self.pen.pensize(.5)

    def _select_piece(self, row, col):
        self.board.select_piece(row, col)
        self.update()

    def _move_piece(self, frow, fcol, trow, tcol):
        self.board.move_piece(frow, fcol, trow, tcol)
        self.update()

    def run(self):
        self.board.draw_board()
        self.piece.start_at_beginning()
        self.update()

        # Listen for mouse clicks.
        self.window.listen()
        self.window.mainloop()


################################################################################
class ChessBoard:
    """Handles anything related to the chess board.
    
    Attributes:
        # Turtle Graphics Ability to Draw
        pen: Turtle pen.

        # Colors
        border_color: Oak Brown (128, 101, 23).
        select_color: Blue (0, 0, 255).
        not_select_color: Black (0, 0, 0)
        square_dark: Off Red (188, 23, 15).
        square_light: White (255, 255, 255).

        # Dimensions
        border_size: Size of the border.
        board_size: Size of the chess board (apart from border).
        board_top_y: Top y of chess board (apart from border).
        board_lft_x: Left x of chess board (apart from border).
        next_square: Amount for next square (horizontal or veritcal).
        square_side_size: Size of each individual side of a square on board.

        # Piece to Board DataStructure.
        squares: 2 dimensional list representing each square on board.
                       1st dimensional
                         0
                         1
                         2
                         3
                         4
                         5
                         6
                         7
                           0 1 2 3 4 5 6 7 2nd dimension
    """

    def __init__(self, pen, square_side_size, squares=None):
        """Inits chess board attributes.
        
        Args:
            pen: Object of turtle pen.
            square_side_size: Integer representing side of square.
            squares: If pass, setup board with particular setup.
                           This could be used for testing or for practice.
            board_top_y: Chess Board top y coord.
            board_lft_x: Chess Board left x coord.
        """
        self.border_color = (128, 101, 23)
        self.square_dark = (188, 100, 75)
        self.square_light = (255, 255, 255)
        self.not_select_color = (0, 0, 0)
        self.select_color = (0, 0, 255)
        self.pen = pen
        self.next_square = square_side_size + 1
        self.board_side = square_side_size * 8 + 7
        self.board_top_y = self.next_square * 4
        self.board_lft_x = self.next_square * -4
        self.square_side_size = square_side_size
        self.border_size = square_side_size * 1.2
        if squares is not None:
            self.squares = squares
        else:
            self.squares = [[None for _ in range(8)] for _ in range(8)]

    def deep_copy(self):

        squares_copy = [deepcopy(l) for l in deepcopy(self.squares)]
        copy = ChessBoard(self.pen, self.square_side_size, squares=squares_copy)
        return copy

    def print_board(self):

        count = 0
        print("\n    0____1_____2_____3_____4____5_____6_____7")
        for r in self.squares:
            print(count, end=":")
            print(r)
            count += 1
        print("---------------")
        return

    def _draw_square(self, left_x, top_y, side, color, fill):
        """Draws a square at a given row, col on board.
        
        Args:
            left_x: Left x of square.
            top_y: Top y of square.
            side: Square side.
            color: Color tuple (r,g,b).
            fill: True if fill.
        """
        self.pen.up()
        self.pen.color(color)
        self.pen.goto(left_x, top_y)
        self.pen.down()
        self.pen.begin_fill()
        for _ in range(4):
            self.pen.forward(side)
            self.pen.right(90)
        self.pen.end_fill()

    def _goto_piece_xy(self, row, col, adjustment_x=0, adjustment_y=0):
        """Goto x,y based upon row,col to display piece.
        
        Args:
            row: 1st dimension.
            col: 2nd dimension.
            adjustment_x: Fraction * square_side_size added to x.
        """
        self.pen.up()
        x = (self.board_lft_x + col * (self.next_square) +
             self.square_side_size * .05) + adjustment_x * self.square_side_size
        y = (self.board_top_y - row * (self.next_square) -
             self.square_side_size * .8) - adjustment_y * self.square_side_size
        self.pen.goto(x, y)

    def _put_chr_at(self, char, row, col, color, adjustment_x=.19, adjustment_y=.19):
        """Put piece on chess board or notation on border.
        
        Args:
            char: Unicode of char.
            row: 1st dimension location.
            col: 2nd dimension location.
            adjustment_x: Fraction * square_side_size added to x. (text)
        """
        self._goto_piece_xy(row, col, adjustment_x, adjustment_y)
        self.pen.color(color)
        self.pen.write(char, font=("Courier", round(self.square_side_size * .7),
                                   "normal"))

    def xy_to_rowcol(self, x, y):
        """Convert x,y to row,col on chess board.
        
        Args:
            x: x location.
            y: y location.
            
        Returns:
            List [row, col].
        """
        col = int((x - self.board_lft_x) / self.next_square)
        row = int((self.board_top_y - y) / self.next_square)
        return [row, col]

    def overwrite_board_square(self, row, col):
        """Overwrite board with new square.
        
        Args:
            row: Row of board, 0-7 from top to bottom.
            col: Col of board, 0-7 from left to right.
        """
        x = self.board_lft_x + col * self.next_square
        y = self.board_top_y - row * self.next_square
        color = self.square_light if (row + col) % 2 == 0 else self.square_dark
        self._draw_square(x, y, self.square_side_size, color, True)

    def put_piece(self, piece, row, col):
        """Put piece on chess board.
        
        Args:
            piece: Unicode of chess piece.
            row: 1st dimension location.
            col: 2nd dimension location.
        """
        self.squares[row][col] = piece
        self._put_chr_at(piece, row, col, self.not_select_color)

    def draw_board(self):
        """Draws border and board. No pieces are drawn."""
        # Clears screen of all turtle drawings
        self.pen.clear()

        # Draw border and fill everything.
        self._draw_square(self.board_lft_x - self.border_size,
                          self.board_top_y + self.border_size,
                          self.board_side + 2 * self.border_size,
                          self.border_color, True)

        # Draw white squares of board.
        self._draw_square(self.board_lft_x, self.board_top_y,
                          self.board_side, self.square_light, True)

        # Draw dark squares of board.
        #   Automatically add a square side to x.
        #   Subtract that square side when row is odd.
        for row in range(8):
            x = self.board_lft_x + self.next_square - row % 2 * self.next_square
            y = self.board_top_y - row * self.next_square
            for col in range(4):
                self._draw_square(x, y, self.square_side_size, self.square_dark,
                                  True)
                x += 2 * self.next_square

        # Draw Notation 1-8 on border.
        for row in range(8):
            self._put_chr_at(chr(ord(str(8 - row))), row, -1, (0, 0, 0))

        # Draw Notation a-h on border.
        for col in range(8):
            self._put_chr_at(chr(ord('a') + col), 8, col, (0, 0, 0))

        # Draw White Turn.
        self._put_chr_at("Turn: White", 9, 1, (0, 0, 0))

    def move_piece(self, from_row, from_col, to_row, to_col):
        """Move from row,col to row,col.
        
        If there is no piece at from location, do nothing.
        Does not validate moves.
        
        Args:
            from_row: from 1st dimension.
            from_col: from 2nd dimension.
            to_row: to 1st dimension.
            to_col: to 2nd dimension.
            
        Returns:
            False there was no piece at location.
        """
        # Get piece from-square
        piece = self.squares[from_row][from_col]

        # overwrite from-square and update board to relect nothing.
        self.squares[from_row][from_col] = None
        self.overwrite_board_square(from_row, from_col)

        # Overwrite to-square (including any pieces taken).
        self.overwrite_board_square(to_row, to_col)
        self.put_piece(piece, to_row, to_col)
        self.squares[to_row][to_col] = piece

        return True

    def select_piece(self, row, col):
        """Select piece at row, col and highlight it to a different color.
        
        Args:
            row: Row 1-8 on board of piece.
            col: Col a-h on board of piece.
            
        Returns:
            A string representing the piece selected.
            None is returned if there is no piece at first selection or unselection.
        """
        piece = self.squares[row][col]
        if piece != None:
            self._put_chr_at(piece, row, col, self.select_color)
        return piece

    def unselect_piece(self, row, col):
        """Unselect piece that was previously selected.
        
        Args:
            row: Row wanting to unselect.
            col: Col wanting to unselect.
        """
        piece = self.squares[row][col]
        self.overwrite_board_square(row, col)
        self._put_chr_at(piece, row, col, self.not_select_color)


################################################################################
class ChessPiece:
    """Checks valid moves of pieces."""
    W_KING = u'♔'
    W_QUEEN = u'♕'
    W_ROOK = u'♖'
    W_BISHOP = u'♗'
    W_KNIGHT = u'♘'
    W_PAWN = u'♙'
    B_KING = u'♚'
    B_QUEEN = u'♛'
    B_ROOK = u'♜'
    B_BISHOP = u'♝'
    B_KNIGHT = u'♞'
    B_PAWN = u'♟'

    def __init__(self, chess_board, moveHistory=None, blackCanCastleQside=True, blackCanCastleKside=True,
                 whiteCanCastleQside=True, whiteCanCastleKside=True, testing=False):
        """Inits attributes.
        
        Args:
            chess_board: Object of ChessBoard.
        """
        import turtle

        self.board = chess_board

        # move history
        self.moveHistory = [(None, 0, 0, 0, 0)]

        # TODO castling (False after associated King or Rook moves)
        self.blackCanCastleQside = blackCanCastleQside
        self.blackCanCastleKside = blackCanCastleKside
        self.whiteCanCastleQside = whiteCanCastleQside
        self.whiteCanCastleKside = whiteCanCastleKside

        # prevents rook-castling and en passant if just checking validity of moves
        # set to True if just testing validity
        self.testing = testing

        # Take user input for pawn promotion
        self.window = turtle.Screen()
        self.update = turtle.update
        self.user_input = Input(self.board, self, self.window, self.update)

    def deep_copy(self, testing=False):
        board_copy = self.board.deep_copy()
        history_copy = [deepcopy(l) for l in deepcopy(self.moveHistory)]
        copy = ChessPiece(board_copy, moveHistory=history_copy,
                          blackCanCastleQside=self.blackCanCastleQside,
                          blackCanCastleKside=self.blackCanCastleKside,
                          whiteCanCastleQside=self.whiteCanCastleQside,
                          whiteCanCastleKside=self.whiteCanCastleKside, testing=testing)
        return copy

    def start_at_beginning(self):
        """Draw pieces at the beginning of game."""
        b_pieces = [ChessPiece.B_ROOK,
                    ChessPiece.B_KNIGHT,
                    ChessPiece.B_BISHOP,
                    ChessPiece.B_QUEEN,
                    ChessPiece.B_KING,
                    ChessPiece.B_BISHOP,
                    ChessPiece.B_KNIGHT,
                    ChessPiece.B_ROOK]
        w_pieces = [ChessPiece.W_ROOK,
                    ChessPiece.W_KNIGHT,
                    ChessPiece.W_BISHOP,
                    ChessPiece.W_QUEEN,
                    ChessPiece.W_KING,
                    ChessPiece.W_BISHOP,
                    ChessPiece.W_KNIGHT,
                    ChessPiece.W_ROOK]

        for i in range(8):
            self.board.put_piece(b_pieces[i], 0, i)
            self.board.put_piece(ChessPiece.B_PAWN, 1, i)
            self.board.put_piece(w_pieces[i], 7, i)
            self.board.put_piece(ChessPiece.W_PAWN, 6, i)

    def piece_color(self, piece):
        """Tells the color of the piece.
        
        Args:
            piece: The unicode of the piece.
            
        Returns:
            "white" is returned for white and "black" for black pieces.
            None is returned for blank piece.
        """
        if piece == None:
            return None
        if ord(ChessPiece.W_KING) <= ord(piece) <= ord(ChessPiece.W_PAWN):
            return "white"
        return "black"

    def _is_taking_own_piece(self, from_row, from_col, to_row, to_col):
        """Trying to take own piece?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if trying to take own piece.
        """
        # Get piece being moved
        piece = self.board.squares[from_row][from_col]
        piece_color = self.piece_color(piece)

        # is piece trying to take it's own piece?
        to_piece = self.board.squares[to_row][to_col]
        if to_piece != None:
            if self.piece_color(to_piece) == piece_color:
                return True
        return False

    def _any_piece_in_way(self, from_row, from_col, dr, dc, dm, toRow=None, toCol=None):
        """Is any pieces are in the way for bishop or rook like moves?
        
        NOTE: If only moving one, than assume piece is not same piece
        so assume can move there.
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            dr: amount to change row
            dc: amount to change col
            dm: amount to move

        Return:
            True if valid move.
        """
        if toRow != None and toCol != None and (toRow == from_row):
            colDiff = abs(toCol - from_col)
            for i in range(1, colDiff):
                if self.board.squares[from_row][from_col + i * dc] != None:
                    return False

            pass

        for i in range(1, dm):
            if self.board.squares[from_row + i * dr][from_col + i * dc] != None:
                return False
        return True

    def is_rook_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a rook?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """
        # if not on same column or row
        if ((from_row != to_row and from_col != to_col) or
            (from_row == to_row and from_col == to_col)):
            return False

        # check if any pieces are in the way of destination
        if from_row != to_row:
            dc = 0
            dr = 1 if to_row - from_row > 0 else -1
        if from_col != to_col:
            dr = 0
            dc = 1 if to_col - from_col > 0 else -1
        dm = abs(to_row - from_row)

        retVal = self._any_piece_in_way(from_row, from_col, dr, dc, dm, toRow=to_row, toCol=to_col)

        # Casting: Rook invalidation
        if retVal and (from_row == 0 or from_row == 7):
            piece = self.board.squares[from_row][from_col]
            piece_color = self.piece_color(piece)
            if piece_color == "white":
                if from_col == 0:
                    self.whiteCanCastleQside = False
                elif from_col == 7:
                    self.whiteCanCastleKside = False
            else:
                if from_col == 0:
                    self.blackCanCastleQside = False
                elif from_col == 7:
                    self.blackCanCastleKside = False

        return retVal

    def is_knight_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a knight?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """
        # check for valid move
        if ((abs(from_row - to_row) == 1 and abs(from_col - to_col) == 2) or
            (abs(from_row - to_row) == 2 and abs(from_col - to_col) == 1)):
            return True
        return False

    def is_bishop_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a bishop?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """
        # if not on same colored diagonal exit.
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False

        # check if any pieces are in the way of destination
        dr = 1 if to_row - from_row > 0 else -1
        dc = 1 if to_col - from_col > 0 else -1
        dm = abs(to_row - from_row)
        return self._any_piece_in_way(from_row, from_col, dr, dc, dm)

    def is_queen_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a queen?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """
        # if not on same colored diagonal
        if abs(from_row - to_row) != abs(from_col - to_col):
            # if on same col? (like rook)
            if from_row != to_row and (from_col == to_col):
                dc = 0
                dr = 1 if to_row - from_row > 0 else -1
            # elif on same row?
            elif from_col != to_col and (from_row == to_row):
                dr = 0
                dc = 1 if to_col - from_col > 0 else -1
            else:
                # if not on same col or row
                return False
        else:
            # on same colored diagonal (moves like bishop)
            dr = 1 if to_row - from_row > 0 else -1
            dc = 1 if to_col - from_col > 0 else -1

        # check if any pieces are in the way of destination
        dm = abs(to_row - from_row)
        return self._any_piece_in_way(from_row, from_col, dr, dc, dm, toRow=to_row, toCol=to_col)

    def is_king_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a king?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """

        piece = self.board.squares[from_row][from_col]
        piece_color = self.piece_color(piece)

        if abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1:
            if piece_color == "white":
                self.whiteCanCastleKside = False
                self.whiteCanCastleQside = False
            else:
                self.blackCanCastleKside = False
                self.blackCanCastleQside = False
            return True

        # TODO Castling implementation
        # if king and rook have not been moved yet this game, and no space between
        # the king and the rook are occupied or threatened, then the king can
        # move 2 spaces towards the rook, and the rook will be placed adjacent to the
        # king on the side closer to the center column.

        # TODO need function which returns squares being threatened which takes a piece position and board as a param

        if (piece_color == "white"):
            if self.whiteCanCastleKside and (from_row == 7 and from_col == 4) and (to_row == from_row) and (to_col == 6):
                # White kingside Castle
                if (self.board.squares[7][5] == None and self.board.squares[7][6] == None):
                    if not self.testing:
                        self.whiteCanCastleKside = False
                        self.whiteCanCastleQside = False
                        self.board.move_piece(7, 7, 7, 5)
                    return True

            if self.whiteCanCastleQside and (from_row == 7 and from_col == 4) and (to_row == from_row) and (to_col == 2):
                # White queenside Castle
                if (self.board.squares[7][3] == None and self.board.squares[7][2] == None and self.board.squares[7][1] == None):

                    if not self.testing:
                        self.whiteCanCastleKside = False
                        self.whiteCanCastleQside = False
                        self.board.move_piece(7, 0, 7, 3)
                    return True

        elif piece_color == "black":
            if self.blackCanCastleKside and (from_row == 0 and from_col == 4) and (to_row == from_row) and (to_col == 6):
                # black kingside Castle
                if (self.board.squares[0][5] == None and self.board.squares[0][6] == None):
                    if not self.testing:
                        self.blackCanCastleKside = False
                        self.blackCanCastleQside = False
                        self.board.move_piece(0, 7, 0, 5)
                    return True

            if self.blackCanCastleQside and (from_row == 0 and from_col == 4) and (to_row == from_row) and (to_col == 2):
                # black queenside Castle
                if (self.board.squares[0][3] == None and self.board.squares[0][2] == None and self.board.squares[0][1] == None):
                    if not self.testing:
                        self.blackCanCastleKside = False
                        self.blackCanCastleQside = False
                        self.board.move_piece(0, 0, 0, 3)
                    return True

        return False

    def promotion_onClick(self, x, y):

        promotionFlag = False

        side = self.board.square_side_size
        left_x = (side * .84)
        top_y = side * 6.7

        # black or white piece to promote
        shift = 0
        promoteTo = ['♘', '♗', '♖', '♕', '♞', '♝', '♜', '♛']
        to_row = self.moveHistory[-1][3]
        to_col = self.moveHistory[-1][4]

        # left edge of square to pick piece
        knight = (left_x)
        bishop = (left_x + (side * 1.1))
        rook = (left_x + (side * 1.1 * 2))
        queen = (left_x + (side * 1.1 * 3))

        if x < left_x or x > (queen + side) or y > top_y or y < (top_y - side):
            return

        if ((knight + side) < x < bishop) or ((bishop + side) < x < rook) \
            or ((rook + side) < x < queen):
            return

        if self.moveHistory[-1][0] == "♟":
            shift = 4

        # Promote pawn to knight
        if (knight < x < (knight + side)) and (top_y > y > (top_y - side)):
            self.board.overwrite_board_square(to_row, to_col)
            self.board.put_piece(promoteTo[0 + shift], to_row, to_col)
            promotionFlag = True

        # Promote pawn to bishop
        elif (bishop < x < (bishop + side)) and (top_y > y > (top_y - side)):
            self.board.overwrite_board_square(to_row, to_col)
            self.board.put_piece(promoteTo[1 + shift], to_row, to_col)
            promotionFlag = True

        # Promote pawn to rook
        elif (rook < x < (rook + side)) and (top_y > y > (top_y - side)):
            self.board.overwrite_board_square(to_row, to_col)
            self.board.put_piece(promoteTo[2 + shift], to_row, to_col)
            promotionFlag = True

        # Promote pawn to queen
        elif (queen < x < (queen + side)) and (top_y > y > (top_y - side)):
            self.board.overwrite_board_square(to_row, to_col)
            self.board.put_piece(promoteTo[3 + shift], to_row, to_col)
            promotionFlag = True

        if promotionFlag:

            # clears piece selection menu
            self.board._draw_square(side * -6.5, side * 17.5, side * 12, (255, 255, 255), True)

            # Makes the program go back to taking user input for piece movement
            self.user_input.turn_color = "white" if self.moveHistory[-1][0] == "♟" else "black"
            self.window.onclick(self.user_input.onclick)

        return

    def pawn_promotion(self, to_row, to_col, piece_color):

        # If pawn moves to last row, it can become a knight, bishop, rook or queen.
        # Need to let the user choose.

        promoteTo = ['♘', '♗', '♖', '♕', '♞', '♝', '♜', '♛']

        if to_row == 0 or to_row == 7:

            for n in range(4):
                self.board._draw_square(self.board.square_side_size * .84 + (self.board.square_side_size \
                    +(.1 * self.board.square_side_size)) * n, self.board.square_side_size * 6.7, \
                    self.board.square_side_size, self.board.square_dark, True)
            if to_row == 0:
                for n in range(4):
                    self.board._put_chr_at(promoteTo[n], -2.5, 5 + (n + (n * .09)), (0, 0, 0), adjustment_x=0)
            elif to_row == 7:
                for n in range(4):
                    self.board._put_chr_at(promoteTo[n + 4], -2.5, 5 + (n + (n * .09)), (0, 0, 0), adjustment_x=0)

            self.board._put_chr_at("Promote Pawn:", -2.5, -2.5, (0, 0, 0))

            self.window.onclick(self.promotion_onClick)

        return

    def is_pawn_move_valid(self, from_row, from_col, to_row, to_col):
        """Is move valid for a pawn?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.

        Return:
            True if valid move.
        """
        # Setup variables used
        piece = self.board.squares[from_row][from_col]
        piece_color = self.piece_color(piece)
        to_piece = self.board.squares[to_row][to_col]
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        dc = 0

        # Set flag for first move of pawn
        first_move = True if from_row == 6 or from_row == 1 else False

        # If direction is not correct for white, exit
        if to_row - from_row > 0:
            dr = 1
            if self.piece_color(piece) == "white":
                return False

        # If direction is not correct for black, exit
        if to_row - from_row < 0:
            dr = -1
            if self.piece_color(piece) == "black":
                return False

        # If moving straight
        if from_col == to_col:
            # if not legal straight move, exit
            if not (row_diff == 1 or (first_move and row_diff == 2)):
                return False

            # make sure to move has no pieces on straight path
            dm = row_diff + 1

            # return value
            retVal = self._any_piece_in_way(from_row, from_col, dr, dc, dm)

#             if retVal and not self.testing:
# #                 self.pawn_promotion(to_row, to_col, piece_color)
#                 self.board.overwrite_board_square(to_row, to_col)
#                 if piece_color == "black":
#                     self.board.put_piece(self.B_QUEEN, to_row, to_col)
#                 else:
#                     self.board.put_piece(self.W_QUEEN, to_row, to_col)

            return retVal

        # WHITE en passant
        # move from moveHistory => ("piece", fromRow, fromCol, toRow, toCol)
        if (self.moveHistory[-1][2] == self.moveHistory[-1][4] == (to_col)) and \
            self.moveHistory[-1][0] == "♟" and self.moveHistory[-1][1] == 1 and\
            self.moveHistory[-1][3] == 3 and piece_color == "white":
            if col_diff == 1 and row_diff == 1 and to_piece == None:
                if not self.testing:
                    self.board.overwrite_board_square(self.moveHistory[-1][3], self.moveHistory[-1][4])
                    self.board.squares[self.moveHistory[-1][3]][self.moveHistory[-1][4]] = None
                return True

        # BLACK en passant
        if (self.moveHistory[-1][2] == self.moveHistory[-1][4] == (to_col)) and \
            self.moveHistory[-1][0] == "♙" and self.moveHistory[-1][1] == 6 and\
            self.moveHistory[-1][3] == 4 and piece_color == "black":
            if col_diff == 1 and row_diff == 1 and to_piece == None:
                if not self.testing:
                    self.board.overwrite_board_square(self.moveHistory[-1][3], self.moveHistory[-1][4])
                    self.board.squares[self.moveHistory[-1][3]][self.moveHistory[-1][4]] = None
                return True

        # else move must be taking piece directly move
        # if legal taking piece move and (opponent-already check for own piece) piece at to-square
        if col_diff == 1 and row_diff == 1 and to_piece != None:

#             if not self.testing:
# #                 self.pawn_promotion(to_row, to_col, piece_color)
#                 self.board.overwrite_board_square(to_row, to_col)
#                 if piece_color == "black":
#                     self.board.put_piece(self.B_QUEEN, to_row, to_col)
#                 else:
#                     self.board.put_piece(self.W_QUEEN, to_row, to_col)
            return True

        return False

    def is_move_valid(self, from_row, from_col, to_row, to_col):
        """Is the piece attempting to move from - to valid?
        
        Args:
            from_row: row of source square.
            from_col: col of source square.
            to_row: row of destination square.
            to_col: col of destination square.
            
        Return:
            True if valid move.
        """
        # check is taking own piece?
        if self._is_taking_own_piece(from_row, from_col, to_row, to_col):
            return False

        piece = self.board.squares[from_row][from_col]
        if piece == ChessPiece.W_ROOK or piece == ChessPiece.B_ROOK:
            return self.is_rook_move_valid(from_row, from_col,
                                              to_row, to_col)
        if piece == ChessPiece.W_KNIGHT or piece == ChessPiece.B_KNIGHT:
            return self.is_knight_move_valid(from_row, from_col,
                                              to_row, to_col)
        if piece == ChessPiece.W_BISHOP or piece == ChessPiece.B_BISHOP:
            return self.is_bishop_move_valid(from_row, from_col,
                                              to_row, to_col)
        if piece == ChessPiece.W_QUEEN or piece == ChessPiece.B_QUEEN:
            return self.is_queen_move_valid(from_row, from_col,
                                             to_row, to_col)
        if piece == ChessPiece.W_KING or piece == ChessPiece.B_KING:
            return self.is_king_move_valid(from_row, from_col,
                                            to_row, to_col)
        if piece == ChessPiece.W_PAWN or piece == ChessPiece.B_PAWN:
            return self.is_pawn_move_valid(from_row, from_col,
                                            to_row, to_col)


class Threat:
    """
    Calculates which spaces are threatened by each piece
    Stores each player's threat and moves separately
    """

    def __init__(self, chess_board, pieces, testing=False):
        self.whiteThreat = {}
        self.blackThreat = {}
        self.blackMoves = []
        self.whiteMoves = []
        self.board = chess_board
        self.pieces = pieces
        self.pieces.testing = testing

    def pawnThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that a specific pawn is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of a pawn to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """

        if color == "black":
            direc = 1
            boardThreat = self.blackThreat
        else:
            direc = -1
            boardThreat = self.whiteThreat

        # Pawn Promotion is automatically changed to a Queen
        if fromRow == 0 or fromRow == 7:
            self.queenThreat(color, fromRow, fromCol)
            return

        # All spots that are threatened by pieces
        threatList = []
        # The list of all possible moves
        moveList = []

        # If it's the left column, it can only go diagonal right
        if fromCol == 0:
            toCol = 1
            toRow = fromRow + direc
            threatList.append((toRow, toCol))
            if self.pieces.piece_color(self.board.squares[toRow][toCol]) != color \
                    and self.pieces.piece_color(self.board.squares[toRow][toCol]) != None:
                moveList.append((toRow, toCol))

        # If it's in the right column, it can only go diagonal left
        elif fromCol == 7:
            toCol = 6
            toRow = fromRow + direc
            threatList.append((toRow, toCol))
            if self.pieces.piece_color(self.board.squares[toRow][toCol]) != color \
                    and self.pieces.piece_color(self.board.squares[toRow][toCol]) != None:
                moveList.append((toRow, toCol))

        # Otherwise the pawn can threaten diagonally both directions
        else:
            toCol1 = fromCol - 1
            toCol2 = fromCol + 1
            toRow = fromRow + direc
            threatList.append((toRow, toCol1))
            threatList.append((toRow, toCol2))
            if self.pieces.piece_color(self.board.squares[toRow][toCol1]) != color \
                    and self.pieces.piece_color(self.board.squares[toRow][toCol1]) != None:
                moveList.append((toRow, toCol1))
            if self.pieces.piece_color(self.board.squares[toRow][toCol2]) != color \
                    and self.pieces.piece_color(self.board.squares[toRow][toCol2]) != None:
                moveList.append((toRow, toCol2))

        # For pawn's first move, adds both spaces in front to the move list
        # Not added to threat because pawns can't kill in front
        if (fromRow == 1 and color == "black") or (fromRow == 6 and color == "white"):
            if self.board.squares[fromRow + direc][fromCol] == None:
                moveList.append((fromRow + direc, fromCol))
                if self.board.squares[fromRow + (direc * 2)][fromCol] == None:
                    moveList.append((fromRow + (direc * 2), fromCol))
        else:  # Otherwise just the one space in front
            if self.board.squares[fromRow + direc][fromCol] == None:
                moveList.append((fromRow + direc, fromCol))

        # Amends the boardThreat dictionary count of threatened spaces or adds it to the dictionary
        for move in threatList:
            if (move[0], move[1]) not in boardThreat.keys():
                boardThreat[(move[0], move[1])] = 1
            else:
                boardThreat[(move[0], move[1])] += 1

        # Adds possible move to move list if the pawn is not blocked without adding to threat
        for move in moveList:
            if self.pieces.piece_color(self.board.squares[move[0]][move[1]]) == color:
                continue
            if color == "black":
                self.blackMoves.append(((fromRow, fromCol), (move[0], move[1])))
            else:
                self.whiteMoves.append(((fromRow, fromCol), (move[0], move[1])))

    def knightThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that a specific knight is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of a knight to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """
        if color == "black":
            boardThreat = self.blackThreat
        else:
            boardThreat = self.whiteThreat

        potential_spots = [[1, 2], [1, -2], [-1, 2], [-1, -2],
                           [2, 1], [-2, 1], [2, -1], [-2, -1]]
        move_list = []

        for move in potential_spots:
            toRow = fromRow + move[0]
            toCol = fromCol + move[1]
            if (0 <= toRow <= 7) and (0 <= toCol <= 7):  # Excludes moves that would be off the board
                move_list.append((toRow, toCol))

        self.addMoves(move_list, boardThreat, color, fromRow, fromCol)

    def rookThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that a specific rook is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of a rook to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """
        if color == "black":
            boardThreat = self.blackThreat
        else:
            boardThreat = self.whiteThreat

        move_list = []

        possible_dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        for direction in possible_dirs:
            emptySpace = True
            toRow = fromRow
            toCol = fromCol
            while emptySpace:
                toRow = toRow + direction[0]
                toCol = toCol + direction[1]
                if not ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                    break
                toSquare = self.board.squares[toRow][toCol]
                toSquareColor = self.pieces.piece_color(toSquare)

                # If the square is empty it can move there
                if toSquareColor is None:
                    move_list.append((toRow, toCol))

                # If the move has a piece of the same color, add the move
                elif toSquareColor == color:
                    move_list.append((toRow, toCol))
                    emptySpace = False

                # The spot behind the king is still threatened
                # Prevents king suicide thinking it is safe to move away
                else:
                    move_list.append((toRow, toCol))
                    if (toSquare == ChessPiece.B_KING and color == "white"):
                        continue
                    elif (toSquare == ChessPiece.W_KING and color == "black"):
                        continue
                    emptySpace = False

        self.addMoves(move_list, boardThreat, color, fromRow, fromCol)

    def bishopThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that a specific bishop is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of a bishop to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """
        if color == "black":
            boardThreat = self.blackThreat
        else:
            boardThreat = self.whiteThreat

        move_list = []

        possible_dirs = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
        for direction in possible_dirs:
            emptySpace = True
            toRow = fromRow
            toCol = fromCol
            while emptySpace:
                toRow = toRow + direction[0]
                toCol = toCol + direction[1]
                if not ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                    break
                toSquare = self.board.squares[toRow][toCol]
                toSquareColor = self.pieces.piece_color(toSquare)

                # If the square is empty it can move there
                if toSquareColor is None:
                    move_list.append((toRow, toCol))

                # If the move has a piece of the same color, add the move
                elif toSquareColor == color:
                    move_list.append((toRow, toCol))
                    emptySpace = False

                # The spot behind the king is still threatened
                # Prevents king suicide thinking it is safe to move away
                else:
                    move_list.append((toRow, toCol))
                    if (toSquare == ChessPiece.B_KING and color == "white"):
                        continue
                    elif (toSquare == ChessPiece.W_KING and color == "black"):
                        continue
                    emptySpace = False

        self.addMoves(move_list, boardThreat, color, fromRow, fromCol)

    def queenThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that the queen is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of the queen to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """
        if color == "black":
            boardThreat = self.blackThreat
        else:
            boardThreat = self.whiteThreat

        move_list = []

        possible_dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
        for direction in possible_dirs:
            emptySpace = True
            toRow = fromRow
            toCol = fromCol
            while emptySpace:
                toRow = toRow + direction[0]
                toCol = toCol + direction[1]
                if not ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                    break
                toSquare = self.board.squares[toRow][toCol]
                toSquareColor = self.pieces.piece_color(toSquare)

                # If the square is empty it can move there
                if toSquareColor is None:
                    move_list.append((toRow, toCol))

                # If the move has a piece of the same color, add the move
                elif toSquareColor == color:
                    move_list.append((toRow, toCol))
                    emptySpace = False

                # The spot behind the king is still threatened
                # Prevents king suicide thinking it is safe to move away
                else:
                    move_list.append((toRow, toCol))
                    if (toSquare == ChessPiece.B_KING and color == "white"):
                        continue
                    elif (toSquare == ChessPiece.W_KING and color == "black"):
                        continue
                    emptySpace = False

        self.addMoves(move_list, boardThreat, color, fromRow, fromCol)

    def kingThreat(self, color, fromRow, fromCol):
        """
        This function adds all spots that the king is threatening to it's
        correct 'boardThreat' list based on color.

        It also adds all possible moves of the king to the correct color move list,
        either "blackMoves" or "whiteMoves."
        """
        if color == "black":
            boardThreat = self.blackThreat
            opponentThreat = self.whiteThreat
        else:
            boardThreat = self.whiteThreat
            opponentThreat = self.blackThreat

        move_list = []

        possible_dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
        for direction in possible_dirs:
            toRow = fromRow + direction[0]
            toCol = fromCol + direction[1]

            if not ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                continue

            # Don't add threatened spots as valid moves
            if (toRow, toCol) in opponentThreat.keys():
                continue

            move_list.append((toRow, toCol))

        # Kings are not allowed to move adjacent to each other
        listCopy = deepcopy(move_list)
        for move in listCopy:
            for direc in possible_dirs:
                toRow = move[0] + direc[0]
                toCol = move[1] + direc[1]
                if not ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                    continue
                if color == "black":
                    if self.board.squares[toRow][toCol] == ChessPiece.W_KING:
                        move_list.remove(move)
                else:
                    if self.board.squares[toRow][toCol] == ChessPiece.B_KING:
                        move_list.remove(move)

        self.addMoves(move_list, boardThreat, color, fromRow, fromCol)

    def getThreat(self):
        """
        Loops through the board and calls the correct threat method on each piece.
        The threat object's threat and move lists are populated by a call to this method
        """

        # Stores the king locations
        wKing = None
        bKing = None
        for row in range(0, 8):
            for col in range(0, 8):
                piece = self.board.squares[row][col]
                color = self.pieces.piece_color(piece)
                if piece is not None:
                    if piece == ChessPiece.W_ROOK or piece == ChessPiece.B_ROOK:
                        self.rookThreat(color, row, col)
                    elif piece == ChessPiece.W_KNIGHT or piece == ChessPiece.B_KNIGHT:
                        self.knightThreat(color, row, col)
                    elif piece == ChessPiece.W_BISHOP or piece == ChessPiece.B_BISHOP:
                        self.bishopThreat(color, row, col)
                    elif piece == ChessPiece.W_QUEEN or piece == ChessPiece.B_QUEEN:
                        self.queenThreat(color, row, col)
                    elif piece == ChessPiece.W_KING or piece == ChessPiece.B_KING:
                        if piece == ChessPiece.W_KING:
                            wKing = (color, row, col)
                        else:
                            bKing = (color, row, col)
                    elif piece == ChessPiece.W_PAWN or piece == ChessPiece.B_PAWN:
                        self.pawnThreat(color, row, col)

        # Calculates king threat last because it uses the threat around it
        if wKing is not None:
            self.kingThreat(wKing[0], wKing[1], wKing[2])
        if bKing is not None:
            self.kingThreat(bKing[0], bKing[1], bKing[2])

    def addMoves(self, moveList, boardThreat, color, fromRow, fromCol):
        """
        Adds the correct moves to the move list and to the threat list
        :param moveList: the valid moves generated from each threat function
        :param boardThreat: The correct color's threat list
        :param color: current color
        :param fromRow: row of origin spot
        :param fromCol: column of origin spot
        :return: Nothing. Adds to the board threat
        """
        threatList = []
        for move in moveList:
            # If the move has a same color piece, add it to threat but not move list
            if self.pieces.piece_color(self.board.squares[move[0]][move[1]]) == color:
                threatList.append((move[0], move[1]))
                continue
            threatList.append((move[0], move[1]))
            if color == "black":
                self.blackMoves.append(((fromRow, fromCol), (move[0], move[1])))
            else:
                self.whiteMoves.append(((fromRow, fromCol), (move[0], move[1])))

        # Increments the dictionary value of the spot being threatened. Adds a dictionary spot if it's not there
        for move in threatList:
            if (move[0], move[1]) not in boardThreat.keys():
                boardThreat[(move[0], move[1])] = 1
            else:
                boardThreat[(move[0], move[1])] += 1

    def is_game_over(self):
        """
        Checks if the game is over. Finds the kings, returning game is over if one isn't there
        Then calls the white and black wins functions to look for checkmate scenarios
        :return: 0 for No, 1 for White win, 2 for Black win, 3 for Tie
        """
        bk = False
        wk = False

        # Find the kings
        for row in range(8):
            for col in range(8):
                if self.board.squares[row][col] == ChessPiece.B_KING:  # Black king symbol
                    bk = True
                    break
                if self.board.squares[row][col] == ChessPiece.W_KING:  # Black king symbol
                    wk = True
                    break

        # If a king is missing, end the game. This fixes a bug we were having
        if bk == False:
            return 1
        if wk == False:
            return 2

        if self.white_wins():
            return 1
        elif self.black_wins():
            return 2
        elif self.tie():
            return 3
        else:
            return 0

    def white_wins(self):
        """
        Evaluates the board for a checkmate where white wins
        :return: bool
        """
        possible_dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
        toMoves = []
        king_spot = None
        for row in range(8):
            for col in range(8):
                if self.board.squares[row][col] == ChessPiece.B_KING:  # Black king symbol
                    king_spot = (row, col)
                    break
            if king_spot is not None:
                break

        # White doesn't win if it isn't threatening the king
        if king_spot not in self.whiteThreat.keys():
            return False

        for direction in possible_dirs:
            toRow = king_spot[0] + direction[0]
            toCol = king_spot[1] + direction[1]

            if ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                toMoves.append((toRow, toCol))

        # check if we can move out of the mate
        for move in toMoves:
            piece = self.board.squares[move[0]][move[1]]
            piece_color = self.pieces.piece_color(piece)
            if piece_color != "black" and (move[0], move[1]) not in self.whiteThreat.keys():
                return False

        # check can I take the attacker
        attack_spot = None

        for move in self.whiteMoves:
            if move[1] == king_spot:
                attack_spot = move[0]
                break

        # If there is a piece attacking, check the possible moves for black to see if one of them is a kill move
        if attack_spot is not None:
            attack_dir = (attack_spot[0] - king_spot[0], attack_spot[1] - king_spot[1])
            for move in self.blackMoves:
                if move[1] == attack_spot:
                    # Check if the attacker can be taken. It can be taken by a non-king piece, or by the king if
                    # the spot is not protected
                    if (self.board.squares[move[0][0]][move[0][1]] == ChessPiece.B_KING and \
                        (move[1]) not in self.whiteThreat.keys()) or \
                            (self.board.squares[move[0][0]][move[0][1]] != ChessPiece.B_KING):
                        return False

            # Identify the attacking piece
            piece = self.board.squares[attack_spot[0]][attack_spot[1]]
            if piece == '♕' or piece == '♖' or piece == '♗':
                h_dir = attack_dir[0]
                v_dir = attack_dir[1]
                check_squares = []

                if h_dir == 0:
                    for c in range(0, v_dir, int(v_dir / abs(v_dir))):
                        check_squares.append((king_spot[0], king_spot[1] + c))
                elif v_dir == 0:
                    for r in range(0, h_dir, int(h_dir / abs(h_dir))):
                        check_squares.append((r + king_spot[0], king_spot[1]))
                else:
                    rows = []
                    cols = []
                    for r in range(0, h_dir, int(h_dir / abs(h_dir))):
                        rows.append(r)
                    for c in range(0, v_dir, int(v_dir / abs(v_dir))):
                        cols.append(c)
                    for n in range(len(cols)):
                        check_squares.append((rows[n] + king_spot[0], cols[n] + king_spot[1]))

                for move in self.blackMoves:
                    if move[1] in check_squares and move[0] != king_spot:
                        return False

        return True

    def black_wins(self):
        """
        Checks for a checkmate where black wins
        :return: bool
        """
        possible_dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
        toMoves = []
        king_spot = None
        for row in range(8):
            for col in range(8):
                if self.board.squares[row][col] == '♔':  # White king symbol
                    king_spot = (row, col)
                    break
            if king_spot is not None:
                break

        # Black doesn't win if it isn't checking the king
        if king_spot not in self.blackThreat.keys():
            return False

        for direction in possible_dirs:
            toRow = king_spot[0] + direction[0]
            toCol = king_spot[1] + direction[1]

            if ((0 <= toRow <= 7) and (0 <= toCol <= 7)):
                toMoves.append((toRow, toCol))

        # check if we can move out of the mate
        for move in toMoves:
            piece = self.board.squares[move[0]][move[1]]
            piece_color = self.pieces.piece_color(piece)
            if piece_color != "white" and (move[0], move[1]) not in self.blackThreat.keys():
                return False

        # check can I take the attacker
        attack_spot = None

        for move in self.blackMoves:
            if move[1] == king_spot:
                attack_spot = move[0]
                break

        # If there is a piece attacking, check the possible moves for black to see if one of them is a kill move
        if attack_spot is not None:
            attack_dir = (attack_spot[0] - king_spot[0], attack_spot[1] - king_spot[1])
            for move in self.whiteMoves:
                if move[1] == attack_spot:
                    # Check if the attacker can be taken. It can be taken by a non-king piece, or by the king if
                    # the spot is not protected
                    if (self.board.squares[move[0][0]][move[0][1]] == ChessPiece.W_KING and \
                        (move[1]) not in self.blackThreat.keys()) or \
                            (self.board.squares[move[0][0]][move[0][1]] != ChessPiece.W_KING):
                        return False

            piece = self.board.squares[attack_spot[0]][attack_spot[1]]
            if piece == '♛' or piece == '♜' or piece == '♝':
                h_dir = attack_dir[0]
                v_dir = attack_dir[1]
                check_squares = []

                if h_dir == 0:
                    for c in range(0, v_dir, int(v_dir / abs(v_dir))):
                        check_squares.append((king_spot[0], king_spot[1] + c))
                elif v_dir == 0:
                    for r in range(0, h_dir, int(h_dir / abs(h_dir))):
                        check_squares.append((r + king_spot[0], king_spot[1]))
                else:
                    rows = []
                    cols = []
                    for r in range(0, h_dir, int(h_dir / abs(h_dir))):
                        rows.append(r)
                    for c in range(0, v_dir, int(v_dir / abs(v_dir))):
                        cols.append(c)
                    for n in range(len(cols)):
                        check_squares.append((rows[n] + king_spot[0], cols[n] + king_spot[1]))

                for move in self.whiteMoves:
                    if move[1] in check_squares and move[0] != king_spot:
                        #                         print(move[0], move[1], king_spot, check_squares)
                        return False

        return True

    def tie(self):
        return self.stalemate() or self.insufficient_material()

    def stalemate(self):
        """
        Checks for a stalemate. If the current player doesn't have any valid moves, it is a stalemate
        :return: bool
        """
        last_piece = self.pieces.moveHistory[-1][0]
        last_piece_color = self.pieces.piece_color(last_piece)
        if last_piece_color == "black":
            if len(self.whiteMoves) == 0:
                return True
        else:
            if len(self.blackMoves) == 0:
                return True
        return False

    def insufficient_material(self):
        """
        Checks the board to see if there's enough pieces left to win. Pawns can be promoted, so the presence of a
        pawn, queen, or rook automatically returns False. If there are fewer than 2 bishops or knights, there
        is insufficient material
        :return: bool
        """
        piece_set = set()
        for row in range(8):
            for col in range(8):
                piece = self.board.squares[row][col]
                if piece is None:
                    continue
                # Any pawn, queen or rook means there is sufficient material
                if piece == ChessPiece.W_PAWN or piece == ChessPiece.B_PAWN or \
                        piece == ChessPiece.W_QUEEN or piece == ChessPiece.B_QUEEN or \
                        piece == ChessPiece.W_ROOK or piece == ChessPiece.B_ROOK:
                    return False
                else:
                    # If you have 2 bishops or 2 knights, you have sufficient material
                    if piece in piece_set:
                        return False
                    else:
                        piece_set.add(piece)
        return True


class opponent_AI:

    def __init__(self, board, pieces):
        self.board = board
        self.pieces = pieces

    def evaluate(self, board_state, pieces, Vals=None):
        """
        Generates a value based on the current game state. If black has the advantage,
        the heuristic value is positive, and for white it is negative.
        
        The majority of the heuristic relies on threat made by each side.
        """
        if Vals is None:
            hVals = [2, 6, 6, 8, 1000, 2, 6, 6, 8, 1000, 3, 5, 3, 5, 10, 6, 6,
                     8, 50, 100, 4, 6, 6, 8, 50, 15, 10, 5, 15, 5, 10,
                     6, 6, 8, 50, 4, 6, 6, 8, 15, 10, 5, 15, 5]
        else:
            hVals = Vals

        h = 0
        board_threat = Threat(board_state, pieces)
        board_threat.getThreat()
        whiteKing = None
        blackKing = None

        gameOver = board_threat.is_game_over()
        if gameOver == 1:
            return -1000000

        elif gameOver == 2:
            return 1000000

        elif gameOver == 3:
            return 0

        for row in range(8):
            for col in range(8):
                if board_state.squares[row][col] == ChessPiece.B_PAWN:
                    h += hVals[0]
                elif board_state.squares[row][col] == ChessPiece.B_KNIGHT:
                    h += hVals[1]
                elif board_state.squares[row][col] == ChessPiece.B_BISHOP:
                    h += hVals[2]
                elif board_state.squares[row][col] == ChessPiece.B_ROOK:
                    h += hVals[3]
                elif board_state.squares[row][col] == ChessPiece.B_QUEEN:
                    h += hVals[4]
                elif board_state.squares[row][col] == ChessPiece.B_KING:
                    blackKing = (row, col)
                    h += 100000
                elif board_state.squares[row][col] == ChessPiece.W_PAWN:
                    h -= hVals[5]
                elif board_state.squares[row][col] == ChessPiece.W_KNIGHT:
                    h -= hVals[6]
                elif board_state.squares[row][col] == ChessPiece.W_BISHOP:
                    h -= hVals[7]
                elif board_state.squares[row][col] == ChessPiece.W_ROOK:
                    h -= hVals[8]
                elif board_state.squares[row][col] == ChessPiece.W_QUEEN:
                    h -= hVals[9]
                elif board_state.squares[row][col] == ChessPiece.W_KING:
                    whiteKing = (row, col)
                    h -= 100000

        if whiteKing is not None and blackKing is not None:
            for row in range(8):
                for col in range(8):
                    # distance to whiteking
                    distWK = sqrt(((row - whiteKing[0]) ** 2) + ((col - whiteKing[1]) ** 2))
                    # distance to blackking
                    distBK = sqrt(((row - blackKing[0]) ** 2) + ((col - blackKing[1]) ** 2))

                    if (row, col) in board_threat.blackThreat.keys():
                        h += hVals[10] * board_threat.blackThreat[(row, col)] + ((distWK * hVals[11]))
                    if (row, col) in board_threat.whiteThreat.keys():
                        h -= hVals[12] * board_threat.whiteThreat[(row, col)] + ((distBK * hVals[13]))

        for move, threat in board_threat.blackThreat.items():
            if board_state.squares[move[0]][move[1]] == ChessPiece.B_PAWN:
                h += hVals[14] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_KNIGHT:
                h += hVals[15] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_BISHOP:
                h += hVals[16] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_ROOK:
                h += hVals[17] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_QUEEN:
                h += hVals[18] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_PAWN:
                h += hVals[19] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_KNIGHT:
                h += hVals[20] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_BISHOP:
                h += hVals[21] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_ROOK:
                h += hVals[22] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_QUEEN:
                h += hVals[23] * threat * 5
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_KING:
                h += 100000
            if move[0] == 4:
                h += hVals[24] * threat
            if move[0] == 3:
                h += hVals[25] * threat
            if move[0] == 2 or move[0] == 5:
                h += hVals[26] * threat
            if move[1] == 3 or move[1] == 4:
                h += hVals[27] * threat
            if move[1] == 2 or move[1] == 5:
                h += hVals[28] * threat

        for move, threat in board_threat.whiteThreat.items():
            if board_state.squares[move[0]][move[1]] == ChessPiece.W_PAWN:
                h -= hVals[29] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_KNIGHT:
                h -= hVals[30] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_BISHOP:
                h -= hVals[31] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_ROOK:
                h -= hVals[32] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.W_QUEEN:
                h -= hVals[33] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_PAWN:
                h -= hVals[34] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_KNIGHT:
                h -= hVals[35] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_BISHOP:
                h -= hVals[36] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_ROOK:
                h -= hVals[37] * threat
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_QUEEN:
                h -= hVals[38] * threat * 5
            elif board_state.squares[move[0]][move[1]] == ChessPiece.B_KING:
                h -= 100000
            if move[0] == 3:
                h -= hVals[39] * threat
            if move[0] == 4:
                h -= hVals[40] * threat
            if move[0] == 2 or move[0] == 5:
                h -= hVals[41] * threat
            if move[1] == 3 or move[1] == 4:
                h -= hVals[42] * threat
            if move[1] == 2 or move[1] == 5:
                h -= hVals[43] * threat

        return round(h)


################################################################################
class Input:
    """Get input from user for move.
    
    Attributes:
        board: refers to ChessBoard object.
        pieces: refers to ChessPieces object.
        update: Update draw. Needed because tracer(0,0) is used.
        is_piece_selected: true if piece was selected.
        selected_row: row of selected piece.
        selected_col: col of selected piece.
        turn_color: color of player taking current turn.
        
    """

    def __init__(self, chess_board, pieces, window, update):
        """Inits and setup keyboard input handlers.
        
        Args:
            chess_board: Object of ChessBoard
            pieces: Object of CheckPiece
            window: Turtle screen.
            update: Refers to update().
        """
        import turtle

        self.board = chess_board
        self.pieces = pieces
        self.update = update
        self.is_piece_selected = False
        self.selected_row = -1
        self.selected_col = -1
        self.turn_color = "white"
        self.window = turtle.Screen()
        window.onclick(self.findHeuristic)

    def newList(self):
        """
        This function creates a single list of specified length with random numbers
        between 0 and 1500. These values are used as weights in the chessAI heuristic 
        function.
        """
        lst = []
        count = 0
        while count < 52:
            lst.append(randint(1, 1500))
            count += 1
        return lst

    def populationList(self, popSize):
        """
        A list of lists of specified population size.
        """
        popList = []

        while popSize > 0:
            popList.append(self.newList())
            popSize -= 1
        return popList

    def fitness(self, hVals):
        """
        Evaluates how good the list of heuristic weights is at evaluating board states. 
        A "Fitness" value of 0 is ideal, and for every boardstate requirement not
        met the 'fitness' counter is incremented accordingly.
        
        """
        fitness = 0

        board_state = self.board.deep_copy()
        pieces_state = self.pieces.deep_copy()

        ai = opponent_AI(self.board, self.pieces)

        # tie/ 0 score
        board1 = [['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
                ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],
                ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']]

        # mild white advantage
        board2 = [['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
                ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, '♙', None, None, None],
                [None, None, None, None, None, None, None, None],
                ['♙', '♙', '♙', '♙', None, '♙', '♙', '♙'],
                ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']]

        # white advantage
        board3 = [[None, None, None, None, None, '♜', '♚', None],
                [None, None, None, None, None, '♟', '♟', '♟'],
                [None, None, '♟', None, '♟', None, None, None],
                [None, '♟', '♙', None, None, None, None, None],
                [None, '♙', None, None, None, None, None, None],
                [None, None, None, None, None, '♘', None, '♙'],
                [None, None, None, None, '♗', '♙', '♙', None],
                [None, None, None, None, None, None, '♔', None]]
        # black advantage
        board4 = [[None, None, None, '♜', None, None, '♚', None],
                [None, None, '♜', None, None, '♟', None, None],
                [None, None, None, None, '♟', None, '♟', None],
                [None, '♟', None, None, '♙', None, None, '♟'],
                [None, '♙', None, '♙', None, None, None, None],
                [None, None, None, None, None, None, None, '♙'],
                [None, None, None, None, None, '♙', '♙', None],
                [None, None, None, None, '♕', None, '♔', None]]

        # white advantage
        board5 = [[None, None, None, None, None, None, '♚', None],
                ['♟', None, None, None, '♙', None, None, '♟'],
                [None, '♟', None, None, None, '♕', None, None],
                [None, None, None, '♟', None, None, None, '♔'],
                [None, None, '♟', '♙', None, None, '♙', None],
                [None, '♞', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, '♙'],
                [None, None, None, None, '♛', None, None, None]]

        # strong black advantage
        board6 = [[None, '♛', None, None, None, '♗', '♚', None],
                [None, None, None, None, None, '♟', None, '♟'],
                [None, None, '♟', None, None, None, '♟', None],
                [None, '♟', None, '♝', None, None, None, None],
                [None, None, None, None, '♞', None, None, None],
                [None, None, None, None, None, '♘', None, '♙'],
                ['♜', None, None, None, None, None, '♙', '♔'],
                [None, None, None, None, None, None, None, None]]

        # even game
        board7 = [['♜', None, '♝', '♛', '♚', '♝', None, '♜'],
                ['♟', '♟', '♟', None, None, '♟', '♟', '♟'],
                [None, None, '♞', '♟', None, '♞', None, None],
                [None, None, None, None, '♟', None, None, None],
                [None, None, None, None, '♙', None, None, None],
                [None, None, '♘', '♙', None, '♘', None, None],
                ['♙', '♙', '♙', None, None, '♙', '♙', '♙'],
                ['♖', None, '♗', '♕', '♔', '♗', None, '♖']]

        # B Queen
        board9 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♛', None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # B Rook
        board10 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♜', None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # B Bishop
        board11 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♝' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # B Knight
        board12 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♞' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]
        # B Pawn
        board13 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♟' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # W Queen
        board15 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♕', None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # W Rook
        board16 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♖', None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # W Bishop
        board17 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♗' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        # W Knight
        board18 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♘' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]
        # W Pawn
        board19 = [[None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, '♚', '♟'],
                [None, None, None, None, None, None, None, None],
                [None, None, None, '♙' , None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, '♔', '♙', None, None, None, None, None],
                [None, None, None, None, None, None, None, None]]

        board_state.squares = board1

        score1 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        # encourages heuristic to evaluate black and white pieces equivalently and opposite to each other
        if not (-24000 < score1 < 24000):
            fitness += 3

        if not (-12000 < score1 < 12000):
            fitness += 3

        if not (-6000 < score1 < 6000):
            fitness += 2

        if not (-5000 < score1 < 5000):
            fitness += 2

        if not (-4000 < score1 < 4000):
            fitness += 2

        if not (-3000 < score1 < 3000):
            fitness += 2

        if not (-2000 < score1 < 2000):
            fitness += 1

        if not (-1000 < score1 < 1000):
            fitness += 1

        if not (-500 < score1 < 500):
            fitness += 1

        if not (-400 < score1 < 400):
            fitness += 1

        if not (-300 < score1 < 300):
            fitness += 1

        if not (-250 < score1 < 250):
            fitness += 1

        if not (-200 < score1 < 200):
            fitness += 1

#         # If the heuristic needs to be very specific
#         if not (-150 < score1 < 150):
#             fitness += 1
#
#         if not (-100 < score1 < 100):
#             fitness += 1
#
#         if not (-75 < score1 < 75):
#             fitness += 1
#
#         if not (-50 < score1 < 50):
#             fitness += 1

        board_state.squares = board2

        score2 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        if score2 > score1:
            fitness += 1

        board_state.squares = board3

        score3 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        if score3 > -200:
            fitness += 1

        board_state.squares = board4

        score4 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        if score4 < 300:
            fitness += 1

        board_state.squares = board5

        score5 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        if score5 > -200:
            fitness += 1

        if score3 > score2:
            fitness += 1

        if score5 > score2:
            fitness += 1

        board_state.squares = board6

        score6 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        if score6 < 500:
            fitness += 1

        if score6 < score4:
            fitness += 1

        board_state.squares = board7

        score7 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        # encourages heuristic to evaluate black and white pieces equivalently and opposite to each other
        if not (-24000 < score7 < 24000):
            fitness += 3

        if not (-12000 < score7 < 12000):
            fitness += 3

        if not (-6000 < score7 < 6000):
            fitness += 2

        if not (-5000 < score7 < 5000):
            fitness += 2

        if not (-4000 < score7 < 4000):
            fitness += 2

        if not (-3000 < score7 < 3000):
            fitness += 2

        if not (-2000 < score7 < 2000):
            fitness += 1

        if not (-1000 < score7 < 1000):
            fitness += 1

        if not (-500 < score7 < 500):
            fitness += 1

        if not (-400 < score7 < 400):
            fitness += 1

        if not (-300 < score7 < 300):
            fitness += 1

        if not (-250 < score7 < 250):
            fitness += 1

        if not (-200 < score7 < 200):
            fitness += 1

#         if not (-150 < score7 < 150):
#             fitness += 1
#
#         if not (-100 < score7 < 100):
#             fitness += 1
#
#         if not (-75 < score7 < 75):
#             fitness += 1
#
#         if not (-50 < score7 < 50):
#             fitness += 1

        board_state.squares = board9
        score9 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board10
        score10 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board11
        score11 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board12
        score12 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board13
        score13 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        # Optimizes Black piece values relative to board impact
        if not (score9 > score10 > score11 > score13 > 0):
            fitness += 1
        if not (score9 > score10 > score12 > score13 > 0):
            fitness += 1

        board_state.squares = board15
        score15 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board16
        score16 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board17
        score17 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board18
        score18 = ai.evaluate(board_state, pieces_state, Vals=hVals)
        board_state.squares = board19
        score19 = ai.evaluate(board_state, pieces_state, Vals=hVals)

        # Optimizes White piece values relative to board impact
        if not (0 > score19 > score18 > score16 > score15):
            fitness += 1

        if not (0 > score19 > score17 > score16 > score15):
            fitness += 1

        if not ((score15) < (score18 + score17) < score16):
            fitness += 1

        if not ((score9) > (score11 + score12) > score10):
            fitness += 1

        # For troubleshooting
        print(fitness, ": ", hVals)

        return fitness

    def evolve(self, popList, retain, random_select, mutate):
        """
        Evolves the entire population of lists, selecting for lists which have the 
        best fitness (lowest value). Random mutation and random selection of some 
        members of the population prevent getting stuck at local maxima.
        """
        popGrades = []
        parents = []
        # deep copy of population List
        population = list(popList)

        for p in population:
            popGrades.append(self.fitness(p))

        parentPopSize = round(len(popList) * retain)

        # adds the percentage specified of the population to the parents list
        while parentPopSize > 0:
            fit = popGrades[0]
            count = 0
            fittest = 0
            for g in popGrades:
                if g < fit:
                    fit = g
                    fittest = count
                count += 1

            parents.append(population[fittest])
            population.pop(fittest)
            popGrades.pop(fittest)
            parentPopSize -= 1

        # selects some random individuals and adds them to the population as well
        for lst in population:
            if random_select > random():
                parents.append(lst)

        # random muatations for more genetic diversity
        for parent in parents:
            if mutate > random():
                randPosition = randint(0, len(parent) - 1)
                parent[randPosition] = randint(1, 1500)

        # crossing over
        parentsLength = len(parents)
        desiredLength = len(popList) - parentsLength

        children = []

        while len(children) < desiredLength:
            par1 = randint(0, parentsLength - 1)
            par2 = randint(0, parentsLength - 1)

            if par1 != par2:
                par1 = parents[par1]
                par2 = parents[par2]

                # each parentis weighed a random amount rather than a 50/50 split
                split = randint(0, len(par1))
                child = par1[:split] + par2[split:]
                children.append(child)

        children.extend(parents)

        return children

    def findHeuristic(self, _, __):
        """
        Finds optimized heuristic weights for chess AI minimax heuristic
        """
        popSize = 100
        retain = 0.25
        random_select = 0.1
        mutate = 0.1

        popList = self.populationList(popSize)

        solved = False
        count = 0
        while not solved:
            # evolves current
            popList = (self.evolve(popList, retain, random_select, mutate))
#             print(popList)  # for troubleshooting
            for i in popList:
                if (self.fitness(i) == 0):
                    print("solution: ", i)
                    solved = True
                    break
                # if plateus at a local minima, then end after 50 generations
                if count >= 50:
                    if (self.fitness(i) <= 10):
                        print("solution: ", i)
                        solved = True
                        break
            if solved is True:
                break
            print("-----------------")

            # will modify mutation, random_select and retain values to help leave a
            # local minima. More randomness the longer it takes up to specific points
            if count % 3 == 0:
                if mutate < 0.2:
                    mutate += 0.01
                if random_select < 0.3:
                    random_select += 0.01
            count += 1

        return exit(0)


################################################################################
# Run the Game.
# print "\x1b[30m \x1b[0m"
chess = Chess()
chess.run()
