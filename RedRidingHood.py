from ast import walk
import pygame
import time
from pygame.locals import *
from pygame import mixer
import random


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60
tile_size = 60
screen_width = 1920
screen_height = 1080 - tile_size


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Red Riding Hood")
pygame.mixer.set_num_channels(100)

# define font
font = pygame.font.Font("AmaticSC-Bold.ttf", 35)
font_health = pygame.font.Font("AmaticSC-Bold.ttf", 30)
# define colors
black = (0, 0, 0)


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
bg_img = pygame.image.load("img/dark-forest-background-hd-1080p-90357.jpg").convert()
background = pygame.transform.scale(bg_img, (screen_width, screen_height))

# define game variables
run = True

game_over = 0
screen_scroll = 0
scroll_thresh = 200


# load sound
walk_fx = pygame.mixer.Sound("music/walk.wav")

jump_fx = pygame.mixer.Sound("music/jump.wav")
flower_fx = pygame.mixer.Sound("music/flower_collect.wav")
flower_fx.set_volume(0.7)
plant_fx = pygame.mixer.Sound("music/plant.wav")
atk1_fx = pygame.mixer.Sound("music/atk.wav")
wiz_atk_fx = pygame.mixer.Sound("music/wiz_atk_fx.wav")
thunder_fx = pygame.mixer.Sound("music/thunder.wav")

mino_atk_fx = pygame.mixer.Sound("music/atk2.wav")
damage_fx = pygame.mixer.Sound("music/damage.wav")
arrow_release_fx = pygame.mixer.Sound("music/arrow_release.wav")
arrow_hit_fx = pygame.mixer.Sound("music/arrow_hit.wav")
growl_fx = pygame.mixer.Sound("music/mino_growl.wav")
screech_fx = pygame.mixer.Sound("music/GIRLS.wav")
screech_fx.set_volume(0.3)
bg1 = pygame.mixer.Sound("music/kaze.wav")
bg1.set_volume(0.3)
channel0 = pygame.mixer.Channel(0)
channel1 = pygame.mixer.Channel(1)
channel2 = pygame.mixer.Channel(2)

bg2 = pygame.mixer.Sound("music/davyjones.wav")
bg2.set_volume(0.5)
bg3 = pygame.mixer.Sound("music/rain.wav")
bg3.set_volume(0.3)
channel0.play(bg1, -1)
channel1.play(bg2, -1)
channel2.play(bg3, -1)

SCREENSIZE = screen_width, screen_height


class Rain(object):
    def __init__(
        self, screen, height=160, speed=3, color=(180, 215, 228, 255), numdrops=10
    ):
        "Create and reuse raindrop particles"
        self.screen = screen
        self.drops = []
        self.height = height
        self.speed = speed
        self.color = color
        self.numdrops = numdrops

        for i in range(self.numdrops):
            # Randomize the size of the raindrop.
            raindropscale = random.randint(40, 100) / 100.0
            w, h = 3, int(raindropscale * self.height)
            # The bigger the raindrop, the faster it moves.
            velocity = raindropscale * self.speed / 10.0
            pic = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
            colorinterval = float(self.color[3] * raindropscale) / h
            r, g, b = self.color[:3]
            for j in range(h):
                # The smaller the raindrop, the dimmer it is.
                a = int(colorinterval * j)
                pic.fill((r, g, b, a), (1, j, w - 2, 1))
                pygame.draw.circle(pic, (r, g, b, a), (1, h - 2), 2)
            drop = Rain.Drop(self.speed, velocity, pic)
            self.drops.append(drop)

    def Timer(self, now):
        "Render the rain"
        dirtyrects = []
        for drop in self.drops:
            r = drop.Render(self.screen, now)
            if r:
                i = r.collidelist(dirtyrects)
                if i > -1:
                    dirtyrects[i].union_ip(r)
                else:
                    dirtyrects.append(r)
        return dirtyrects

    def AdjustSpeed(self, adj):
        newspeed = self.speed + adj
        newspeed = max(1, newspeed)
        newspeed = min(100, newspeed)
        self.speed = newspeed
        for drop in self.drops:
            drop.SetSpeed(newspeed)
        print("Rain speed: %d" % newspeed)

    class Drop(object):
        "Rain drop used by rain generator"
        nexttime = 0  # The next time the raindrop will draw
        interval = 0.01  # How frequently the raindrop should draw

        def __init__(self, speed, scale, pic):
            "Initialize the rain drop"
            self.speed = speed
            self.scale = scale
            self.pic = pic
            self.size = pic.get_size()
            self.SetSpeed(speed)
            self.pos = [
                random.random() * SCREENSIZE[0],
                -random.randint(-SCREENSIZE[1], SCREENSIZE[1]),
            ]
            self.currentspeed = speed

        def SetSpeed(self, speed):
            "Speed up or slow down the drop"
            self.speed = speed
            self.velocity = self.scale * self.speed / 10.0

        def Reset(self):
            "Restart the drop at the top of the screen."
            self.pos = [
                random.random() * SCREENSIZE[0],
                -random.random() * self.size[1] - self.size[1],
            ]
            self.currentspeed = self.speed

        def Render(self, screen, now):
            "Draw the rain drop"
            if now < self.nexttime:
                return None
            self.nexttime = now + self.interval
            oldrect = pygame.Rect(
                self.pos[0], self.pos[1], self.size[0], self.size[1] + self.currentspeed
            )
            self.pos[1] += self.currentspeed
            newrect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            r = oldrect.union(newrect)
            screen.blit(self.pic, self.pos)
            self.currentspeed += self.velocity
            if self.pos[1] > SCREENSIZE[1]:
                self.Reset()
            return r


class health_bar:
    def draw(self, health):
        pygame.draw.rect(screen, (255, 0, 0), (100, 10, 100 * 4, 20))
        pygame.draw.rect(screen, (0, 255, 0), (100, 10, health * 4, 20))


