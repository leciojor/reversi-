import numpy as np
import reversi_bot
import socket
import sys
import time

class ReversiServerConnection:
    def __init__(self, host, bot_move_num):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, 3333 + bot_move_num)
        self.sock.connect(server_address)
        self.sock.recv(1024)

    def get_game_state(self):
        server_msg = self.sock.recv(1024).decode('utf-8').split('\n')

        turn = int(server_msg[0])

        # If the game is over
        if turn == -999:
            return ReversiGameState(None, turn)

        # Flip is necessary because of the way the server does indexing
        board = np.flip(np.array([int(x) for x in server_msg[4:68]]).reshape(8, 8), 0)

        return ReversiGameState(board, turn)

    def send_move(self, move):
        # The 7 - bit is necessary because of the way the server does indexing
        move_str = str(7 - move[0]) + '\n' + str(move[1]) + '\n'
        self.sock.send(move_str.encode('utf-8'))

class ReversiGame:
    def __init__(self, host, bot_move_num, mode):
        self.bot_move_num = bot_move_num
        self.server_conn = ReversiServerConnection(host, bot_move_num)
        self.bot = reversi_bot.ReversiBot(bot_move_num)
        self.mode = int(mode)

    def play(self):
        while True:
            state = self.server_conn.get_game_state()

            # If the game is over
            if state.turn == -999:
                time.sleep(1)
                sys.exit()

            # If it is the bot's turn
            if state.turn == self.bot_move_num:
                move = self.bot.make_move(state, self.mode)
                self.server_conn.send_move(move)

class ReversiGameState:
    DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1),
    (1, 0), (1, -1), (0, -1), (-1, -1)]

    def __init__(self, board, turn):
        self.board_dim = 8 # Reversi is played on an 8x8 board
        self.board = board
        self.turn = turn # Whose turn is it

    def capture_will_occur(self, row, col, xdir, ydir, opponent, could_capture=0):
        # We shouldn't be able to leave the board
        if not self.space_is_on_board(row, col):
            return False

        # If we're on a space associated with our turn and we have pieces
        # that could be captured return True. If there are no pieces that
        # could be captured that means we have consecutive bot pieces.
        check = self.turn
        if opponent:
            check = 3 - self.turn
            
        if self.board[row, col] == check:
            return could_capture != 0

        if self.space_is_unoccupied(row, col):
            return False

        return self.capture_will_occur(row + ydir,
                                       col + xdir,
                                       xdir, ydir, opponent,
                                       could_capture + 1)

    def space_is_on_board(self, row, col):
        return 0 <= row < self.board_dim and 0 <= col < self.board_dim

    def space_is_unoccupied(self, row, col):
        return self.board[row, col] == 0

    def space_is_available(self, row, col):
        return self.space_is_on_board(row, col) and \
               self.space_is_unoccupied(row, col)

    def is_valid_move(self, row, col, opponent):
        if self.space_is_available(row, col):
            # A valid move results in capture
            for xdir in range(-1, 2):
                for ydir in range(-1, 2):
                    if xdir == ydir == 0:
                        continue
                    if self.capture_will_occur(row + ydir, col + xdir, xdir, ydir, opponent):
                        return True
                    
    def get_amount_of_pieces(self, color):
        count = 0
        for i in range(8):
            for j in range(8):
                if self.board[i,j] == color:
                    count += 1
        return count
    
    def get_amount_of_corners(self, color):
        count = 0
        for i in range(8):
            for j in range(8):
                if self.board[i,j] == color and i == 7 and j == 7:
                    count += 1
        return count


    def get_valid_moves(self, opponent=False):
        valid_moves = []

        # If the middle four squares aren't taken the remaining ones are all
        # that is available
        if 0 in self.board[3:5, 3:5]:
            for row in range(3, 5):
                for col in range(3, 5):
                    if self.board[row, col] == 0:
                        valid_moves.append((row, col))
        else:
            for row in range(self.board_dim):
                for col in range(self.board_dim):
                    if self.is_valid_move(row, col, opponent):
                        valid_moves.append((row, col))

        return valid_moves
    
    def get_new_state(self, move, player, opponent, turn):
        board = self.board
        row = move[0]
        col = move[1]
        new_board = board.copy()  
        new_board[row, col] = player  

        for dr, dc in ReversiGameState.DIRECTIONS:
            r, c = row + dr, col + dc
            to_flip = []

            while 0 <= r < 8 and 0 <= c < 8 and new_board[r, c] == opponent:
                to_flip.append((r, c))
                r += dr
                c += dc

            if 0 <= r < 8 and 0 <= c < 8 and new_board[r, c] == player:
                for fr, fc in to_flip:
                    new_board[fr, fc] = player

        return ReversiGameState(new_board, not turn) 
    
    def is_stable(self, row, col):
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:  
            return True
        
        for dr, dc in ReversiGameState.DIRECTIONS:
            r, c = row, col
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r, c] == 0:  
                    return False
                r += dr
                c += dc
        return True

    def is_unstable(self, row, col, player, opponent):
        for dr, dc in ReversiGameState.DIRECTIONS:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r, c] == opponent:
                while 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r, c] == 0:  
                        return True
                    if self.board[r, c] == player:  
                        break
                    r += dr
                    c += dc
        return False

    def stability_score(self, player):
        score = 0
        for row in range(8):
            for col in range(8):
                if self.board[row, col] == player:
                    if self.is_stable(row, col):
                        score += 1
                    elif self.is_unstable(row, col, player, 3-player):
                        score -= 1  
                    
        return score


