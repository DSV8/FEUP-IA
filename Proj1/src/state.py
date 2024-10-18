from enum import Enum
from copy import deepcopy


# Enum for representing a stone
# Empty describes an empty position in the board 
class Stone(Enum):
    WHITE = 1
    BLACK = 2
    EMPTY = 3

    def __str__(self):
        return str(self.name)


# Enum for diferentiating between the 2 kinds of captures
class CaptureType(Enum):
    APPROACH = 1
    WITHDRAWAL = 2


# Enum for representing the "ways" (sub-directions), a stone can move in
# The values are tuples with the row and col deltas, when a stone moves that way on the board 
class Way(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    DIAGONAL_1_UP = (-1, -1)
    DIAGONAL_1_DOWN = (1, 1)
    DIAGONAL_2_DOWN = (1, -1)
    DIAGONAL_2_UP = (-1, 1)


# Enum for diferentiating between the 2 kinds of captures
class Direction(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    DIAGONAL_1 = 2 # The diagonal leaning -45º
    DIAGONAL_2 = 3 # The diagonal leaning 45º


# A dictionary that maps a way to its corresponding direction
# Used to check that the player is not capturing in the same direction twice, in a capture sequence
way_to_direction = {
    Way.UP: Direction.VERTICAL,
    Way.DOWN: Direction.VERTICAL,
    Way.LEFT: Direction.HORIZONTAL,
    Way.RIGHT: Direction.HORIZONTAL,
    Way.DIAGONAL_1_UP: Direction.DIAGONAL_1,
    Way.DIAGONAL_1_DOWN: Direction.DIAGONAL_1,
    Way.DIAGONAL_2_UP: Direction.DIAGONAL_2,
    Way.DIAGONAL_2_DOWN: Direction.DIAGONAL_2
}


# The "interface" to implement the 2 types of moves
class Move:
    def __init__(self, origin, destination, way) -> None:
        self.origin = origin # Tuple with x and y values of the stone to move
        self.destination = destination # Tuple with x and y values of the the stone after the move
        self.way = way # Enum value that represents the way in wich the stone moves

    def __str__(self):
        return "Src: " + str(self.origin) + "; Dest: " + str(self.destination) + "; Way: " + str(self.way.name)


# A Paika simply inherits from Move
class Paika(Move):
    pass


# A Capture inherits from Move and adds 2 new fields
class Capture(Move):
    def __init__(self, origin, destination, way, capture_type, stones_captured):
        super().__init__(origin, destination, way)
        self.capture_type = capture_type # Approach or Withdrawal
        self.stones_captured = stones_captured # List with the positions of all the stones captured

    def __str__(self):
        return super().__str__() + "; Capture Type: " + str(self.capture_type.name) + "; Stones Captured: " + str(self.stones_captured)


# Tree structure that represents a capturing sequence
class CaptureSequenceNode():
    def __init__(self, capture, parent=None):
        self.capture = capture # The Capture this node is describing
        self.value = len(capture.stones_captured)
        self.dir = way_to_direction[capture.way] # The direction of this capture
                                                 # We can check with parents to see if they're different
        self.parent = parent # The parent node of this node. Starting Node is the only with value None 
        self.children = [] # List with the child nodes
                           # Represents the next captures in the sequence that this one can generate

    def __str__(self):
        return "[Capture Sequence Node] | Capture: " + str(self.capture) + " | Value: " + str(self.value) + " | Direction: " + self.dir.name + " | Nº of children: " + str(len(self.children))

    # Appends node to the children list, and this is set as the parent of child
    def add_child(self, child_node):
        self.children.append(child_node)
        self.value += child_node.value
        child_node.parent = self

# Recursive function to check if a position already appeared in a capturing sequence
def pos_in_seq(node, pos):
        if node == None: # Reached start node
                         # Pos is not apart of this capturing path
            return False
        elif pos == node.capture.origin: # Pos is the position of the capture i'm evaluating
                                         # and it corresponds to the destination of the previous capture,
                                         # so I only need to check against origin
            return True
        else:
            return pos_in_seq(node.parent, pos)

# Function to check if the direction of the capture I'm evaluating
# is the same as the direction of the last node in the sequence
def same_dir_twice(last_node, direction):
    return last_node.dir == direction


# The class that represent the game state
class State():
    def __init__(self, vertical, horizontal):
        self.player = 1 # White starts first
        self.winner = -1 # No winner = -1, draw = 0, player 1 = 1, player 2 = 2
        self.stones_remaining = self.init_num_stones(vertical,horizontal) # First is White, Second is Black
        self.last_positions = [None, None] # Last position for white and black. Used to check for repetitions
        self.repetitions = [0, 0] # Number of times white or black returns to the same position. If both reach 3, a draw happens
        self.board_size = (vertical, horizontal) # Number of rows and columns of the board
        self.board = self.init_board(vertical,horizontal) # Initializes the board
        self.valid_moves = [] # List with the moves that the current player can play.
        self.ai_moves = []

        self.get_moves_board() # Gets the valid moves for the initial state

    # Dynamically builds the board, given a number of rows and columns
    def init_board(self,x,y):
        board = []
        for i in range(x):
            if (i<(x//2)):
                l = [Stone.BLACK for _ in range(y)]
                board.append(l)
            elif(i==x//2):
                l= [Stone.BLACK if x % 2 == 0 else Stone.WHITE for x in range(y//2)]
                if (i%2==0):
                    final = l + [Stone.EMPTY] + l
                    board.append(final)
                else:
                    l2= [Stone.WHITE if x % 2 == 0 else Stone.BLACK for x in range(y//2)]
                    final = l + [Stone.EMPTY] + l2
                    board.append(final)
                
            else:
                l = [Stone.WHITE for _ in range(y)]
                board.append(l)
        return board
    
    # Initializes the number of stones of each player
    def init_num_stones(self,x,y):
        num = (x*y)//2
        return(num,num)

    # Replaces the stone specified by pos with a Stone.Empty value
    # and decreases the respective value in the stones_remaining tuple
    def remove_stone(self, pos):
        row, col = pos
        white_left, black_left = self.stones_remaining
        stone = self.board[row][col]
        self.stones_remaining = (white_left-1, black_left) if stone == Stone.WHITE else (white_left, black_left-1)
        self.board[row][col] = Stone.EMPTY

    # Replaces the stone specified by pos with a Stone.Empty value
    # and returns the stone (lifting a stone off the board to move it)
    def pop_stone(self, pos):
        row, col = pos
        stone = self.board[row][col]
        self.board[row][col] = Stone.EMPTY
        return stone

    # Places the sone in the cell specified by pos
    def place_stone(self, pos, stone):
        row, col = pos
        self.board[row][col] = stone

    # Checks if either one of the values in stones_remaining is 0
    # and returns the winner if so. Otherwise returns None
    def update_winner(self):
        remaining_white, remaining_black = self.stones_remaining
        if remaining_white == 0:
            self.winner = 2
        elif remaining_black == 0:
            self.winner = 1
        elif self.repetitions == [3, 3]:
            self.winner = 0

    # Receives a move, makes a copy of the current state, applies
    # the effects of the move to the copy and returns it
    def apply_move(self, move):
        copied_state = deepcopy(self)

        if isinstance(move, CaptureSequenceNode):
            stone = copied_state.pop_stone(move.capture.origin)
            copied_state.place_stone(move.capture.destination, stone)

            for captured_stone in move.capture.stones_captured:
                copied_state.remove_stone(captured_stone)

            copied_state.update_winner()

            # If it's part of a capture sequence, it only switches switches turn
            # if it's the last node otherwise, it makes the valid moves of the
            # new state, the children of the current node plus the option of
            # stopping the sequence (move 'q')
            if move.children:
                copied_state.valid_moves = move.children + ['q']
            else:
                copied_state.swap_player()
                copied_state.get_moves_board()
        elif move == 'q':
            # When stopping a capture sequence, simply switches turn
            # and gets the new valid moves
            copied_state.swap_player()
            copied_state.get_moves_board()
        else:
            # For AI
            if isinstance(move, list):
                list_of_captures = move
                for capture in list_of_captures:
                    stone = copied_state.pop_stone(capture.origin)
                    copied_state.place_stone(capture.destination, stone)

                    for captured_stone in capture.stones_captured:
                        copied_state.remove_stone(captured_stone)
            else: 
                # Moves stone to its destination
                stone = copied_state.pop_stone(move.origin)
                copied_state.place_stone(move.destination, stone)

                # If its a capture, remove all captured stones from the board
                if isinstance(move, Capture):
                    for captured_stone in move.stones_captured:
                        copied_state.remove_stone(captured_stone)

                else:
                    # When there are no more  captures availables, it starts
                    # counting 
                    if copied_state.last_positions[copied_state.player - 1] == move.destination:
                        copied_state.repetitions[copied_state.player - 1] += 1
                    else:
                        copied_state.repetitions = [0, 0]

                    copied_state.last_positions[copied_state.player - 1] = move.origin

            copied_state.update_winner()
            copied_state.swap_player()
            copied_state.get_moves_board()

        return copied_state

    # Switches the turn at the end of a game cycle
    def swap_player(self):
        self.player = 3 - self.player

    # Function to check if a position is within the confines of the board
    def valid_pos(self, pos):
        row, col = pos
        row_cnt, col_cnt = self.board_size
        return (row >= 0 and row < row_cnt) and (col >= 0 and col < col_cnt)

    # Function to get all stones of the same color as the one in pos
    # along a certain direction described by delta
    # Used to get all the stone positions that a capturing move
    # will get
    def get_consecutive_stones(self, pos, delta):
        stones = [pos]
        row, col = pos
        d_row, d_col = delta

        row += d_row
        col += d_col
        # While pos doesn't go outside the board
        while self.valid_pos((row, col)):
            if self.board[row][col] == Stone.EMPTY or self.board[row][col].value == self.player:
                break
            stones.append((row, col))
            row += d_row
            col += d_col

        return stones

    # Gets all valid moves for the stone at stone_pos
    def get_moves_stone(self, stone_pos):
        row, col = stone_pos
        stone = self.board[row][col]
        captures = []
        paikas = []

        if stone.value == self.player:
            opposite_stone = Stone.BLACK if stone == Stone.WHITE else Stone.WHITE

            for way in Way:
                if ((row + col) % 2 != 0) and (way_to_direction[way] == Direction.DIAGONAL_1 or way_to_direction[way] == Direction.DIAGONAL_2):
                    continue

                dx, dy = way.value

                forward_1 = (row + dx, col + dy)
                forward_2 = (row + 2*dx, col + 2*dy)
                backward = (row - dx, col - dy)

                stone_ford_1 = self.board[forward_1[0]][forward_1[1]] if self.valid_pos(forward_1) else None
                stone_ford_2 = self.board[forward_2[0]][forward_2[1]] if self.valid_pos(forward_2) else None
                stone_back = self.board[backward[0]][backward[1]] if self.valid_pos(backward) else None

                if stone_ford_1 == Stone.EMPTY:
                    # Moving to the move in front is a Paika only if it doesn't capture along the line
                    if (stone_ford_2 != opposite_stone) and (stone_back != opposite_stone):
                        paikas.append(Paika((row, col), forward_1, way))
                    else:
                        # I can capture 2 cells in front of me by approach if the one in front
                        # of me is empty and the one at that position is a stone of the adversary
                        if stone_ford_2 == opposite_stone:
                            stones_captured = self.get_consecutive_stones(forward_2, (dx, dy))
                            capture = Capture((row, col), forward_1, way, CaptureType.APPROACH, stones_captured)
                            captures.append(capture)
                        # I can capture 1 cell behind me by withdrawal if the one in front
                        # of me is empty and the one at that position is a stone of the adversary
                        if stone_back == opposite_stone:
                            stones_captured = self.get_consecutive_stones(backward, (-dx, -dy))
                            capture = Capture((row, col), forward_1, way, CaptureType.WITHDRAWAL, stones_captured)
                            captures.append(capture)

        # Paikas only returned if no capture can be made
        if not captures:
            return paikas
        
        return captures

    # Takes a dummy state, and applies the effects of a capture
    # taking place in a capture sequence, to evaluate what the next possible captures
    # are after this one
    def advance_sequence(self, capture, dummy_state):
        stone = dummy_state.pop_stone(capture.origin)
        dummy_state.place_stone(capture.destination, stone)

        for captured_stone in capture.stones_captured:
            dummy_state.remove_stone(captured_stone)
    
    # Recursively builds the children of capture sequence node
    def build_capture_sequence(self, capture_node, dummy_state, sequences, sequence=None):
        if sequence is None:
            sequence = [capture_node.capture]
            sequences.append(sequence)

        self.advance_sequence(capture_node.capture, dummy_state)

        curr_stone_pos = capture_node.capture.destination
        new_moves = dummy_state.get_moves_stone(curr_stone_pos)

        # Returns if it can't continue to capture
        if not new_moves or isinstance(new_moves[0], Paika):
            return
        
        for new_capture in new_moves:
            # A capture sequence cannot return to the same position nor go in the same direction twice
            if not pos_in_seq(capture_node, new_capture.destination) and not same_dir_twice(capture_node, way_to_direction[new_capture.way]):
                child_node = CaptureSequenceNode(new_capture)
                capture_node.add_child(child_node)
                # Builds capture sequence as a list of possible sequences of captures
                # to be stored in the state variable ai_moves, and used by mcts
                new_sequence = sequence + [new_capture]
                sequences.append(new_sequence)
                self.build_capture_sequence(child_node, dummy_state, sequences, new_sequence)

    # Calls get_moves_stone for every stone in the board
    def get_moves_board(self):
        row_cnt, col_cnt = self.board_size
        captures = []
        paikas = []
        ai_captures = []

        for row in range(0, row_cnt):
            for col in range(0, col_cnt):
                moves = self.get_moves_stone((row, col))

                if moves:
                    if isinstance(moves[0], Capture):
                        for capture in moves:
                            capture_node = CaptureSequenceNode(capture)
                            sequences = []
                            self.build_capture_sequence(capture_node, deepcopy(self), sequences)

                            if capture_node.children:
                                captures.append(capture_node)
                                ai_captures += sequences
                            # If the capture node has no children, then it is a simple capture
                            # and not apart of a capture sequence
                            else:
                                captures.append(capture)
                                ai_captures.append(capture)

                    elif isinstance(moves[0], Paika):
                        paikas += moves

        # Updates both valid_moves and ai_moves, which are the valid movees
        # formatted for mcts
        if not captures:
            self.valid_moves = paikas
            self.ai_moves = paikas
        else:
            self.valid_moves = captures
            self.ai_moves = ai_captures

    # Returns the already calculated valid moves for the stone at stone_pos
    def retrieve_moves_stone(self, stone_pos):
        stone_moves = []

        for move in self.valid_moves:
            if move == 'q': continue

            origin = move.capture.origin if isinstance(move, CaptureSequenceNode) else move.origin
            
            if origin == stone_pos:
                stone_moves.append(move)

        return stone_moves