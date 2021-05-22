from ast import walk
import pygame
import time
from pygame.locals import *
from pygame import mixer


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080


screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Red Riding Hood")

# define font
font = pygame.font.SysFont("Chilanka", 30)
font_health = pygame.font.SysFont("Chilanka", 25)
#define colors
black = (0,0,0)

def draw_grid():
    for line in range(1, 33):
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (0, line * tile_size),
            (screen_width, line * tile_size),
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (line * tile_size, 0),
            (line * tile_size, screen_height),
        )

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# load images
bg_img = pygame.image.load("img/bg_img.png").convert_alpha()
background = pygame.transform.scale(bg_img, (screen_width, screen_height))

# define game variables
run = True
tile_size = 60
game_over = 0
screen_scroll  = 0
scroll_thresh = 190


#load sound
walk_fx = pygame.mixer.Sound("music/walk.wav")

jump_fx = pygame.mixer.Sound("music/jump.wav")
flower_fx = pygame.mixer.Sound("music/flower_collect.wav")
flower_fx.set_volume(0.7)
plant_fx = pygame.mixer.Sound("music/plant.wav")
atk1_fx = pygame.mixer.Sound("music/atk.wav")
mino_atk_fx = pygame.mixer.Sound("music/atk2.wav")
damage_fx = pygame.mixer.Sound("music/damage.wav")
pygame.mixer.music.load("music/Conturbatio.wav")
pygame.mixer.music.play(-1, 0.0, 1000)

class health_bar:

        
    def draw(self,health):
        pygame.draw.rect(screen,(255,0,0),(100,10,100*4,20))
        pygame.draw.rect(screen,(0,255,0),(100,10,health*4,20))

