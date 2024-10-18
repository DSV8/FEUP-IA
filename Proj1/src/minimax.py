import math
from state import *

# Returns the difference of white and black stones
# player is the one making the minimax/negamax moves
def stone_diff(state, player):
    p1_stones, p2_stones = state.stones_remaining
    stone_diff = (p1_stones - p2_stones)

    return stone_diff * (1 if player == 1 else -1) # Multiplication due to it beeing writen from player 1's perspective

#
def board_control(state, player):
    # Used sets so that a certain position is considered only once
    pos_p1_can_move_to = set()
    pos_p2_can_move_to = set()
    pos_p1_can_capture = set()
    pos_p2_can_capture = set()

    row_cnt, col_cnt = state.board_size
    for row in range(row_cnt):
        for col in range(col_cnt):
            stone = state.board[row][col]
            if stone == Stone.EMPTY: continue
            # For each direction, add to the set the positions of the stones
            # the stone at this position attacks
            for way in Way:
                if ((row + col) % 2 != 0) and (way_to_direction[way] == Direction.DIAGONAL_1 or way_to_direction[way] == Direction.DIAGONAL_2):
                    continue

                dx, dy = way.value

                # Get for this direction the stone 1 and 2 cells in front and 1 cell behing
                forward_1 = (row + dx, col + dy)
                forward_2 = (row + 2*dx, col + 2*dy)
                backward = (row - dx, col - dy)

                stone_ford_1 = state.board[forward_1[0]][forward_1[1]] if state.valid_pos(forward_1) else None
                stone_ford_2 = state.board[forward_2[0]][forward_2[1]] if state.valid_pos(forward_2) else None
                stone_back = state.board[backward[0]][backward[1]] if state.valid_pos(backward) else None

                # Builds the positions that white/black stones are attacking, and to where they can move
                if stone_ford_1 == Stone.EMPTY:
                    if stone == Stone.WHITE:
                        if stone_ford_2 is not None:
                            pos_p1_can_capture.add(forward_2)
                        pos_p1_can_move_to.add(forward_1)
                    elif stone == Stone.BLACK:
                        if stone_ford_2 is not None:
                            pos_p2_can_capture.add(forward_2)
                        pos_p2_can_move_to.add(forward_1)

                if stone_back == Stone.EMPTY and stone_ford_1 is not None:
                    if stone == Stone.WHITE:
                        pos_p1_can_capture.add(forward_1)
                    elif stone == Stone.BLACK:
                         pos_p2_can_capture.add(forward_1)

    # Fraction of the number of positions to where Black stones can move to, that Player one can capture in
    # If Player 1 has one, the value is maximum
    p1_control = 1 if state.winner == 1 else len(pos_p1_can_capture.intersection(pos_p2_can_move_to))/len(pos_p2_can_move_to)
    # Fraction of the number of positions to where White stones can move to, that Player two can capture in
    # If Player 2 has one, the value is maximum
    p2_control = 1 if state.winner == 2 else len(pos_p2_can_capture.intersection(pos_p1_can_move_to))/len(pos_p1_can_move_to)

    board_control = p1_control - p2_control

    return board_control * (1 if player == 1 else -1)

# Returns the number of stones of the player making
# the minimax/negamax move under attack in this state
def attacked(state, player):
    # Used sets so that a certain position is considered under attack only once
    pos_p1_attacked = set()
    pos_p2_attacked = set()

    row_cnt, col_cnt = state.board_size
    for row in range(row_cnt):
        for col in range(col_cnt):
            stone = state.board[row][col]
            if stone == Stone.EMPTY: continue
            # For each direction, add to the set the positions of the stones
            # the stone at this position attacks
            for way in Way:
                # Skip the diagonals on the cells that don't have them
                if ((row + col) % 2 != 0) and (way_to_direction[way] == Direction.DIAGONAL_1 or way_to_direction[way] == Direction.DIAGONAL_2):
                    continue

                dx, dy = way.value

                # Get for this direction the stone 1 and 2 cells in front and 1 cell behing
                forward_1 = (row + dx, col + dy)
                forward_2 = (row + 2*dx, col + 2*dy)
                backward = (row - dx, col - dy)

                stone_ford_1 = state.board[forward_1[0]][forward_1[1]] if state.valid_pos(forward_1) else None
                stone_ford_2 = state.board[forward_2[0]][forward_2[1]] if state.valid_pos(forward_2) else None
                stone_back = state.board[backward[0]][backward[1]] if state.valid_pos(backward) else None

                if stone_ford_1 == Stone.EMPTY:
                    if stone == Stone.WHITE:
                        if stone_ford_2 == Stone.BLACK:
                            stones_attacked = state.get_consecutive_stones(forward_2, (dx, dy))
                            pos_p2_attacked.update(stones_attacked)
                    elif stone == Stone.BLACK:
                        if stone_ford_2 == Stone.WHITE:
                            stones_attacked = state.get_consecutive_stones(forward_2, (dx, dy))
                            pos_p1_attacked.update(stones_attacked)

                if stone_back == Stone.EMPTY:
                    if stone == Stone.WHITE:
                        if stone_ford_1 == Stone.BLACK:
                            stones_attacked = state.get_consecutive_stones(forward_1, (dx, dy))
                            pos_p2_attacked.update(stones_attacked)
                    elif stone == Stone.BLACK:
                         if stone_ford_1 == Stone.WHITE:
                            stones_attacked = state.get_consecutive_stones(forward_1, (dx, dy))
                            pos_p1_attacked.update(stones_attacked)

    p1_attacked = len(pos_p1_attacked)
    p2_attacked = len(pos_p2_attacked)

    # Return the number of stones beeing attacked, in accordance to player
    attacked = (p1_attacked if player == 1 else p2_attacked)

    return attacked


