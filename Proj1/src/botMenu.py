import pygame
from utils import center_window



class IAMENU:
    def __init__(self, mode):
        
        pygame.init()
        pygame.display.set_caption("IA Menu")

        center_window()
        self.mode = mode
        self.vertical = 440
        self.horizontal = 380
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.horizontal, self.vertical))
        self.running = True
        self.ia1 = [[50,150,"c"],[50,210,"u"],[50,270,"u"]]
        self.ia2 = [[220,150,"c"],[220,210,"u"],[220,270,"u"]]
        self.endOptions = [[140,30],[140,350]]


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
    
    def draw_ia1(self):
        options = ["Easy", "Medium", "Hard"]
        i = 0
        text_surface = self.font.render("IA 1", True, "Black")
        text_rect = text_surface.get_rect(midleft = (75,120))
        self.screen.blit(text_surface, text_rect)
        for op in self.ia1:
         
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

    def draw_ia2(self):
        options = ["Easy", "Medium", "Hard"]
        i = 0
        text_surface = self.font.render("IA 2", True, "Black")
        text_rect = text_surface.get_rect(midleft = (245,120))
        self.screen.blit(text_surface, text_rect)

        for op in self.ia2:
        
            x = op[0]
            y = op[1]
            

            if(op[2]=="c"):
                pygame.draw.rect(self.screen, "Red", (x, y, 100, 40))    
            else:
                pygame.draw.rect(self.screen, "Black", (x, y, 100, 40))
            text_surface = self.font.render(options[i], True, "White")
            text_rect = text_surface.get_rect(midleft = (x+5,y+20))
            self.screen.blit(text_surface, text_rect)
            i+=1
        
    def check_options(self,pos):
        for i in range(3):
            
            xt = self.ia1[i][0]
            yt = self.ia1[i][1]
            if(pos[0] > xt and pos [0] < 150 and pos[1] > yt and pos[1] < yt + 40):
                for j in range(3):           
                    self.ia1[j][2] = "u"
                self.ia1[i][2] = "c"

            if(self.mode ==2):
                xb = self.ia2[i][0]
                yb = self.ia2[i][1]
                if(pos[0] > xb and pos [0] < 320 and pos[1] > yb and pos[1] < yb + 40):
                    for j in range(3):           
                        self.ia2[j][2] = "u"
                    self.ia2[i][2] = "c"

    def return_options(self):
        a = 0
        b = 0
        for i in range(3):
            if self.ia1[i][2] == "c":
                a = i
            if self.ia2[i][2] == "c":
                b = i
        if(self.mode == 2):
            return(a,b)
        else:
            return a
    

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
            self.draw_ia1()
            if(self.mode == 2): self.draw_ia2()

            pygame.display.flip()