class Player:
    def __init__(self, x, y):
        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_jump = []
        self.images_left_jump = []
        self.images_right_latk = []
        self.images_left_latk = []
        self.index = 0
        self.counter = 0
        self.run_fx = False
        self.walk_music = 0
        self.jump_counter = 0
        self.jump_index = 0
        self.idle_counter = 0
        self.idle_index = 0
        self.flower_count = 0
        self.flower_counter = 0
        self.latk_index = 0
        self.latk_counter = 0
        self.light_atk_sequence = False
        self.atk_music = False
        self.health = 100 
        self.flower_cooler = 0


        for num in range(1, 4):
            img_right_idle = pygame.image.load(f"img/idle{num}.png").convert_alpha()
            img_right_idle = pygame.transform.scale(img_right_idle, (40, 80))
            img_left_idle = pygame.transform.flip(img_right_idle, True, False)
            self.images_right_idle.append(img_right_idle)
            self.images_left_idle.append(img_left_idle)
        for num in range(1, 12):
            img_right_run = pygame.image.load(f"img/run{num}.png").convert_alpha()
            img_right_run = pygame.transform.scale(img_right_run, (40, 80))
            img_left_run = pygame.transform.flip(img_right_run, True, False)
            self.images_right_run.append(img_right_run)
            self.images_left_run.append(img_left_run)
        for num in range(1, 7):
            img_right_jump = pygame.image.load(f"img/jump{num}.png").convert_alpha()
            img_right_jump = pygame.transform.scale(img_right_jump, (40, 80))
            img_left_jump = pygame.transform.flip(img_right_jump, True, False)
            self.images_right_jump.append(img_right_jump)
            self.images_left_jump.append(img_left_jump)
        for num in range(1, 9):
            img_right_latk = pygame.image.load(f"img/lightatk/latk{num}.png").convert_alpha()
            img_right_latk = pygame.transform.scale(img_right_latk, (40, 80))
            img_left_latk = pygame.transform.flip(img_right_latk, True, False)
            self.images_right_latk.append(img_right_latk)
            self.images_left_latk.append(img_left_latk)

        self.image = self.images_right_idle[self.idle_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True

    def update(self, game_over):
        if self.rect.bottom >= screen_height:
            
            self.health = 0
        screen_scroll = 0
        dx = 0
        dy = 0
        walk_cooldown = 1
        jump_cooldown = 2
        walk_music_cooldown = 20
        idle_cooldown = 8
        flower_cooldown = 8
        latk_cooldown = 2
        
        
        col_thresh = 20

        if game_over == 0:
            # get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True

            if key[pygame.K_SPACE] == False:
                self.jumped = False

            if key[pygame.K_LEFT]:
                if self.run_fx == False:
                    self.run_fx = True
                    walk_fx.play()
                dx -= 5
                self.counter += 1
                self.walk_music += 1
                self.direction = -1

            if key[pygame.K_RIGHT]:
                if self.run_fx == False:
                    self.run_fx = True
                    walk_fx.play()
                dx += 5
                self.counter += 1
                self.walk_music += 1
                self.direction = 1

            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                walk_fx.stop()
                self.run_fx = False
                self.idle_counter +=1
                if self.idle_counter > idle_cooldown:
                    self.idle_counter = 0
                    self.idle_index += 1
                    if self.idle_index >= len(self.images_right_idle):
                        self.idle_index = 0

                    if self.direction == 1:
                        self.image = self.images_right_idle[self.idle_index]
                    if self.direction == -1:
                        self.image = self.images_left_idle[self.idle_index]

            #collect flowers
            if key[pygame.K_e] and pygame.sprite.spritecollide(self,flower_group,False):
                flower_fx.play()
                flower_list = pygame.sprite.spritecollide(self,flower_group,False)
                for flower in flower_list:
                    if flower.consumed == False:
                        self.flower_count += 1
                    else:
                        self.health += 5
                    flower_group.remove(flower)
                    
                

            # plant flowers
            if key[pygame.K_f] and self.flower_cooler <= 0:
                    self.flower_counter += 1
                    if self.flower_count > 0:
                        if self.flower_counter > flower_cooldown:
                            self.flower_counter = 0
                            self.flower_count -= 1
                            flower = Flower(self.rect.x,self.rect.y + 22)
                            flower.consumed = True
                            flower_group.add(flower)
                            plant_fx.play()
                            self.flower_cooler = 50

            #use light atk
            if key[pygame.K_q]:
                if self.atk_music == False:
                    atk1_fx.play()
                    self.atk_music = True
                self.light_atk_sequence = True
                
                            

                    

                #self.latk_counter += 1
                

            

            # handle animations

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right_run):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right_run[self.index]
                if self.direction == -1:
                    self.image = self.images_left_run[self.index]

           # if self.walk_music > walk_music_cooldown and self.in_air == False:
            #    self.walk_music = 0
             #   walk_fx.play()

            
            
            if self.in_air == True:
                    self.walk_music = 0
                    walk_fx.stop()
                    self.run_fx = False
                    self.jump_index = 0
                    self.jump_index += 1
                    if self.jump_index >= len(self.images_right_jump):
                        self.jump_index = 0
                    if self.direction == 1:
                        self.image = self.images_right_jump[self.jump_index]
                    if self.direction == -1:
                        self.image = self.images_left_jump[self.jump_index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.in_air = True

            for tile in world.tile_list:
                # check for collision in x direction
                if tile[2] != False:

                    if tile[1].colliderect(
                        self.rect.x + dx, self.rect.y, self.width, self.height
                    ):
                        dx = 0

                    # check for collision in y direction
                    if tile[1].colliderect(
                        self.rect.x, self.rect.y + dy, self.width, self.height
                    ):
                        # check if below the ground i.e. jumping
                        if self.vel_y < 0:
                            dy = tile[1].bottom - self.rect.top
                            self.vel_y = 0

                        # check if above the ground i.e. falling
                        elif self.vel_y >= 0:
                            dy = tile[1].top - self.rect.bottom
                            self.vel_y = 0
                            self.in_air = False
            

            


            # update player co ordinates
            self.rect.x += dx
            self.rect.y += dy

            #update scroll
            if (self.rect.right > (screen_width - scroll_thresh)) or self.rect.left < scroll_thresh:
                
                self.rect.x -= dx
                screen_scroll = -dx

        # draw player onto the screen
        if self.light_atk_sequence == True:
            self.latk_counter += 1
            if self.latk_counter > latk_cooldown:
                self.latk_counter = 0
                
                self.latk_index += 1
                if self.latk_index >= len(self.images_right_latk):
                    self.light_atk_sequence = False
                    self.latk_index = 0
                    if pygame.sprite.spritecollide(self, minotaur_group, False):
                        minotaur_list = pygame.sprite.spritecollide(self, minotaur_group, False)
                        for minotaur in minotaur_list:
                            minotaur.health -= 50
                    self.atk_music = False
                if self.direction == 1:
                    self.image = self.images_right_latk[self.latk_index]
                if self.direction == -1:
                    self.image = self.images_left_latk[self.latk_index]
                screen.blit(self.image,self.rect)
            else:
                screen.blit(self.image, self.rect)
                #time.sleep(0.01)
        else:
            screen.blit(self.image, self.rect)
        self.flower_cooler -= 1
        if self.flower_cooler < 0:
            self.flower_cooler = 0

        return screen_scroll
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)


