
class ReversiBot:
    def __init__(self, move_num):
        self.move_num = move_num

    def main(self, state):
        valid_moves = state.get_valid_moves()
        other = 3 - self.move_num
        alpha = float('-inf')  
        beta = float('inf')    
             
        move_chosen = valid_moves[0]
        for move in valid_moves:
            curr_utility = self.minimax(move, 0, True, state, other, alpha, beta)
            if curr_utility > alpha:
                alpha = curr_utility
                move_chosen = move

        return move_chosen

    def evaluation(self, curr_state, other, valid_moves, valid_moves_opponent):
        if not self.mode: 
            max_amount_pieces = curr_state.get_amount_of_pieces(self.move_num)
            min_amount_pieces = curr_state.get_amount_of_pieces(other)
            return self.evaluation_logic(max_amount_pieces, min_amount_pieces)
        if self.mode == 1:
            max_valid = valid_moves
            min_valid = valid_moves_opponent
            return self.evaluation_logic(max_valid, min_valid)
        elif self.mode == 2:
            max_corners = curr_state.get_amount_of_corners(self.move_num)
            min_corners = curr_state.get_amount_of_corners(other)
            return self.evaluation_logic(max_corners, min_corners)
        elif self.mode == 3:
            max_stability = curr_state.stability_score(self.move_num)
            min_stability = curr_state.stability_score(other)
            return self.evaluation_logic(max_stability, min_stability)
        elif self.mode == 4:
            return self.evaluation_logic(curr_state.get_amount_of_pieces(self.move_num), curr_state.get_amount_of_pieces(other), valid_moves, valid_moves_opponent, curr_state.get_amount_of_corners(self.move_num), curr_state.get_amount_of_corners(other), curr_state.stability_score(self.move_num), curr_state.stability_score(other))

    def minimax(self, move, curr, turn, curr_state, other, alpha, beta):
        new_state = curr_state.get_new_state(move, self.move_num, other, turn)
        valid_moves = new_state.get_valid_moves()
        if curr == self.max_depth or not valid_moves: 
            return self.evaluation(curr_state, other, len(valid_moves), len(new_state.get_valid_moves(opponent=True))) 
        
        scores = []
        if (turn):
            for new_move in valid_moves:
                score = self.minimax(new_move, curr + 1, False, new_state, other, alpha, beta)
                scores.append(score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break 

            return max(scores)
        
        else:
            for new_move in valid_moves:
                score = self.minimax(new_move, curr + 1, True, new_state, other, alpha, beta)
                scores.append(score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min(scores)


    def make_move(self, state, mode):
        '''
        The parameter "state" is of type ReversiGameState and has two useful
        member variables. The first is "board", which is an 8x8 numpy array
        of 0s, 1s, and 2s. If a spot has a 0 that means it is unoccupied. If
        there is a 1 that means the spot has one of player 1's stones. If
        there is a 2 on the spot that means that spot has one of player 2's
        stones. The other useful member variable is "turn", which is 1 if it's
        player 1's turn and 2 if it's player 2's turn.

        ReversiGameState objects have a nice method called get_valid_moves.
        When you invoke it on a ReversiGameState object a list of valid
        moves for that state is returned in the form of a list of tuples.

        Move should be a tuple (row, col) of the move you want the bot to make.
        '''
        self.mode = mode
        self.max_depth = 4
        if not mode:
            self.evaluation_logic = self.eval_1
        elif mode == 1:
            self.evaluation_logic = self.eval_2
        elif mode == 2:
            self.evaluation_logic = self.eval_3
        elif mode == 3:
            self.evaluation_logic = self.eval_4
        elif mode == 4:
            self.evaluation_logic = self.eval_5

        move = self.main(state)
        return move

    def eval_1(self, max_coins_amount, min_coins_amount):
        return 100 * (max_coins_amount - min_coins_amount ) / (max_coins_amount + min_coins_amount)

    def eval_2(self, max_player_moves, min_player_moves):
        if max_player_moves + min_player_moves:
                return 100 * (max_player_moves - min_player_moves) / (max_player_moves + min_player_moves)
        return 0 

    def eval_3(self, max_corners, min_corners):
        return self.eval_2(max_corners, min_corners)

    def eval_4(self, max_stability, min_stability):
        return self.eval_2(max_stability, min_stability)

    def eval_5(self, max_coins_amount, min_coins_amount, max_player_moves, min_player_moves, max_corners, min_corners, max_stability, min_stability):
        return 0.3 * self.eval_1(max_coins_amount, min_coins_amount) + 0.1 * self.eval_2(max_player_moves, min_player_moves) + 0.2 * self.eval_3(max_corners, min_corners) + 0.4 * self.eval_4(max_stability, min_stability)
