import pygame
from utils import center_window

class STARTMENU:
    def __init__(self):
        
        pygame.init()
        pygame.display.set_caption("Main Menu")

        center_window()

        self.vertical = 440
        self.horizontal = 380
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.horizontal, self.vertical))
        self.running = True
        self.types = [[50,150,"c"],[50,210,"u"],[50,270,"u"]]
        self.boards = [[220,150,"c"],[220,210,"u"],[220,270,"u"]]
        self.endOptions = [[140,70],[140,350]]


    def draw_screen(self):
        self.screen.fill("gray")
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(self.screen, "Black", (mouse_pos[0], mouse_pos[1], 10, 10))
    

    def draw_play_exit(self):
        options = ["Play", "Exit"]
        i = 0
        for op in self.endOptions:
         
            x = op[0]
            y = op[1]

            pygame.draw.rect(self.screen, "Black", (x, y, 100, 40))
            text_surface = self.font.render(options[i], True, "White")
            text_rect = text_surface.get_rect(midleft = (x+25,y+20))
            self.screen.blit(text_surface, text_rect)
            i+=1
    
    def draw_types(self):
        options = ["H v H", "H v PC", "PC v PC"]
        i = 0
        for op in self.types:
         
            x = op[0]
            y = op[1]

            if(op[2]=="c"):
                pygame.draw.rect(self.screen, "Blue", (x, y, 100, 40))    
            else:
                pygame.draw.rect(self.screen, "Black", (x, y, 100, 40))
            text_surface = self.font.render(options[i], True, "White")
            text_rect = text_surface.get_rect(midleft = (x+5,y+20))
            self.screen.blit(text_surface, text_rect)
            i+=1

    def draw_boards(self):
        options = ["5 x 9", "7 x 11", "9 x 13"]
        i = 0
        for op in self.boards:
         
            x = op[0]
            y = op[1]
            

            if(op[2]=="c"):
                pygame.draw.rect(self.screen, "Red", (x, y, 100, 40))    
            else:
                pygame.draw.rect(self.screen, "Black", (x, y, 100, 40))
            text_surface = self.font.render(options[i], True, "White")
            text_rect = text_surface.get_rect(midleft = (x+15,y+20))
            self.screen.blit(text_surface, text_rect)
            i+=1
        
    def check_options(self,pos):
        for i in range(3):
            
            xt = self.types[i][0]
            yt = self.types[i][1]
            if(pos[0] > xt and pos [0] < 150 and pos[1] > yt and pos[1] < yt + 40):
                for j in range(3):           
                    self.types[j][2] = "u"
                self.types[i][2] = "c"

            
            xb = self.boards[i][0]
            yb = self.boards[i][1]
            if(pos[0] > xb and pos [0] < 320 and pos[1] > yb and pos[1] < yb + 40):
                for j in range(3):           
                    self.boards[j][2] = "u"
                self.boards[i][2] = "c"

    def return_options(self):
        a = 0
        b = 0
        for i in range(3):
            if self.types[i][2] == "c":
                a = i
            if self.boards[i][2] == "c":
                b = i
        return(a,b)
    

    def check_play_exit(self,pos): 
        for i in range(2):
            x = self.endOptions[i][0]
            y = self.endOptions[i][1]
            if(pos[0] > x and pos [0] < 230 and pos[1] > y and pos[1] < y + 40):
                return i
            
        return None
        

    def draw_menu(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        self.running = True
                        self.check_options(mouse_pos)
                        choice = self.check_play_exit(mouse_pos)
                        if(choice != None):
                            if(choice == 1):
                                self.running = False
                                return None
                            else:
                                options = self.return_options()
                                return(options)
                        
            self.draw_screen()
            self.draw_play_exit()
            self.draw_types()
            self.draw_boards()

            pygame.display.flip()