class World:
    def __init__(self, data):
        self.tile_list = []
        # load images
        ground_img = pygame.image.load("img/ground.png").convert_alpha()
        tree_img = pygame.image.load("img/tree.png").convert_alpha()
        box_img = pygame.image.load("img/box.png").convert_alpha()
        scarecrow_img = pygame.image.load("img/scarecrow.png").convert_alpha()
        logs_img = pygame.image.load("img/logs.png").convert_alpha()
        table_img = pygame.image.load("img/table.png").convert_alpha()
        well_img = pygame.image.load("img/well.png").convert_alpha()
        surface_img = pygame.image.load("img/surface.png").convert_alpha()
        obstacle_img = pygame.image.load("img/obstacle.png").convert_alpha()
        cart_img = pygame.image.load("img/cart.png").convert_alpha()
        wheel_img = pygame.image.load("img/wheel.png").convert_alpha()
        bush1 = pygame.image.load("img/bush1.png").convert_alpha()
        bush2 = pygame.image.load("img/bush2.png").convert_alpha()
        bush3 = pygame.image.load("img/bush3.png").convert_alpha()
        flower_3 = pygame.image.load("img/3flowers.png").convert_alpha()

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(bush1, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(bush2, (int(tile_size*1.5), int(tile_size*1.5)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2 - int(tile_size*0.5)
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(bush3, (tile_size*2, int(tile_size*1.5)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2 - int(tile_size*0.5)
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = pygame.transform.scale(flower_3, (int(tile_size * 1.5), tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - 60
                    img_rect.y = row_count * tile_size +2
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 5:
                    flower = Flower(col_count * tile_size - 20,row_count * tile_size +2)
                    flower_group.add(flower)
                    
                if tile == 6:
                    img = pygame.transform.scale(ground_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)
                if tile == 7:
                    img = pygame.transform.scale(cart_img, (tile_size*3, int(tile_size*1.5)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2 - int(tile_size*0.5)
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 8:
                    img = pygame.transform.scale(wheel_img, (int(tile_size // 1.5), int(tile_size // 1.5)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - 30
                    img_rect.y = row_count * tile_size + 2 + 20
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 9:
                    img = pygame.transform.scale(surface_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size 
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)
                if tile == 10:
                    img = pygame.transform.scale(obstacle_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size 
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)
                if tile == 11:
                    img = pygame.transform.scale(
                        tree_img, (tile_size * 4, tile_size * 6)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - tile_size * 5 +2
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 12:
                    img = pygame.transform.scale(
                        box_img, (tile_size , tile_size)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)
                if tile == 13:
                    img = pygame.transform.scale(
                        scarecrow_img, (tile_size , tile_size + 30)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - 30 +2
                    tile = (img, img_rect, False)
                    self.tile_list.append(tile)
                if tile == 14:
                    img = pygame.transform.scale(
                        logs_img, (tile_size *2, tile_size)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size +2
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)
                if tile == 15:
                    img = pygame.transform.scale(
                        well_img, (tile_size*2 , tile_size*2)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size 
                    img_rect.y = row_count * tile_size - tile_size * 1 +2
                    tile = (img, img_rect, True)
                    self.tile_list.append(tile)

                if tile == 16:
                    minotaur = Minotaur(col_count * tile_size ,row_count * tile_size - 30 )
                    minotaur_group.add(minotaur)
                
                col_count += 1
            row_count += 1

    def draw(self,screen_scroll):
        for tile in self.tile_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/1flower.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.consumed = False
    def update(self,screen_scroll):
        self.rect.x += screen_scroll
        screen.blit(self.image,self.rect)


class Minotaur(pygame.sprite.Sprite):
    def __init__(self,x,y):

        pygame.sprite.Sprite.__init__(self)
        self.health = 200
        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_atk1 = []
        self.images_left_atk1 = []
        self.images_right_ded = []
        self.images_left_ded = []
        self.index = 0
        self.counter = 0
        self.idle_index = 0
        self.idle_counter = 0
        self.direction = 1
        self.move_counter = 0
        self.move_direction = 1
        self.is_moving = False
        self.run_counter = 0
        self.iterations = 0
        self.detect_player = False
        self.atk1_index = 0
        self.atk1_counter = 0
        self.atk1_sequence = False
        self.atk1_music = False
        self.dead_counter = 0
        self.dead_index = 0
        self.alive = True
        self.ded_music = False
        self.jumped = False
        self.in_air = False



        for num in range(1, 6):
            img_right_idle = pygame.image.load(f"img/Mino_idle_list/idle{num}.png").convert_alpha()
            img_right_idle = pygame.transform.scale(img_right_idle, (tile_size + 48, 90))
            img_left_idle = pygame.transform.flip(img_right_idle, True, False)
            self.images_right_idle.append(img_right_idle)
            self.images_left_idle.append(img_left_idle)
        for num in range(1, 9):
            img_right_run = pygame.image.load(f"img/Mino_run_list/run{num}.png").convert_alpha()
            img_right_run = pygame.transform.scale(img_right_run,(tile_size + 48, 90))
            img_left_run = pygame.transform.flip(img_right_run, True, False)
            self.images_right_run.append(img_right_run)
            self.images_left_run.append(img_left_run)
        for num in range(1, 10):
            img_right_atk1 = pygame.image.load(f"img/Mino_atk_list/atk{num}.png").convert_alpha()
            img_right_atk1 = pygame.transform.scale(img_right_atk1,(tile_size + 48, 90))
            img_left_atk1 = pygame.transform.flip(img_right_atk1, True, False)
            self.images_right_atk1.append(img_right_atk1)
            self.images_left_atk1.append(img_left_atk1)
        for num in range(1, 4):
            img_right_ded = pygame.image.load(f"img/Mino_ded_list/ded{num}.png").convert_alpha()
            img_right_ded = pygame.transform.scale(img_right_ded,(tile_size + 48, 90))
            img_left_ded = pygame.transform.flip(img_right_ded, True, False)
            self.images_right_ded.append(img_right_ded)
            self.images_left_ded.append(img_left_ded)

        
        self.image = self.images_right_idle[self.idle_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.in_air = False
        self.dx = 0
        self.dy = 0

    def update(self,screen_scroll):
        if self.rect.y >= screen_height:
            self.health = 0
        if self.health <= 0:
            if self.ded_music == False:
                damage_fx.play()
                self.ded_music = True
            if self.alive == True:
                self.dead_counter += 1
                if self.dead_counter > 10:
                    self.ded(screen_scroll)
            else:
                minotaur_group.remove(self)
        else:
            detect_thresh = 100
            atk_cooldown = 10
            self.dx = 0
            self.dy = 0
            if self.atk1_sequence == True:
                self.iterations += 1
                    
                self.atk1_counter += 1
                if self.atk1_counter > atk_cooldown:
                    self.atk1_counter = 0
                    self.atk1_index += 1
                    if self.atk1_index >= len(self.images_right_atk1):
                        self.atk1_sequence = False
                        self.atk1_index = 0
                        self.atk1_music = False
                        self.iterations = 0
                    if self.atk1_index >= (len(self.images_right_atk1)//2) and self.atk1_index <= (len(self.images_right_atk1)//2):
                        if pygame.sprite.spritecollide(player, minotaur_group, False):
                            player.health -= 10

                        
                        
                    if self.direction == 1:
                        self.image = self.images_right_atk1[self.atk1_index]
                    if self.direction == -1:
                        self.image = self.images_left_atk1[self.atk1_index]
                    self.rect.x += screen_scroll
                    screen.blit(self.image,self.rect)
                    
                
            else:
                if abs(player.rect.x - self.rect.x) <= detect_thresh:
                    self.detect_player = True
                if self.detect_player == False:
                    if self.is_moving == True:
                        self.move(screen_scroll)
            
                    if self.is_moving == False:
                        self.idle(screen_scroll)
                else: 
                    self.ai(screen_scroll)
        # add gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        self.dy += self.vel_y
        #check for collision
        self.in_air = True
        for tile in world.tile_list:
                # check for collision in x direction
                if tile[2] == True and tile[1].colliderect(
                    self.rect.x + self.dx, self.rect.y, self.width, self.height
                ):
                    self.dx = 0

                # check for collision in y direction
                if tile[2] == True and tile[1].colliderect(
                    self.rect.x, self.rect.y + self.dy, self.width, self.height
                ):
                    # check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        self.dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    # check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        self.dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
                        self.jumped = False
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.rect.x += screen_scroll
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        
        

    def idle(self,screen_scroll):    
        idle_cooldown = 5
        

        self.idle_counter +=1
        if self.idle_counter > idle_cooldown:
            self.idle_counter = 0
            self.idle_index += 1
            if self.idle_index >= len(self.images_right_idle):
                self.idle_index = 0
                self.iterations += 1
                if self.iterations == 3:
                    self.is_moving = True
                    self.iterations = 0

            if self.direction == 1:
                self.image = self.images_right_idle[self.idle_index]
            if self.direction == -1:
                self.image = self.images_left_idle[self.idle_index]
        
        
        screen.blit(self.image,self.rect)
    

    def ded(self,screen_scroll):
        dead_cooldown = 5
        self.dead_counter += 1
        if self.dead_counter > dead_cooldown:
            self.dead_counter = 0
            self.dead_index += 1
            if self.dead_index >= len(self.images_right_ded):
                self.dead_index = 0
                self.dead_counter = 0
                self.alive = False

            if self.direction == 1:
                self.image = self.images_right_ded[self.dead_index]
            if self.direction == -1:
                self.image = self.images_left_ded[self.dead_index]

       
        
        screen.blit(self.image,self.rect)

    def move(self,screen_scroll):
        
        
        self.dx += self.move_direction
        self.direction = self.move_direction

        self.move_counter += 1
        self.run_counter += 1
        move_cooldown = 5
        
        if self.run_counter > move_cooldown:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(self.images_right_run):
                self.index = 0

            if self.direction == 1:
                self.image = self.images_right_run[self.index]
            if self.direction == -1:
                self.image = self.images_left_run[self.index]

        
        
        screen.blit(self.image,self.rect)

        if abs(self.move_counter) > 120:
            self.is_moving = False
            self.move_direction *= -1
            self.move_counter *= -1
            
            return

    def ai(self,screen_scroll):
        
        #collision with player
        if pygame.sprite.spritecollide(player, minotaur_group, False):
            self.atk1_sequence = True
            
            if self.atk1_music == False:
                self.iterations = 0
                mino_atk_fx.play()
                self.atk1_music = True
        
            
        if self.detect_player == True and self.atk1_sequence == False:
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
                self.dx -= 4
            else:
                self.direction = 1
                self.dx += 4
        self.run_counter += 1
        move_cooldown = 5
        
        if self.run_counter > move_cooldown:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(self.images_right_run):
                self.index = 0

            if self.direction == 1:
                self.image = self.images_right_run[self.index]
            if self.direction == -1:
                self.image = self.images_left_run[self.index]
        #make minotaur jump
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if tile[2] == True and tile[1].colliderect(
                    self.rect.x + self.dx, self.rect.y, self.width, self.height
                    ) and self.jumped == False:
                        self.vel_y -= 15
                        self.jumped = True
        
        screen.blit(self.image,self.rect)

        if self.detect_player == True and abs(player.rect.x - self.rect.x) > 300:
            self.detect_player = False

        
class Score_Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/1flower.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size // 3, int(tile_size // 1.5)))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.consumed = False
    def update(self,screen_scroll):
        screen.blit(self.image,self.rect)


            


world_data = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0  ,13,5,16,3,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,    12,6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,   12,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,11,0,0,7,8,0,4,0,11,0,3,0,10,12,6,0,15,0,10,0,4,14,11,0,3,0,10,10,0,5,1,13,0,2,13,0,1,5,11,16,0,0,1,0,0,0,0,3,12,15,0,0,0,11],
    [9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9],
    [6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6],
]

flower_group = pygame.sprite.Group()
player = Player(200, screen_height - 260 + 2)
minotaur_group = pygame.sprite.Group()
health = health_bar()

dummy_flower = Score_Flower(20,tile_size)
flower_group.add(dummy_flower)
world = World(world_data)

text_x = 0
text_x = tile_size

while run:

    clock.tick(fps)
    screen.blit(background, (0, 0))

    # draw_grid()

    world.draw(screen_scroll)
    
    draw_text("HEALTH", font_health, (255,255,255), 0 , 10)
    draw_text("X" + str(player.flower_count), font_health, (255,255,255), 40 , tile_size - 10)

    health.draw(player.health)
    flower_group.draw(screen)
    flower_group.update(screen_scroll)
    screen_scroll =  player.update(game_over)
    
    text_x += screen_scroll
    draw_text("Collect flowers for granny", font, black, text_x, 180)
    draw_text("Collect flowers using E", font, black, text_x, 220)
    draw_text("Plant flowers using F and consume them again to heal", font, black, text_x, 260)
    
    minotaur_group.draw(screen)
    minotaur_group.update(screen_scroll)
    
    if player.health <= 0:
        game_over = -1
        pass
    #print(player.health)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()
