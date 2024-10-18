import time

from enum import Enum
from state import *
from gui import *
from minimax import *
from mcts import *
from startMenu import *
from botMenu import *

class GameType(Enum):
    HUMAN_HUMAN = 1
    HUMAN_COMPUTER = 2
    COMPUTER_COMPUTER = 3


class AiType(Enum):
    EASY = make_minimax_move(eval_f1, 2)
    # Eval_f2 was the one that generally gave us the best results in minimax
    MEDIUM = make_negamax_move(eval_f2, 5)
    # Ai that gave us the best results
    HARD = make_mcts_move(10)


# Function that represents a play made by a human player
def human_player(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if game.gui.in_sequence:
                    game.state = game.state.apply_move('q')
                    game.gui.pressed_moves = []
                    game.gui.draw = True
                    game.gui.in_sequence = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = event.pos

                if game.gui.mouse_inside_board(mouse_pos):
                    closest_stone = game.gui.get_closest_stone_pos_to_mouse(mouse_pos)
                    row, col = closest_stone

                    if row is not None and col is not None:
                        if game.gui.decision:
                            option1 = game.gui.decision[0].capture.stones_captured[0] if isinstance(game.gui.decision[0], CaptureSequenceNode) else game.gui.decision[0].stones_captured[0]
                            option2 = game.gui.decision[1].capture.stones_captured[0] if isinstance(game.gui.decision[1], CaptureSequenceNode) else game.gui.decision[1].stones_captured[0]

                            applied_move = None
                            if (row, col) == option1:
                                applied_move = game.gui.decision[0]
                            elif (row, col) == option2:
                                applied_move = game.gui.decision[1]

                            if applied_move is not None:
                                game.state = game.state.apply_move(applied_move)
                                if isinstance(applied_move, CaptureSequenceNode):
                                    if applied_move.children:
                                        if not game.gui.in_sequence:
                                            game.gui.in_sequence = True
                                    else:
                                        game.gui.in_sequence = False

                                game.gui.decision = []

                        elif game.state.board[row][col].value == game.state.player:
                            game.gui.pressed_moves = game.state.retrieve_moves_stone((row, col))

                        elif game.gui.pressed_moves:
                            chosen_moves = []

                            for move in game.gui.pressed_moves:
                                if move == 'q':
                                    continue
                                elif isinstance(move, CaptureSequenceNode):
                                    if (row, col) == move.capture.destination:
                                        chosen_moves.append(move)
                                elif (row, col) == move.destination:
                                    chosen_moves.append(move)

                            if len(chosen_moves) == 2:
                                game.gui.decision += chosen_moves
                            elif len(chosen_moves) == 1:
                                applied_move = chosen_moves[0]
                                game.state = game.state.apply_move(applied_move)

                                if isinstance(applied_move, CaptureSequenceNode):
                                    if applied_move.children:
                                        if not game.gui.in_sequence:
                                            game.gui.in_sequence = True
                                    else:
                                        game.gui.in_sequence = False

                            game.gui.pressed_moves = []
                    else:
                        game.gui.pressed_moves = []
                else:
                    game.gui.pressed_moves = []

                game.gui.draw = True

        elif event.type == pygame.MOUSEMOTION:
            game.gui.draw = True


class FanoronaTsivy:
    def __init__(self, game_type, player_1_ai, player_2_ai, dimensions):
        self.gui = None
        self.game_type = game_type
        self.player_1_ai = player_1_ai
        self.player_2_ai = player_2_ai
        self.vertical, self.horizontal = dimensions

    def play(self, log_moves = False):
        self.state = State(self.vertical,self.horizontal)
        
        if self.game_type != GameType.COMPUTER_COMPUTER or log_moves:
            self.gui = GUI((self.vertical, self.horizontal))
            self.gui.draw_game(self.state)

        self.running = True
        while self.running:
            if self.game_type == GameType.HUMAN_HUMAN:
                human_player(self)
            elif self.game_type == GameType.HUMAN_COMPUTER:
                if self.state.player == 1:
                    human_player(self)
                elif self.state.player == 2:
                    self.player_1_ai(self)
                    self.gui.draw = True
            elif self.game_type == GameType.COMPUTER_COMPUTER:
                if self.state.player == 1:
                    self.player_1_ai(self)
                elif self.state.player == 2:
                    self.player_2_ai(self)

                if self.gui is not None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False

                    self.gui.draw = True

            if self.gui is not None:
                if self.gui.draw:
                    self.gui.draw_game(self.state)
                    self.gui.draw = False

            if self.state.winner != -1:
                if self.gui is not None:
                    if self.state.winner == 0:
                        print("\nDRAW")
                    else:
                        print(f"\nPLAYER {self.state.winner} WINS. CONGRATULATIONS!!!")
                self.running = False

        if self.gui is not None:
            pygame.quit()

    def run_n_matches(self, n, max_time = 3600, log_moves = False):
        self.game_type = GameType.COMPUTER_COMPUTER

        start_time = time.time()

        results = [0, 0, 0] # [draws, player_1_wins, player_2_wins]

        while n > 0 and time.time() - start_time < max_time:
            n -= 1
            self.play(log_moves)
            results[self.state.winner] += 1

        print(f"=== Elapsed time: {int(time.time() - start_time)} seconds ===")
        print(f"  Player 1: {results[1]} wins")
        print(f"  Player 2: {results[2]} wins")
        print(f"  Draws: {results[0]}")

menu = STARTMENU()
menuOption = menu.draw_menu()
if menuOption is not None:
    type = GameType(menuOption[0]+1)
    ia1 = ia2 = None
    test = None

    if type == GameType.HUMAN_COMPUTER or type == GameType.COMPUTER_COMPUTER:
        menuIa = IAMENU(1 if type == GameType.HUMAN_COMPUTER else 2)
        menuIaOption = menuIa.draw_menu()

        if menuIaOption is not None:
            if isinstance(menuIaOption, int):
                ia1 = AiType.EASY if menuIaOption == 0 else AiType.MEDIUM if menuIaOption == 1 else AiType.HARD
            else:
                ia1 = AiType.EASY if menuIaOption[0] == 0 else AiType.MEDIUM if menuIaOption[0] == 1 else AiType.HARD
                ia2 = AiType.EASY if menuIaOption[1] == 0 else AiType.MEDIUM if menuIaOption[1] == 1 else AiType.HARD
        else:
            test = -1

    v = 5 + menuOption[1] * 2
    h = v + 4
    
    game = FanoronaTsivy(type, ia1, ia2,(v,h)) #Board size can be changed here

    if(test!=-1):  
        game.play(log_moves=True)