# Only uses heuristic 1
def eval_f1(state, player):
    return stone_diff(state, player)


# Uses heuristic 1 and 2
def eval_f2(state, player):
    return stone_diff(state, player) - attacked(state, player)


# Uses heuristic 1 and 3
def eval_f3(state, player):
    return stone_diff(state, player) + board_control(state, player)


# Uses all heuristic
def eval_f4(state, player):
    return stone_diff(state, player) + board_control(state, player) - attacked(state, player)


# Returns the key from which to sort the minimax successors
def get_sort_key(element):
    if isinstance(element, CaptureSequenceNode):
        # The value of a capture sequence node is the total sum of the stones
        # captured by its children
        return element.value
    elif isinstance(element, Capture):
        # The number of stones captured
        return len(element.stones_captured)
    elif isinstance(element, Paika) or element == 'q':
        # Quitting a capture sequence or a paika move captures no children
        return 0
    else:
        raise TypeError(f"Unexpected type: {type(element)}")
    

# Calls an aux function to make a minimax move
# with a certain evaluation function and depth
def make_minimax_move(eval_func, depth):
    def make_minimax_move_aux(game):
        # There is no need to calculate minimax, if there is only 1 valid move
        if len(game.state.valid_moves) == 1:
            game.state = game.state.apply_move(game.state.valid_moves[0])
            return
        
        best_move = None
        best_eval = -math.inf

        moves = game.state.valid_moves
        # Moves with most stones captured come first
        moves.sort(key=get_sort_key, reverse=True)

        for move in moves:
            new_state = game.state.apply_move(move)
            new_state_eval = minimax(new_state, depth-1, -math.inf, math.inf, False, game.state.player, eval_func)
            if new_state_eval > best_eval:
                best_move = new_state
                best_eval = new_state_eval
        # The new game state is the state resulting from aplying the move
        # with greatest evaluation
        game.state = best_move

    return make_minimax_move_aux

# The minimax implementation
def minimax(state, depth, alpha, beta, maximizing, player, eval_func):
    # Returns evaluation if it has reached max depth
    # Or the game has ended
    if depth == 0 or state.winner != -1:
        return eval_func(state, player)

    moves = state.valid_moves
    # Moves with most stones captured come first
    moves.sort(key=get_sort_key, reverse=True)

    if maximizing:
        max_eval = -math.inf
        for move in moves:
            new_state = state.apply_move(move)
            new_maximizing = False
            # If the move is part of a capture sequence, keep maximizing
            if isinstance (move, CaptureSequenceNode):
                new_maximizing = True
            evaluation = minimax(new_state, depth-1, alpha , beta, new_maximizing, player, eval_func)
            max_eval = max(max_eval, evaluation)
            # For alpha-beta pruning
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            new_state = state.apply_move(move)
            new_maximizing = True
            # If the move is part of a capture sequence, keep minimizing
            if isinstance (move, CaptureSequenceNode):
                new_maximizing = False
            evaluation = minimax(new_state, depth-1, alpha, beta, new_maximizing, player, eval_func)
            min_eval = min(min_eval, evaluation)
            # For alpha-beta pruning
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval

# Negamax is based on our minimax implementation.
def make_negamax_move(eval_func, depth):
    def make_negamax_move_aux(game):
        if len(game.state.valid_moves) == 1:
            game.state = game.state.apply_move(game.state.valid_moves[0])
            return
        
        best_move = None
        best_eval = -math.inf

        moves = game.state.valid_moves
        moves.sort(key=get_sort_key, reverse=True)

        new_state_value = -math.inf
        for move in moves:
            new_state = game.state.apply_move(move)
            new_state_value = max(new_state_value, -negamax(new_state, depth-1, -math.inf, math.inf, game.state.player, eval_func, -1))
            if new_state_value > best_eval:
                best_move = new_state
                best_eval = new_state_value
        game.state = best_move

    return make_negamax_move_aux

# Color == -1 "minimizes" and color == 1 "maximizes"
def negamax(state, depth, alpha, beta, player, eval_func, color):
    if depth == 0 or state.winner != -1:
        return color * (eval_func(state, player))

    moves = state.valid_moves
    moves.sort(key=get_sort_key, reverse=True)

    value = -math.inf
    for move in moves:
        new_state = state.apply_move(move)
        if isinstance (move, CaptureSequenceNode):
            value = max(value, negamax(new_state, depth-1, alpha, beta, player, eval_func, color))
        else:
            value = max(value, -negamax(new_state, depth-1, -beta, -alpha, player, eval_func, -color))
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    return value
