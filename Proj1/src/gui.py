import pygame
from pygame import gfxdraw
from state import Stone, Capture, CaptureSequenceNode
from utils import center_window

class GUI:
    def __init__(self, board_size):
        self.board_start_x = 200
        self.board_start_y = 160
        self.board_interval = 100
        self.row_cnt, self.col_cnt = board_size
        self.board_last_x = self.board_start_x + self.board_interval*(self.col_cnt - 1)
        self.board_last_y = self.board_start_y + self.board_interval*(self.row_cnt - 1)
        self.board_gui_positions = [[(self.board_start_x + self.board_interval*col, self.board_start_y + self.board_interval*row)
                            for col in range(self.col_cnt)] for row in range(self.row_cnt)]
        self.stone_rad = 20

        pygame.init()
        pygame.display.set_caption("Fanorana-Tsivy")

        center_window()

        display = self.init_display() # Inits display accordlying to the number of pieces
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode(display)

        self.pressed_moves = []
        self.decision = []
        self.in_sequence = False
        self.draw = False

    # Initialize the display size based on the board size
    def init_display(self):
        y = self.row_cnt*100 + 200
        x = self.col_cnt*100 + 300
        return(x,y)

    # Draw the current player's turn on the screen
    def draw_turn(self, pos, turn):
        if(turn == 1):
            text_surface = self.font.render("White's Turn", True, "White")
            text_rect = text_surface.get_rect(midleft = pos)
            self.screen.blit(text_surface, text_rect)
        elif(turn == 2):
            text_surface = self.font.render("Black's Turn", True, "Black")
            text_rect = text_surface.get_rect(midleft = pos)
            self.screen.blit(text_surface, text_rect)
    

    # Draw the remaining stones for each player on the screen
    def draw_stones_left(self, pos, stones_left):
        text_surface = self.font.render("White: " + str(stones_left[0]) + " Black: " + str(stones_left[1]), True, "Black")
        text_rect = text_surface.get_rect(midright = pos)
        self.screen.blit(text_surface, text_rect)


    # Draw a warning to finish the turn on the screen
    def draw_sequence_warning(self, pos):
        text_surface = self.font.render("FINISH TURN - Q", True, "Red")
        text_rect = text_surface.get_rect(center = pos)
        self.screen.blit(text_surface, text_rect)


    # Draw the lines of the board on the screen
    def draw_board_lines(self):
        # Horizontal Lines
        for row in range(self.row_cnt):
            pygame.draw.line(self.screen, "black", self.board_gui_positions[row][0], self.board_gui_positions[row][self.col_cnt - 1], 2)

        # Vertical Lines
        for col in range(self.col_cnt):
            pygame.draw.line(self.screen, "black", self.board_gui_positions[0][col], self.board_gui_positions[self.row_cnt - 1][col], 2)
        
        # Diagonal Lines Leaning Left
        start_row, start_col = (0, 0)
        end_row, end_col = (0, 0)
        limit_row, limit_col = (self.row_cnt//2*2, self.col_cnt//2*2)

        while start_col < (limit_col - 2) and end_row < (limit_row - 2):
            
            if (start_row == limit_row):
                start_col += 2
            else:
                start_row += 2

            if (end_col == limit_col):
                end_row += 2
            else:
                end_col += 2

            pygame.draw.line(self.screen, "black", self.board_gui_positions[start_row][start_col], self.board_gui_positions[end_row][end_col], 2)

        # Diagonal Lines Leaning Right
        start_row, start_col = ((self.row_cnt - 1), 0)
        end_row, end_col = ((self.row_cnt - 1), 0)
        limit_row, limit_col = (0, self.col_cnt//2*2)

        while start_col < (limit_col - 2) and end_row > (limit_row + 2):
            
            if (start_row == limit_row):
                start_col += 2
            else:
                start_row -= 2

            if (end_col == limit_col):
                end_row -= 2
            else:
                end_col += 2

            pygame.draw.line(self.screen, "black", self.board_gui_positions[start_row][start_col], self.board_gui_positions[end_row][end_col], 2)


    # Draw a stone on the screen at the given position
    def draw_stone(self, stone, pos):
        x, y = pos
        if stone == Stone.WHITE:
            gfxdraw.aacircle(self.screen, x, y, self.stone_rad, (255, 255, 255))
            gfxdraw.filled_circle(self.screen, x, y, self.stone_rad, (255, 255, 255))
        elif stone == Stone.BLACK:
            gfxdraw.aacircle(self.screen, x, y, self.stone_rad, (0, 0, 0))
            gfxdraw.filled_circle(self.screen, x, y, self.stone_rad, (0, 0, 0))

    # Draw all the stones on the board
    def draw_stones(self, board):
        for row in range(self.row_cnt):
            for col in range(self.col_cnt):
                stone = board[row][col]
                pos = self.board_gui_positions[row][col]
                self.draw_stone(stone, pos)

    # Highlight with red the stones that are able to perform a valid move
    def draw_valid_moves(self, valid_moves):
        origins = set(move.capture.origin if isinstance(move, CaptureSequenceNode) else move.origin for move in valid_moves if move != 'q')

        for (row, col) in origins:
            pos = self.board_gui_positions[row][col]
            x, y = pos
            gfxdraw.aacircle(self.screen, x, y, int(self.stone_rad*0.5), (200, 0, 0))
            gfxdraw.filled_circle(self.screen, x, y, int(self.stone_rad*0.5), (200, 0, 0))

    # Highlight with green the valid moves of a selected stones
    def draw_pressed_moves(self, pressed_cell):
        pressed_row, pressed_col = pressed_cell
        pressed_x, pressed_y = self.board_gui_positions[pressed_row][pressed_col]
        gfxdraw.aacircle(self.screen, pressed_x, pressed_y, int(self.stone_rad*0.75), (0, 255, 0))
        gfxdraw.filled_circle(self.screen, pressed_x, pressed_y, int(self.stone_rad*0.75), (0, 255, 0))

        for move in self.pressed_moves:
            if move == 'q': continue
            elif isinstance(move, CaptureSequenceNode):
                move = move.capture

            dest_row, dest_col = move.destination
            dest_x, dest_y = self.board_gui_positions[dest_row][dest_col]
            gfxdraw.aacircle(self.screen, dest_x, dest_y, self.stone_rad, (0, 0, 255))
            gfxdraw.filled_circle(self.screen, dest_x, dest_y, self.stone_rad, (0, 0, 255))

            if isinstance(move, Capture):
                for (row, col) in move.stones_captured:
                    captured_x, captured_y = self.board_gui_positions[row][col]
                    gfxdraw.aacircle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (255, 255, 0))
                    gfxdraw.filled_circle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (255, 255, 0))

    # Highlight with orange the final position of the stone played and with purple the stones that can be captured
    def draw_decision(self):
        capture1 = self.decision[0].capture if isinstance(self.decision[0], CaptureSequenceNode) else self.decision[0]
        capture2 = self.decision[1].capture if isinstance(self.decision[1], CaptureSequenceNode) else self.decision[1]
        row, col = capture1.destination
        dest_x, dest_y = self.board_gui_positions[row][col]
        gfxdraw.aacircle(self.screen, dest_x, dest_y, self.stone_rad, (255, 165, 0))
        gfxdraw.filled_circle(self.screen, dest_x, dest_y, self.stone_rad, (255, 165, 0))

        for (row, col) in capture1.stones_captured:
            captured_x, captured_y = self.board_gui_positions[row][col]
            gfxdraw.aacircle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (128, 0, 128))
            gfxdraw.filled_circle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (128, 0, 128))

        for (row, col) in capture2.stones_captured:
            captured_x, captured_y = self.board_gui_positions[row][col]
            gfxdraw.aacircle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (128, 0, 128))
            gfxdraw.filled_circle(self.screen, captured_x, captured_y, int(self.stone_rad*0.75), (128, 0, 128))

    # Draw the entire game on the screen
    def draw_game(self, state):
        self.screen.fill("gray")

        self.draw_turn((self.board_start_x, self.board_start_y//2), state.player)
        self.draw_stones_left((self.board_last_x, self.board_start_y//2), state.stones_remaining)
        if self.in_sequence:
            self.draw_sequence_warning((self.board_start_x + (self.board_last_x - self.board_start_x)//2, self.board_start_y//2))
        self.draw_board_lines()
        self.draw_stones(state.board)
        if self.decision:
            self.draw_decision()
        else:
            if state.valid_moves:
                self.draw_valid_moves(state.valid_moves)
            if self.pressed_moves:
                if isinstance(self.pressed_moves[0], CaptureSequenceNode):
                    pressed_cell = self.pressed_moves[0].capture.origin
                else:
                    pressed_cell = self.pressed_moves[0].origin

                self.draw_pressed_moves(pressed_cell)


        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(self.screen, "Black", (mouse_pos[0], mouse_pos[1], 10, 10))

        pygame.display.flip()

    # Check if the mouse is inside the board
    def mouse_inside_board(self, pos):
        x, y = pos
        return (self.board_start_x - self.stone_rad) < x < (self.board_last_x + self.stone_rad) and (self.board_start_y - self.stone_rad) < y < (self.board_last_y + self.stone_rad)

    # Round the mouse position to the nearest board position
    def round_to_nearest_coord(self, coord, start, cnt):
        if coord < start:
            nearest = start
        elif coord > start + self.board_interval*cnt:
            nearest = start + self.board_interval*cnt
        else:
            nearest = start + round((coord - start)/self.board_interval)*self.board_interval

            
        if abs(nearest - coord) <= self.stone_rad:
            return nearest
        else:
            return None

    # Get the position of the stone closest to the mouse
    def get_closest_stone_pos_to_mouse(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        nearest_x = self.round_to_nearest_coord(mouse_x, self.board_start_x, self.col_cnt)
        nearest_y = self.round_to_nearest_coord(mouse_y, self.board_start_y, self.row_cnt)


        row = (nearest_y - self.board_start_y)//self.board_interval if nearest_y != None else nearest_y
        col = (nearest_x - self.board_start_x)//self.board_interval if nearest_x != None else nearest_x

        return (row, col)