class Player:
    def __init__(self, x, y):

        self.speed = 5
        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_jump = []
        self.images_left_jump = []
        self.images_right_latk = []
        self.images_left_latk = []
        self.images_right_shoot = []
        self.images_left_shoot = []
        self.images_right_ded = []
        self.images_left_ded = []
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
        self.latk_dmg = 50
        self.light_atk_sequence = False
        self.atk_music = False
        self.health = 100
        self.flower_cooler = 0
        self.shoot_index = 0
        self.shoot_counter = 0
        self.shoot_sequence = False
        self.shoot_music = False
        self.powerup_index = []

        self.ded_index = 0
        self.ded_counter = 0
        self.ded_sequence = False
        self.ded_music = False

        self.num_of_arrows = 12

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
            img_right_latk = pygame.image.load(
                f"img/lightatk/latk{num}.png"
            ).convert_alpha()
            img_right_latk = pygame.transform.scale(img_right_latk, (40, 80))
            img_left_latk = pygame.transform.flip(img_right_latk, True, False)
            self.images_right_latk.append(img_right_latk)
            self.images_left_latk.append(img_left_latk)
        for num in range(1, 13):
            img_left_shoot = pygame.image.load(
                f"img/shoot_list/shoot{num}.png"
            ).convert_alpha()
            img_left_shoot = pygame.transform.scale(img_left_shoot, (40, 80))
            img_right_shoot = pygame.transform.flip(img_left_shoot, True, False)
            self.images_right_shoot.append(img_right_shoot)
            self.images_left_shoot.append(img_left_shoot)
        for num in range(1, 7):
            img_left_ded = pygame.image.load(
                f"img/ded_list/ded{num}.png"
            ).convert_alpha()
            img_left_ded = pygame.transform.scale(img_left_ded, (40, 80))
            img_right_ded = pygame.transform.flip(img_left_ded, True, False)
            self.images_right_ded.append(img_right_ded)
            self.images_left_ded.append(img_left_ded)

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
        self.ground_level = self.rect.bottom

    def update(self, game_over):
        if self.rect.bottom >= screen_height:
            self.health = 0
        screen_scroll = 0
        y_scroll = 0
        dx = 0
        dy = 0
        walk_cooldown = 1
        jump_cooldown = 2
        walk_music_cooldown = 20
        idle_cooldown = 8
        flower_cooldown = 8

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
                dx -= self.speed
                self.counter += 1
                self.walk_music += 1
                self.direction = -1

            if key[pygame.K_RIGHT]:
                if self.run_fx == False:
                    self.run_fx = True
                    walk_fx.play()
                dx += self.speed
                self.counter += 1
                self.walk_music += 1
                self.direction = 1

            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                walk_fx.stop()
                self.run_fx = False
                self.idle_counter += 1
                if self.idle_counter > idle_cooldown:
                    self.idle_counter = 0
                    self.idle_index += 1
                    if self.idle_index >= len(self.images_right_idle):
                        self.idle_index = 0

                    if self.direction == 1:
                        self.image = self.images_right_idle[self.idle_index]
                    if self.direction == -1:
                        self.image = self.images_left_idle[self.idle_index]

            # collect flowers
            if key[pygame.K_e] and pygame.sprite.spritecollide(
                self, flower_group, False
            ):
                flower_fx.play()
                flower_list = pygame.sprite.spritecollide(self, flower_group, False)
                for flower in flower_list:
                    if flower.consumed == False:
                        self.flower_count += 1
                    else:
                        self.health += 5
                    flower_group.remove(flower)

            # plant flowers
            if key[pygame.K_f] and self.flower_cooler <= 0 and self.in_air == False:
                self.flower_counter += 1
                if self.flower_count > 0:
                    if self.flower_counter > flower_cooldown:
                        self.flower_counter = 0
                        self.flower_count -= 1
                        flower = Flower(self.rect.x, self.rect.y + 22)
                        flower.consumed = True
                        flower_group.add(flower)
                        plant_fx.play()
                        self.flower_cooler = 50

            # use light atk
            if key[pygame.K_q]:
                if self.atk_music == False:
                    atk1_fx.play()
                    self.atk_music = True
                self.light_atk_sequence = True

            # shoot arrows
            if key[pygame.K_w] and self.num_of_arrows > 0:
                if self.shoot_music == False:
                    arrow_release_fx.play()
                    self.shoot_music = True
                    self.num_of_arrows -= 1
                self.shoot_sequence = True

                # self.latk_counter += 1

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
                            self.ground_level = self.rect.y

            # check for collision with powerups
            if pygame.sprite.spritecollide(self, powerup_group, False):
                powerup_list = pygame.sprite.spritecollide(self, powerup_group, True)
                for powerup in powerup_list:
                    if powerup.index == 1:
                        powerup_group.remove(powerup)
                        flower_fx.play()
                        self.num_of_arrows += 5
                    elif powerup.index == 2:
                        powerup_group.remove(powerup)
                        flower_fx.play()
                        self.powerup_index.append(list([2, True]))
                    elif powerup.index == 3:
                        powerup_group.remove(powerup)
                        flower_fx.play()
                        self.powerup_index.append(list([3, True]))

            # update player co ordinates
            self.rect.x += dx
            self.rect.y += dy

            # update scroll
            if (
                self.rect.right > (screen_width - scroll_thresh) and self.direction == 1
            ) or (self.rect.left < scroll_thresh and self.direction == -1):

                self.rect.x -= dx
                screen_scroll = -dx

            if (
                (self.rect.top < (200))
                or (
                    (self.rect.bottom > (screen_height - 400))
                    and (self.rect.bottom < (screen_height - 300))
                )
                or (self.rect.bottom < (screen_height - 150))
            ):
                self.rect.y -= dy
                y_scroll = -(dy)

            # draw player onto the screen
            if self.light_atk_sequence == True:
                self.latk()
            elif self.shoot_sequence == True:
                self.shoot_arrow()

            else:
                screen.blit(self.image, self.rect)
            self.flower_cooler -= 1
            if self.flower_cooler < 0:
                self.flower_cooler = 0
        elif game_over == -1:
            if self.ded_sequence == False:
                self.ded()
                if self.ded_music == True:
                    damage_fx.play()
                    self.ded_music = False
            else:
                self.image = self.images_left_ded[5]
                screen.blit(self.image, self.rect)
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

        return screen_scroll, y_scroll
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def latk(self):
        latk_cooldown = 2
        self.latk_counter += 1
        if self.latk_counter > latk_cooldown:
            self.latk_counter = 0

            self.latk_index += 1
            if self.latk_index >= len(self.images_right_latk):
                self.light_atk_sequence = False
                self.latk_index = 0
                if pygame.sprite.spritecollide(self, minotaur_group, False):
                    minotaur_list = pygame.sprite.spritecollide(
                        self, minotaur_group, False
                    )
                    for minotaur in minotaur_list:
                        minotaur.health -= self.latk_dmg
                if pygame.sprite.spritecollide(self, wizard_group, False):
                    wizard_list = pygame.sprite.spritecollide(self, wizard_group, False)
                    for wizard in wizard_list:
                        wizard.health -= self.latk_dmg
                if pygame.sprite.spritecollide(self, eye_group, False):
                    eye_list = pygame.sprite.spritecollide(self, eye_group, False)
                    for eye in eye_list:
                        eye.health -= self.latk_dmg
                self.atk_music = False
            if self.direction == 1:
                self.image = self.images_right_latk[self.latk_index]
            if self.direction == -1:
                self.image = self.images_left_latk[self.latk_index]
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)
            # time.sleep(0.01)

    def shoot_arrow(self):
        shoot_cooldown = 1
        self.shoot_counter += 1
        if self.shoot_counter > shoot_cooldown:
            self.shoot_counter = 0

            self.shoot_index += 1
            if self.shoot_index >= len(self.images_right_shoot):
                self.shoot_sequence = False
                self.shoot_index = 0

            if self.shoot_index == 5:
                i = 1
                j = 1
                cond = 0
                for powerup in self.powerup_index:
                    cond = 1
                    if powerup[0] == 2:
                        arrow = Arrow(
                            self.rect.centerx, self.rect.centery, self.direction
                        )
                        arrow_group.add(arrow)
                        arrow = Arrow(
                            self.rect.centerx,
                            self.rect.centery - (7 * i),
                            self.direction,
                        )
                        arrow_group.add(arrow)
                        arrow = Arrow(
                            self.rect.centerx,
                            self.rect.centery + (7 * i),
                            self.direction,
                        )
                        arrow_group.add(arrow)
                        i += 1
                    elif powerup[0] == 3:
                        arrow = Arrow(
                            self.rect.centerx, self.rect.centery, self.direction
                        )
                        arrow.damage *= 4 * j
                        arrow_group.add(arrow)
                        print(arrow.damage)
                        j += 1
                if cond == 0:
                    arrow = Arrow(self.rect.centerx, self.rect.centery, self.direction)
                    arrow_group.add(arrow)
                self.shoot_music = False

            if self.direction == 1:
                self.image = self.images_right_shoot[self.shoot_index]
            if self.direction == -1:
                self.image = self.images_left_shoot[self.shoot_index]

        screen.blit(self.image, self.rect)
        # time.sleep(0.01)

    def ded(self):
        ded_cooldown = 2
        self.ded_counter += 1
        if self.ded_counter > ded_cooldown:
            self.ded_counter = 0

            self.ded_index += 1
            if self.ded_index >= len(self.images_right_ded):
                self.ded_sequence = True
                self.ded_index = 0

            if self.direction == 1:
                self.image = self.images_right_ded[self.ded_index]
            if self.direction == -1:
                self.image = self.images_left_ded[self.ded_index]
        screen.blit(self.image, self.rect)


