import sys, copy, random, argparse, os

from game import Game, cards, HIT, STAND, WIN_STATE, LOSE_STATE
from ai import Agent

from test import *

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,139)
GREEN = (0x44,0xff,0x44)
RED = (0xff, 0x44, 0x44)

PADDING = 5

GAME_OVER_TEXT_POS = (240, 20)

OPS_BTN_Y = 430
OPS_TXT_Y = OPS_BTN_Y + 3

OPS_INSTR_X = 10
OPS_INSTR_Y = 460

OPS_BTN_HEIGHT = 23

USR_CARD_HEIGHT = 275

class GameRunner:
    def __init__(self):
        self.game = Game()
        self.agent = Agent()

        self.autoMC = False
        self.autoTD = False
        self.autoQL = False
        self.autoPlay = False

        card_path = 'resources/cards/'
        self.card_imgs = {}
        for (rank, suit) in cards:
            self.card_imgs[(rank, suit)] = pygame.image.load(os.path.join(card_path, f"{rank}_{suit}.png"))
        self.cBack = pygame.image.load('resources/cardback.png')

        self.init_display()
        self.render_board()
        

    def init_display(self):
        #Initialize Game
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Blackjack')
        self.font = pygame.font.SysFont("arial", 15)
        
        self.hitTxt = self.font.render('[H]it', 1, BLACK)
        self.standTxt = self.font.render('[S]tand', 1, BLACK)

        modes = ["off", "on"]
        self.MCTxt = [self.font.render('[M]C - ' + mode, 1, BLUE) for mode in modes]
        self.TDTxt = [self.font.render('[T]D - ' + mode, 1, BLUE) for mode in modes]
        self.QLTxt = [self.font.render('[Q]L - ' + mode, 1, BLUE) for mode in modes]
        self.playTxt = [self.font.render('[A]uto Play - ' + mode, 1, BLUE) for mode in modes]
        self.gameoverTxt = [self.font.render('End of Round. You WON!', 1, RED), self.font.render('End of Round. You LOST!', 1, RED)]

        self.ops_instr = self.font.render('Click on the button or type the initial character of the operation to play or toggle modes', 1, BLACK)
        self.save_instr = self.font.render('Press 1 to save AI state', 1, BLACK)
        self.load_instr = self.font.render('Press 2 to load from AI\'s saved state', 1, BLACK)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0x00, 0x62, 0xbe))
        self.hitB = pygame.draw.rect(self.background, WHITE, (10, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.standB = pygame.draw.rect(self.background, WHITE, (95, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))

        
    def loop(self):
        while True:
            # Our state information does not take into account of number of cards
            
            if self.autoMC:
                #MC Learning
                #Compute the values of all states under the default policy (see ai.py)
                self.agent.MC_run(50)
            if self.autoTD:
                #TD Learning
                #Compute the values of all states under the default policy (see ai.py)
                self.agent.TD_run(50)
            if self.autoQL:
                #Q-Learning
                #For each state, compute the Q value of the action "Hit" and "Stand"
                self.agent.Q_run(50)
            
            if self.autoPlay:
                if self.game.game_over() or self.game.stand:
                    self.game.update_stats()
                    self.game.reset()

                decision = self.agent.autoplay_decision(copy.deepcopy(self.game.state))
                if decision == 0:
                    self.game.act_hit()
                else:
                    self.game.act_stand()
                
            self.handle_user_action()
            self.render_board()
            
    def check_act_MC(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.MCB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_m
        return clicked or pressed

    def check_act_TD(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.TDB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_t
        return clicked or pressed

    def check_act_QL(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.QLB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_q
        return clicked or pressed
    
    def check_act_autoplay(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.playB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_a
        return clicked or pressed

    def check_act_hit(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.hitB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_h

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_stand(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.standB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_s

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_reset(self, event):
        clicked = event.type == MOUSEBUTTONDOWN
        pressed = event.type == KEYDOWN

        return self.game.game_over() and not self.autoPlay and (clicked or pressed)
    
    def handle_user_action(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Clicking the white buttons can start or pause the learning processes
            elif self.check_act_MC(event):
                self.autoMC = not self.autoMC
            elif self.check_act_TD(event):
                self.autoTD = not self.autoTD
            elif self.check_act_QL(event):
                self.autoQL = not self.autoQL
            elif self.check_act_autoplay(event):
                self.autoPlay = not self.autoPlay
            
            elif self.check_act_hit(event):
                self.game.act_hit()
                
            elif self.check_act_stand(event):
                self.game.act_stand()

            elif self.check_reset(event):
                self.game.update_stats()
                self.game.reset()
            
            if event.type == KEYDOWN:
                if event.key == K_x:
                    pygame.quit()
                    sys.exit()
                if event.key == K_1:
                    self.agent.save("saved")
                elif event.key == K_2:
                    self.agent.load("saved")
    
    @staticmethod
    def draw_label_hl(surface, pos, label, padding=PADDING, bg=WHITE, wd=2, border=True):
        specs = [(bg, 0)]
        if border:
            specs += [(BLACK, wd)]
        for color, width in specs:
            x = pos[0] - padding
            y = pos[1] - padding
            w = label.get_width() + padding * 2
            h = label.get_height() + padding * 2
            pygame.draw.rect(surface, color, (x, y, w, h), width)

    def render_board(self):
        winTxt = self.font.render('Wins: {}'.format(self.game.winNum), 1, WHITE)
        loseTxt = self.font.render('Losses: {}'.format(self.game.loseNum), 1, WHITE)
        if self.game.loseNum == 0 and self.game.winNum == 0:
            win_rate = 0.
        else:
            win_rate = self.game.winNum / (self.game.winNum + self.game.loseNum)
        win_rate_txt = self.font.render('Win rate: {:.2f}%'.format(win_rate * 100), 1, WHITE)
            
        button_colors = [RED, GREEN]
        self.MCB = pygame.draw.rect(self.background, button_colors[self.autoMC], (180, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.TDB = pygame.draw.rect(self.background, button_colors[self.autoTD], (265, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.QLB = pygame.draw.rect(self.background, button_colors[self.autoQL], (350, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.playB = pygame.draw.rect(self.background, button_colors[self.autoPlay], (435, OPS_BTN_Y, 115, OPS_BTN_HEIGHT))


        state_info = self.font.render('State (user_sum, user_has_Ace, dealer_first) ={}'.format(self.game.state), 1, BLACK)
        MCU = self.font.render('Current state\'s (MC value, #samples): ({:f}, {})'.format(
            self.agent.MC_values[self.game.state], 
            self.agent.N_MC[self.game.state]
        ), 1, BLACK)

        TDU = self.font.render('Current state\'s (TD value, #samples): ({:f}, {})'.format(
            self.agent.TD_values[self.game.state], 
            self.agent.N_TD[self.game.state]
        ), 1, BLACK)

        QV = self.font.render('Current stats\'s Q values ([Hit, Stand], #samples): ([{:f},{:f}], {})'.format(
            self.agent.Q_values[self.game.state][0],
            self.agent.Q_values[self.game.state][1],
            self.agent.N_Q[self.game.state],
        ) , 1, BLACK)
        
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.hitTxt, (37, OPS_TXT_Y))
        self.screen.blit(self.standTxt, (113, OPS_TXT_Y))
        self.screen.blit(self.MCTxt[self.autoMC], (190, OPS_TXT_Y))
        self.screen.blit(self.TDTxt[self.autoTD], (277, OPS_TXT_Y))
        self.screen.blit(self.QLTxt[self.autoQL], (359, OPS_TXT_Y))
        self.screen.blit(self.playTxt[self.autoPlay], (444, OPS_TXT_Y))
        self.screen.blit(self.ops_instr, (OPS_INSTR_X, OPS_INSTR_Y))

        for width, color in [(0, WHITE), (2, BLACK)]:
            pygame.draw.rect(self.screen, color,
                (10, 170, 600, 95), width)
        self.screen.blit(state_info, (20, 180))
        self.screen.blit(MCU, (20, 200))
        self.screen.blit(TDU, (20, 220))
        self.screen.blit(QV, (20, 240))

        self.screen.blit(winTxt, (520, 23))
        self.screen.blit(loseTxt, (520, 48))
        self.screen.blit(win_rate_txt, (520, 73))

        self.screen.blit(self.save_instr, (350, 380))
        self.screen.blit(self.load_instr, (350, 400))

        for i, card in enumerate(self.game.userCard):
            x = 10 + i * 20
            self.screen.blit(self.card_imgs[card], (x, USR_CARD_HEIGHT))
        
        if self.game.game_over() or self.game.stand:
            if self.game.state == WIN_STATE:
                result_txt = self.gameoverTxt[0]
            else:
                result_txt = self.gameoverTxt[1]
            self.draw_label_hl(self.screen, GAME_OVER_TEXT_POS, result_txt)
            self.screen.blit(result_txt, GAME_OVER_TEXT_POS)
            for i, card in enumerate(self.game.dealCard):
                x = 10 + i * 20
                self.screen.blit(self.card_imgs[card], (x, 10))
        else:
            self.screen.blit(self.card_imgs[self.game.dealCard[0]], (10, 10))
            self.screen.blit(self.cBack, (30, 10))

        pygame.display.update()


parser = argparse.ArgumentParser(description='Blackjack')
parser.add_argument('--test', '-t', dest="test", type=int, default=0, \
    help='1: test three steps (deterministic), \
          2: test for divergence (100k steps, asymptotic), \
          3: test for convergence (1 million steps, asymptotic)'
)
parser.add_argument('--algorithm', '-a', dest="algorithm", type=int, default=0, help='0: all, 1: MC, 2: TD, 3: Q-Learning')
args = parser.parse_args()

if __name__ == '__main__':
    if args.test == 1:
        test_three_steps(args.algorithm)
    elif args.test == 2:
        test_divergence(args.algorithm)
    elif args.test == 3:
        test_convergence(args.algorithm)
    else:
        import pygame
        from pygame.locals import *
        ROTATIONS = {pygame.K_UP: 0, pygame.K_DOWN: 2, pygame.K_LEFT: 1, pygame.K_RIGHT: 3}
        game = GameRunner()
        game.loop()