class World:
    def __init__(self, data):
        self.tile_list = []
        self.light_list = []

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
        lamp = pygame.image.load("img/lamp.png").convert_alpha()
        pole = pygame.image.load("img/pole.png").convert_alpha()

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 10:
                    img = pygame.transform.scale(bush1, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + 2
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 20:
                    img = pygame.transform.scale(
                        bush2, (int(tile_size * 1.5), int(tile_size * 1.5))
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + 2 - int(tile_size * 0.5)
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 30:
                    img = pygame.transform.scale(
                        bush3, (tile_size * 2, int(tile_size * 1.5))
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + 2 - int(tile_size * 0.5)
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 40:
                    img = pygame.transform.scale(
                        flower_3, (int(tile_size * 1.5), tile_size)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - 60
                    img_rect.y = row_count * tile_size + 2
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 50:
                    flower = Flower(col_count * tile_size, row_count * tile_size + 2)
                    flower_group.add(flower)

                if tile == 60:
                    img = pygame.transform.scale(ground_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)
                if tile == 70:
                    img = pygame.transform.scale(
                        cart_img, (tile_size * 3, int(tile_size * 1.5))
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - int(tile_size * 0.5)
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 80:
                    img = pygame.transform.scale(
                        wheel_img, (int(tile_size // 1.5), int(tile_size // 1.5))
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - 30
                    img_rect.y = row_count * tile_size + 2 + 20
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 90:
                    img = pygame.transform.scale(surface_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)
                if tile == 21:
                    img = pygame.transform.scale(obstacle_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)

                if tile == 12:
                    img = pygame.transform.scale(box_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + 2
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)
                if tile == 13:
                    img = pygame.transform.scale(
                        scarecrow_img, (tile_size, tile_size + 30)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - 30 + 2
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 14:
                    img = pygame.transform.scale(logs_img, (tile_size * 2, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + 2
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)
                if tile == 15:
                    img = pygame.transform.scale(
                        well_img, (tile_size * 2, tile_size * 2)
                    )
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - tile_size * 1 + 2
                    tile = (img, img_rect, True, 0)
                    self.tile_list.append(tile)

                if tile == 16:
                    minotaur = Minotaur(
                        col_count * tile_size, row_count * tile_size - 30
                    )
                    minotaur_group.add(minotaur)

                if tile == 17:
                    powerup = Arrow_powerup1(
                        col_count * tile_size, row_count * tile_size
                    )
                    powerup_group.add(powerup)
                if tile == 18:
                    powerup = Arrow_powerup2(
                        col_count * tile_size, row_count * tile_size
                    )
                    powerup_group.add(powerup)
                if tile == 19:
                    powerup = Arrow_powerup3(
                        col_count * tile_size, row_count * tile_size
                    )
                    powerup_group.add(powerup)
                if tile == 22:
                    img = pygame.transform.scale(pole, (tile_size, tile_size * 2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - tile_size * 1 + 2
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 23:
                    img = pygame.transform.scale(lamp, (tile_size // 2, tile_size // 2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - 30
                    img_rect.y = row_count * tile_size - tile_size * 1 + 35
                    tile = (img, img_rect, False, 1)

                    self.tile_list.append(tile)
                if tile == 11:
                    tree_width = tile_size * 4
                    tree_height = tile_size * 6
                    img = pygame.transform.scale(tree_img, (tree_width, tree_height))
                    img_rect = img.get_rect()
                    img_rect.x = (
                        col_count * tile_size - (tree_width // 2) + (tile_size // 2)
                    )
                    img_rect.y = row_count * tile_size - tile_size * 5 + 2
                    tile = (img, img_rect, False, 0)
                    self.tile_list.append(tile)
                if tile == 24:
                    wizard = Wizard(col_count * tile_size, row_count * tile_size - 30)
                    wizard_group.add(wizard)
                if tile == 25:
                    eye = Eye(col_count * tile_size, row_count * tile_size - 30)
                    eye_group.add(eye)
                col_count += 1
            row_count += 1

    def draw(self, screen_scroll, y_scroll):
        for tile in self.tile_list:
            tile[1][0] += screen_scroll
            tile[1][1] += y_scroll
            if tile[3] == 1:
                circs = [
                    17,
                    17,
                    17,
                    17,
                    17,
                    16,
                    16,
                    16,
                    17,
                    17,
                    17,
                    15,
                    14,
                    13,
                    12,
                    11,
                    11,
                    10,
                    10,
                    9,
                ]
                for i in range(len(circs)):
                    pygame.draw.circle(
                        screen,
                        (circs[i] * 15, circs[i] * 15, 0),
                        (tile[1][0] + 20, tile[1][1] + 17),
                        i + 1,
                        1,
                    )
                screen.blit(tile[0], tile[1])
            else:
                screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


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

    def update(self, screen_scroll, y_scroll):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class Minotaur(pygame.sprite.Sprite):
    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.health = 200
        self.max_health = 200
        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_atk1 = []
        self.images_left_atk1 = []
        self.images_right_ded = []
        self.images_left_ded = []
        self.images_right_taunt = []
        self.images_left_taunt = []
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
        self.taunt_counter = 0
        self.taunt_index = 0
        self.taunt_time = 0
        self.alive = True
        self.ded_music = False
        self.taunt_music = False
        self.taunt_sequence = False
        self.taunt_complete = False
        self.jumped = False
        self.in_air = False
        self.damage = 20
        self.t = 200

        for num in range(1, 6):
            img_right_idle = pygame.image.load(
                f"img/Mino_idle_list/idle{num}.png"
            ).convert_alpha()
            img_right_idle = pygame.transform.scale(
                img_right_idle, (tile_size + 48, 90)
            )
            img_left_idle = pygame.transform.flip(img_right_idle, True, False)
            self.images_right_idle.append(img_right_idle)
            self.images_left_idle.append(img_left_idle)
        for num in range(1, 9):
            img_right_run = pygame.image.load(
                f"img/Mino_run_list/run{num}.png"
            ).convert_alpha()
            img_right_run = pygame.transform.scale(img_right_run, (tile_size + 48, 90))
            img_left_run = pygame.transform.flip(img_right_run, True, False)
            self.images_right_run.append(img_right_run)
            self.images_left_run.append(img_left_run)
        for num in range(1, 10):
            img_right_atk1 = pygame.image.load(
                f"img/Mino_atk_list/atk{num}.png"
            ).convert_alpha()
            img_right_atk1 = pygame.transform.scale(
                img_right_atk1, (tile_size + 48, 90)
            )
            img_left_atk1 = pygame.transform.flip(img_right_atk1, True, False)
            self.images_right_atk1.append(img_right_atk1)
            self.images_left_atk1.append(img_left_atk1)
        for num in range(1, 4):
            img_right_ded = pygame.image.load(
                f"img/Mino_ded_list/ded{num}.png"
            ).convert_alpha()
            img_right_ded = pygame.transform.scale(img_right_ded, (tile_size + 48, 90))
            img_left_ded = pygame.transform.flip(img_right_ded, True, False)
            self.images_right_ded.append(img_right_ded)
            self.images_left_ded.append(img_left_ded)

        for num in range(1, 6):
            img_right_taunt = pygame.image.load(
                f"img/mino_taunt/taunt{num}.png"
            ).convert_alpha()
            img_right_taunt = pygame.transform.scale(
                img_right_taunt, (tile_size + 48, 90)
            )
            img_left_taunt = pygame.transform.flip(img_right_taunt, True, False)
            self.images_right_taunt.append(img_right_taunt)
            self.images_left_taunt.append(img_left_taunt)

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

    def update(self, screen_scroll, y_scroll):

        if self.health <= 0:
            if self.ded_music == False:
                damage_fx.play()
                self.ded_music = True
            if self.alive == True:
                self.dead_counter += 1
                if self.dead_counter > 10:
                    self.ded(screen_scroll)
            else:
                if self.t != 0:
                    self.t -= 1
                    if self.direction == 1:
                        self.image = self.images_right_ded[
                            len(self.images_right_ded) - 1
                        ]
                    if self.direction == -1:
                        self.image = self.images_left_ded[len(self.images_left_ded) - 1]
                else:
                    minotaur_group.remove(self)
        else:
            detect_thresh = 400
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
                    if self.atk1_index >= (
                        (int(len(self.images_right_atk1)) // 2)
                    ) and self.atk1_index <= (len(self.images_right_atk1) // 2):
                        if self.rect.colliderect(player.rect):
                            player.health -= self.damage
                            if player.health <= 0:
                                damage_fx.play()

                    if self.direction == 1:
                        self.image = self.images_right_atk1[self.atk1_index]
                    if self.direction == -1:
                        self.image = self.images_left_atk1[self.atk1_index]
                    self.rect.x += screen_scroll
                    screen.blit(self.image, self.rect)

            else:
                if abs(player.rect.x - self.rect.x) <= detect_thresh:
                    self.detect_player = True
                    self.taunt_sequence = True
                if self.taunt_sequence == True and self.taunt_complete == False:
                    if self.taunt_music == False:
                        growl_fx.play()
                        self.taunt_music = True
                    self.taunt(screen_scroll)
                else:
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
        # check for collision
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
        self.rect.y += y_scroll
        self.mino_healthbar(self.rect.x, self.rect.y)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def mino_healthbar(self, x, y):
        if self.direction == 1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 15, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 15, y - 7, int(self.health // 4), 10)
            )
        elif self.direction == -1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 40, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 40, y - 7, int(self.health // 4), 10)
            )

    def idle(self, screen_scroll):
        idle_cooldown = 5

        self.idle_counter += 1
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

        screen.blit(self.image, self.rect)

    def taunt(self, screen_scroll):
        taunt_cooldown = 8
        self.taunt_counter += 1
        self.taunt_time += 1
        if self.taunt_counter > taunt_cooldown:
            self.taunt_counter = 0
            self.taunt_index += 1
            if self.taunt_index >= len(self.images_right_taunt):
                self.taunt_index = 0

            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
            else:
                self.direction = 1

            if self.direction == 1:
                self.image = self.images_right_taunt[self.taunt_index]
            if self.direction == -1:
                self.image = self.images_left_taunt[self.taunt_index]
        if abs(self.taunt_time) > 120:
            self.taunt_time = 0
            self.taunt_sequence = False
            self.taunt_music = False
            self.taunt_complete = True
        screen.blit(self.image, self.rect)

    def ded(self, screen_scroll):
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

        screen.blit(self.image, self.rect)

    def move(self, screen_scroll):
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

        screen.blit(self.image, self.rect)

        if abs(self.move_counter) > 120:
            self.is_moving = False
            self.move_direction *= -1
            self.move_counter *= -1

            return

    def ai(self, screen_scroll):

        # collision with player
        if self.rect.colliderect(player.rect):
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
        # make minotaur jump
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if (
                    tile[2] == True
                    and tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y, self.width, self.height
                    )
                    and self.jumped == False
                ):
                    self.vel_y -= 15
                    self.jumped = True

        screen.blit(self.image, self.rect)

        if self.detect_player == True and abs(player.rect.x - self.rect.x) > 300:
            self.detect_player = False


class Wizard(pygame.sprite.Sprite):
    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.health = 300
        self.max_health = 300
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
        self.damage = 50
        self.t = 200

        for num in range(1, 9):
            img_right_idle = pygame.image.load(
                f"img/wizard_idle/Idle{num}.png"
            ).convert_alpha()
            img_right_idle = pygame.transform.scale(
                img_right_idle, (int(tile_size * 2.5), tile_size * 4)
            )
            img_left_idle = pygame.transform.flip(img_right_idle, True, False)
            self.images_right_idle.append(img_right_idle)
            self.images_left_idle.append(img_left_idle)

        for num in range(1, 9):
            img_right_run = pygame.image.load(
                f"img/Run_idle/Run{num}.png"
            ).convert_alpha()
            img_right_run = pygame.transform.scale(
                img_right_run, (int(tile_size * 2.5), tile_size * 4)
            )
            img_left_run = pygame.transform.flip(img_right_run, True, False)
            self.images_right_run.append(img_right_run)
            self.images_left_run.append(img_left_run)

        for num in range(1, 9):
            img_right_atk1 = pygame.image.load(
                f"img/wiz_atk/Attack{num}.png"
            ).convert_alpha()
            img_right_atk1 = pygame.transform.scale(
                img_right_atk1, (int(tile_size * 2.5), tile_size * 4)
            )
            img_left_atk1 = pygame.transform.flip(img_right_atk1, True, False)
            self.images_right_atk1.append(img_right_atk1)
            self.images_left_atk1.append(img_left_atk1)

        for num in range(1, 8):
            img_right_ded = pygame.image.load(
                f"img/wiz_ded/Death{num}.png"
            ).convert_alpha()
            img_right_ded = pygame.transform.scale(
                img_right_ded, (int(tile_size * 2.5), tile_size * 4)
            )
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

    def update(self, screen_scroll, y_scroll):
        if self.health <= 0:
            if self.ded_music == False:
                damage_fx.play()
                self.ded_music = True
            if self.alive == True:
                self.dead_counter += 1
                if self.dead_counter > 10:
                    self.ded(screen_scroll)
            else:
                if self.t != 0:
                    self.t -= 1
                    if self.direction == 1:
                        self.image = self.images_right_ded[
                            len(self.images_right_ded) - 1
                        ]
                    if self.direction == -1:
                        self.image = self.images_left_ded[len(self.images_left_ded) - 1]
                else:
                    wizard_group.remove(self)
        else:
            detect_thresh = 300
            atk_cooldown = 5
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
                    if self.atk1_index >= (
                        (int(len(self.images_right_atk1)) // 2)
                    ) and self.atk1_index <= (len(self.images_right_atk1) // 2):
                        if self.rect.colliderect(player.rect):
                            player.health -= self.damage
                            if player.health <= 0:
                                damage_fx.play()

                    if self.direction == 1:
                        self.image = self.images_right_atk1[self.atk1_index]
                    if self.direction == -1:
                        self.image = self.images_left_atk1[self.atk1_index]
                    self.rect.x += screen_scroll
                    screen.blit(self.image, self.rect)

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
        # check for collision
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
        self.rect.y += y_scroll
        self.wiz_healthbar(self.rect.x, self.rect.y)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def wiz_healthbar(self, x, y):
        if self.direction == 1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 15, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 15, y - 7, int(self.health // 4), 10)
            )
        elif self.direction == -1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 40, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 40, y - 7, int(self.health // 4), 10)
            )

    def idle(self, screen_scroll):
        idle_cooldown = 8
        self.idle_counter += 1
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
        screen.blit(self.image, self.rect)

    def move(self, screen_scroll):
        self.dx += 7 * self.move_direction
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
        # make wizard jump
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if (
                    tile[2] == True
                    and tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y, self.width, self.height
                    )
                    and self.jumped == False
                ):
                    self.vel_y -= 15
                    self.jumped = True

        screen.blit(self.image, self.rect)

        if abs(self.move_counter) > 120:
            self.is_moving = False
            self.move_direction *= -1
            self.move_counter *= -1

            return

    def ded(self, screen_scroll):
        dead_cooldown = 7
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

        screen.blit(self.image, self.rect)

    def ai(self, screen_scroll):

        # collision with player
        if self.rect.colliderect(player.rect):
            self.atk1_sequence = True

            if self.atk1_music == False:
                self.iterations = 0
                wiz_atk_fx.play()
                self.atk1_music = True

        if self.detect_player == True and self.atk1_sequence == False:
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
                self.dx -= 6
            else:
                self.direction = 1
                self.dx += 6
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
        # make wizard jump
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if (
                    tile[2] == True
                    and tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y, self.width, self.height
                    )
                    and self.jumped == False
                ):
                    self.vel_y -= 20
                    self.jumped = True

        screen.blit(self.image, self.rect)

        if self.detect_player == True and abs(player.rect.x - self.rect.x) > 300:
            self.detect_player = False


class Eye(pygame.sprite.Sprite):
    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.health = 60
        self.max_health = 60
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
        self.damage = 10
        self.t = 200
        self.fly_counter = 0
        self.updown = random.choice([1, -1])
        self.flying = False

        for num in range(1, 9):
            img_right_idle = pygame.image.load(
                f"img/eye/Flight{num}.png"
            ).convert_alpha()
            img_right_idle = pygame.transform.scale(
                img_right_idle, (tile_size + 48, 90)
            )
            img_left_idle = pygame.transform.flip(img_right_idle, True, False)
            self.images_right_idle.append(img_right_idle)
            self.images_left_idle.append(img_left_idle)

        for num in range(1, 5):
            img_right_ded = pygame.image.load(
                f"img/eye_ded/Death{num}.png"
            ).convert_alpha()
            img_right_ded = pygame.transform.scale(img_right_ded, (tile_size + 48, 90))
            img_left_ded = pygame.transform.flip(img_right_ded, True, False)
            self.images_right_ded.append(img_right_ded)
            self.images_left_ded.append(img_left_ded)
        for num in range(1, 9):
            img_right_atk1 = pygame.image.load(
                f"img/eye_attack/Attack{num}.png"
            ).convert_alpha()
            img_right_atk1 = pygame.transform.scale(
                img_right_atk1, ((tile_size + 48, 90))
            )
            img_left_atk1 = pygame.transform.flip(img_right_atk1, True, False)
            self.images_right_atk1.append(img_right_atk1)
            self.images_left_atk1.append(img_left_atk1)

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

    def update(self, screen_scroll, y_scroll):
        if self.health <= 0:
            self.dx = 0
            self.dy = 2
            if self.ded_music == False:
                damage_fx.play()
                self.ded_music = True
            if self.alive == True:
                self.dead_counter += 1
                if self.dead_counter > 10:
                    self.ded(screen_scroll)
            else:
                if self.t != 0:
                    self.t -= 1
                    if self.direction == 1:
                        self.image = self.images_right_ded[
                            len(self.images_right_ded) - 1
                        ]
                    if self.direction == -1:
                        self.image = self.images_left_ded[len(self.images_left_ded) - 1]
                else:
                    eye_group.remove(self)
        else:
            detect_thresh = 300
            atk_cooldown = 6
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
                    if self.atk1_index >= (
                        (int(len(self.images_right_atk1)) - 1)
                    ) and self.atk1_index <= (len(self.images_right_atk1)):
                        if self.rect.colliderect(player.rect):
                            player.health -= self.damage
                            if player.health <= 0:
                                damage_fx.play()

                    if self.direction == 1:
                        self.image = self.images_right_atk1[self.atk1_index]
                    if self.direction == -1:
                        self.image = self.images_left_atk1[self.atk1_index]
                    self.rect.x += screen_scroll
                    screen.blit(self.image, self.rect)

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

        # make eye fall down when dead
        if self.alive == False:
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            self.dy += self.vel_y
        else:
            # make eye fly
            if self.fly_counter == 0:
                self.fly_counter = 100
                self.dy = self.updown
                self.updown *= -1
        self.fly_counter -= 1

        # check for collision
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
        self.rect.y += y_scroll
        self.eye_healthbar(self.rect.x, self.rect.y)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    def eye_healthbar(self, x, y):
        if self.direction == 1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 57, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 57, y - 7, int(self.health // 4), 10)
            )
        elif self.direction == -1:
            pygame.draw.rect(
                screen, (255, 0, 0), (x + 40, y - 7, int(self.max_health // 4), 10)
            )
            pygame.draw.rect(
                screen, (0, 255, 0), (x + 40, y - 7, int(self.health // 4), 10)
            )

    def idle(self, screen_scroll):
        idle_cooldown = 5
        self.idle_counter += 1
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

        screen.blit(self.image, self.rect)

    def ded(self, screen_scroll):
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

        screen.blit(self.image, self.rect)

    def move(self, screen_scroll):
        self.dx = self.move_direction * 6
        self.direction = self.move_direction

        self.move_counter += 1
        self.run_counter += 1
        move_cooldown = 5

        if self.run_counter > move_cooldown:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(self.images_right_idle):
                self.index = 0

            if self.direction == 1:
                self.image = self.images_right_idle[self.index]

            if self.direction == -1:
                self.image = self.images_left_idle[self.index]

        # make eye fly
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if (
                    tile[2] == True
                    and tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y, self.width, self.height
                    )
                    and self.jumped == False
                ):
                    self.dy = -3
                    self.jumped = True
        screen.blit(self.image, self.rect)

        if abs(self.move_counter) > 120:
            self.is_moving = False
            self.move_direction *= -1
            self.move_counter *= -1

            return

    def ai(self, screen_scroll):

        # collision with player
        if self.rect.colliderect(player.rect):
            self.atk1_sequence = True

            if self.atk1_music == False:
                self.iterations = 0
                screech_fx.play(0, 850)
                self.atk1_music = True

        if self.detect_player == True and self.atk1_sequence == False:
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
                self.dx = -4
            else:
                self.direction = 1
                self.dx = 4
            if (player.rect.y - self.rect.y) <= 0:
                self.dy = -2
            else:
                self.dy = 2
        self.run_counter += 1
        move_cooldown = 5

        if self.run_counter > move_cooldown:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(self.images_right_idle):
                self.index = 0

            if self.direction == 1:
                self.image = self.images_right_idle[self.index]
            if self.direction == -1:
                self.image = self.images_left_idle[self.index]
        # make eye fly
        if self.atk1_sequence == False:
            for tile in world.tile_list:
                if (
                    tile[2] == True
                    and tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y, self.width, self.height
                    )
                    and self.jumped == False
                ):
                    self.dy = -3
                    self.jumped = True

        screen.blit(self.image, self.rect)

        if self.detect_player == True and abs(player.rect.x - self.rect.x) > 1000:
            self.detect_player = False


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/arrow.png").convert_alpha()
        self.image_right = pygame.transform.scale(
            img, (tile_size // 2, int(tile_size // 5))
        )
        self.image_left = pygame.transform.flip(self.image_right, True, False)

        self.direction = direction
        self.speed = 12
        self.dx = 0
        self.dy = 0
        self.stopped = False
        self.damage = 30
        if self.direction == 1:
            self.image = self.image_right
        if self.direction == -1:
            self.image = self.image_left

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, screen_scroll, y_scroll):
        screen.blit(self.image, self.rect)
        self.dx = self.speed * self.direction
        # check for collision
        self.in_air = True
        for tile in world.tile_list:
            # check for collision in x direction
            if tile[2] == True and tile[1].colliderect(
                self.rect.x + self.dx, self.rect.y, self.width, self.height
            ):
                self.dx = 0
                arrow_hit_fx.play()
                arrow_group.remove(self)

        # check for collision with minotaur
        if pygame.sprite.spritecollide(self, minotaur_group, False):
            minotaur_list = pygame.sprite.spritecollide(self, minotaur_group, False)
            for minotaur in minotaur_list:
                minotaur.health -= self.damage
                arrow_hit_fx.play()
            arrow_group.remove(self)
        # check for collision with wizard
        if pygame.sprite.spritecollide(self, wizard_group, False):
            wizard_list = pygame.sprite.spritecollide(self, wizard_group, False)
            for wizard in wizard_list:
                wizard.health -= self.damage
                arrow_hit_fx.play()
            arrow_group.remove(self)
        # check for collision with eye
        if pygame.sprite.spritecollide(self, eye_group, False):
            eye_list = pygame.sprite.spritecollide(self, eye_group, False)
            for eye in eye_list:
                eye.health -= self.damage
                arrow_hit_fx.play()
            arrow_group.remove(self)
        self.rect.x += self.dx
        self.rect.x += screen_scroll
        self.rect.y += y_scroll


class Score_Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/1flower.png").convert_alpha()
        self.image = pygame.transform.scale(
            img, (tile_size // 3, int(tile_size // 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False

    def update(self, screen_scroll, y_scroll):
        screen.blit(self.image, self.rect)


class Arrow_count(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/arrow.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size // 2, int(tile_size // 5)))
        self.image = pygame.transform.rotozoom(self.image, 45, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, screen_scroll, y_scroll):
        screen.blit(self.image, self.rect)


class Arrow_powerup1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/arrow_powerup.png").convert_alpha()
        self.image = pygame.transform.scale(
            img, (int(tile_size // 1.5), int(tile_size // 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = 1

    def update(self, screen_scroll, y_scroll):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class Arrow_powerup2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/arrow_powerup2.png").convert_alpha()
        self.image = pygame.transform.scale(
            img, (int(tile_size // 1.5), int(tile_size // 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = 2

    def update(self, screen_scroll, y_scroll):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class Arrow_powerup3(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # load image
        img = pygame.image.load("img/arrow_powerup3.png").convert_alpha()
        self.image = pygame.transform.scale(
            img, (int(tile_size // 1.5), int(tile_size // 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = 3

    def update(self, screen_scroll, y_scroll):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class Arrow_powerup1_1(pygame.sprite.Sprite):
    def __init__(self, x, y, index):
        pygame.sprite.Sprite.__init__(self)
        # load image
        if index == 1:
            img = pygame.image.load("img/arrow_powerup.png").convert_alpha()
        if index == 2:
            img = pygame.image.load("img/arrow_powerup2.png").convert_alpha()
        if index == 3:
            img = pygame.image.load("img/arrow_powerup3.png").convert_alpha()

        self.image = pygame.transform.scale(
            img, (int(tile_size // 1.5), int(tile_size // 1.5))
        )
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = 1

    def update(self, screen_scroll, y_scroll):
        pygame.draw.circle(
            screen, (0, 0, 0), (self.rect.centerx, self.rect.centery), 25
        )
        screen.blit(self.image, self.rect)


# world_data = [
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,13,50,16,30,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,12,60,60,60,60,60,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,90,90,90,90,90,90,90,90,90,90,90,90,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [00,00,00,19,00,00,00,00,00,00,00,00,00,00,12,60,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,90,90,00,00,00,00,00,00,00,00,00,00,00,00,60,90,90,00,00,00,00,00,00,12,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [10,11,00,00,70,80,00,40,00,11,00,30,00,21,12,60,00,15,00,10,00,40,14,11,00,30,17,10,10,00,50,10,13,00,20,13,00,10,50,11,16,00,00,10,00,00,00,00,30,12,15,00,17,00,11,00,10,00,00,10,00,13,00,00,00,16,00,14,00,20,00,11,00,50,00,18,50,00,10,10,16,00,30,00,00,16,00,50,50,00,11,10,00,16,00,10,00,00,00,00,11,00,00,00,00,10,00,00,00,00,00,16,00,00,00,00,00,00,00,00,90,90,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,60,60,90,90,00,16,00,21,60,00,11,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,90,00,00,90,90,00,00,90,90,90,90,90,90,00,00,90,90,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,60,60,90,90,90,90,90,90,90,90,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
#    [60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,00,00,60,60,00,00,60,60,60,60,60,60,00,00,60,60,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,60,60,60,60,60,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00],
# ]
import worldgen

world_data = worldgen.gen_new_world()
# world_data = worldgen.new_meth()
world_data = worldgen.base_connect(world_data)

world_data = worldgen.place_items(world_data)

flower_group = pygame.sprite.Group()
player = Player(tile_size + 10, screen_height - 260 + 2)

minotaur_group = pygame.sprite.Group()
wizard_group = pygame.sprite.Group()
eye_group = pygame.sprite.Group()

arrow_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
health = health_bar()

dummy_flower = Score_Flower(20, tile_size)
dummy_arrow = Arrow_count(20, tile_size + 40)
arrow_group.add(dummy_arrow)

flower_group.add(dummy_flower)
world = World(world_data)

text_x = 0
text_x = tile_size
text_y = 180

powerup_iterations = []
set_iterations = []

screen_scroll = 0
y_scroll = 0
dummy_arrow3 = Arrow_powerup1_1(3, 175, 1)
dummy_arrow2 = []
c_list = []
active_p = 0
thunder = False
thunder2 = False

co = 0
while 1:

    clock.tick(fps)
    screen.blit(background, (0, 0))

    # draw_grid()

    world.draw(screen_scroll, y_scroll)

    draw_text("HEALTH", font_health, (255, 255, 255), 0, 10)
    draw_text(
        "X" + str(player.flower_count), font_health, (255, 255, 255), 40, tile_size - 10
    )
    draw_text(
        "X" + str(player.num_of_arrows),
        font_health,
        (255, 255, 255),
        50,
        tile_size + 40 - 10,
    )

    health.draw(player.health)
    flower_group.draw(screen)
    flower_group.update(screen_scroll, y_scroll)
    (screen_scroll, y_scroll) = player.update(game_over)

    text_x += screen_scroll
    text_y += y_scroll
    draw_text("Collect flowers for granny", font, (255, 255, 255), text_x, text_y)
    draw_text("Collect flowers using E", font, (255, 255, 255), text_x, text_y + 40)
    draw_text(
        "Plant flowers using F and consume them again to heal",
        font,
        (255, 255, 255),
        text_x,
        text_y + 80,
    )

    minotaur_group.draw(screen)
    minotaur_group.update(screen_scroll, y_scroll)
    wizard_group.draw(screen)
    wizard_group.update(screen_scroll, y_scroll)
    eye_group.draw(screen)
    eye_group.update(screen_scroll, y_scroll)
    arrow_group.draw(screen)
    arrow_group.update(screen_scroll, y_scroll)
    powerup_group.draw(screen)
    powerup_group.update(screen_scroll, y_scroll)

    if player.health <= 0:
        game_over = -1
        pass

    for p in range(len(player.powerup_index)):
        if player.powerup_index[p][1] == True:
            powerup_iterations.append(1000)
            set_iterations.append(True)
            if player.powerup_index[p][0] == 2:
                x = Arrow_powerup1_1(25, 150 + (60 * active_p), 2)
                dummy_arrow2.append(x)
                c_list.append((150 + (60 * active_p)))
                powerup_group.add(dummy_arrow2[active_p])
                player.powerup_index[p][1] = False
                active_p += 1

            if player.powerup_index[p][0] == 3:
                x = Arrow_powerup1_1(25, 150 + (60 * active_p), 3)
                dummy_arrow2.append(x)
                c_list.append((150 + (60 * active_p)))
                powerup_group.add(dummy_arrow2[active_p])
                player.powerup_index[p][1] = False
                active_p += 1

    for inte in range(len(powerup_iterations)):
        if inte >= len(powerup_iterations):
            break
        if set_iterations[inte] == True:
            pygame.draw.rect(
                screen,
                (0, 255, 255),
                (55, c_list[inte], (powerup_iterations[inte] / 10), 15),
            )
        if powerup_iterations[inte] > 0:
            powerup_iterations[inte] -= 1
        if powerup_iterations[inte] == 0:
            if set_iterations[inte] == True:
                plant_fx.play()
            powerup_group.remove(dummy_arrow2[inte])
            dummy_arrow2.remove(dummy_arrow2[inte])
            set_iterations.remove(set_iterations[inte])
            player.powerup_index.remove(player.powerup_index[inte])
            c_list.remove(c_list[inte])
            powerup_iterations.remove(powerup_iterations[inte])
            active_p -= 1

    # Create rain generator
    rain = Rain(screen)

    # Draw rain
    dirtyrects = rain.Timer(time.time())

    # Update the screen for the dirty rectangles only
    pygame.display.update(dirtyrects)

    # Fill the background with the dirty rectangles only
    for r in dirtyrects:
        screen.fill((0, 0, 0), r)

    # print(player.health)
    if random.randint(0, 200) == 7 and thunder == False and thunder2 == False:
        thunder = True
    if thunder == True and co < 25:
        co += 1
    if co == 20:
        screen.fill((255, 255, 255))
        thunder2 = True
    if co == 25 and thunder2 == True:
        screen.fill((255, 255, 255))
        co = 0
        thunder = False
        thunder2 = False
        thunder_fx.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    pygame.display.update()
pygame.quit()
