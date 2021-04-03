import pygame
import sql_wrapper
import math
import threading
import Music
from time import sleep
from random import choice, randint

# Initialize the game
pygame.init()
sceneNumber = 0
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (180, 34, 22)
LIGHT_GREY = (213, 213, 213)
SIENNA = (160, 82, 45)
BURLYWOOD = (222, 184, 135)
# Define powerup images
POWERUP_IMGS = [
    pygame.image.load('art/vert.png'),
    pygame.image.load('art/x2.png'),
    pygame.image.load('art/slowdown.png')
]
# Define blocks
red = pygame.image.load('art/Red_basic.png')
green = pygame.image.load('art/Red_basic.png')
yellow = pygame.image.load('art/Red_basic.png')
# Set the window properties
size = (400, 500)
screen = pygame.display.set_mode(size)

next_figure_window = (100, 100)

pygame.display.set_caption("Ages and Resources")
clock = pygame.time.Clock()

# List of colors for the tetris shapes
RGB_COLORS = [0, 96, 192, 255]
RGB = []
for r in RGB_COLORS:
    for g in RGB_COLORS:
        for b in RGB_COLORS:
            RGB.append((r, g, b))
COLORS = [
    # Purple
    (120, 37, 179),
    # Teal
    # (100, 179, 179),
    # white ---Aleks--- changed teal to white as teal was hard to spot
    (255, 255, 255),
    # Brown
    (80, 34, 22),
    # Green
    (155, 230, 76),
    # Red
    (180, 34, 22),
    # Pink
    (217, 35, 144),
    # Yellow
    (240, 234, 74),
    # ADD ALL OTHER COLORS BEFORE POWERUPS!!!
    # Three of the same color makes them share
    (0, 210, 0),
    (0, 210, 0),
    (0, 210, 0),
    # Colors for resources
    (122, 70, 1),
    (255, 170, 0),
    (145, 144, 142)
]

SCOREBOARD_LEN = 5


# Figure class
class Figure:
    x = 0
    y = 0

    # List of each shape
    figures = [
        # Line
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        # Z
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        # Backwards Z
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        # L
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        # Backwards L
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        # T
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        # Square
        [[1, 2, 5, 6]],
    ]

    # Function to initialize each block
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        if shape == -1:
            self.type = randint(0, len(self.figures) - 1)
        else:
            self.type = shape
        self.color = self.type
        self.rotation = 0

    # Function to get the current physical properties of the shape(type, and rotation)
    def image(self):
        return self.figures[self.type][self.rotation]

    # Function to rotate the shape
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

    def Crotate(self):
        self.rotation = (self.rotation - 1) % len(self.figures[self.type])


# Tetris class
class Tetris:
    level = 2
    state = "start"
    field = []  # Field checks where there is an empty space on the board
    height = 0
    width = 0
    x = 100
    y = 60
    zoom = 20
    score = 0
    figure = None
    next_figure = None  # Variable to hold the next figure
    held_figure = None  # Variable to hold the figure
    can_swap = False
    game_loop_effect = 0
    resc_gain = 10

    # Function to initialize the tetris game
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.state = "start"
        self.score = 0
        self.age = "None"  # kara added --this should be updated as progressing through ages to be added to the highscores
        self.resc = [0, 0, 0]
        self.sceneNumber = 0
        self.can_swap = True
        self.field = [[-1 for x in range(width)] for x in range(height)]

    # Powerup Functions
    def VERTICAL_CLEAR(self, block):
        for i in range(self.height):
            self.field[i][block] = -1
        for i in range(self.height):
            if self.field[i][block] != -1:
                print("CRIT ERROR @ FIELD ({},{}) - VERT CLEAR FAILED".format(i, block))
        return

    def SLOWER_DROP(self):
        self.game_loop_effect = 1
        return

    def DOUBLE_RESOURCES(self):
        self.resc_gain *= 2
        thread = threading.Thread(target=self.HALF_RESOURCES)
        thread.start()
        print("RES UP - {}".format(self.resc_gain))
        return

    def HALF_RESOURCES(self):
        sleep(20)
        self.resc_gain //= 2
        print("RES DOWN - {}".format(self.resc_gain))
        return

    # Function to add a figure
    def new_figure(self):
        # ---Andy---Check if it is the first time figures are created, if not set the figure equal to next figure
        if self.figure is None:
            self.figure = Figure(3, 0, -1)
        else:
            self.figure = self.next_figure
        # ---Andy---Create a new figure
        self.next_figure = Figure(3, 0, -1)
        # Spawn powerup
        if (not self.has_powerup()) and (randint(0, 100) < 15):
            self.spawn_powerup()
        for x in range(10, 13):
            if (not self.has_rec(x)) and (randint(0, 100) < 25):
                self.spawn_rec(x)

    # Function to check if its a valid move
    def valid_move(self):
        valid = False
        # Loop through each block
        for i in range(4):
            # Check each side of the block
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > -1:
                        valid = True
        return valid

    # Function to break the lines if there is a complete line
    def break_lines(self):
        full_line = 0
        # Loop to check the entire board
        for i in range(1, self.height):
            open_line = 0
            # Loop to check if there are any open blocks
            for j in range(self.width):
                if self.field[i][j] == -1:
                    open_line += 1

            # If there is a completed line, remove it and drop the above blocks down
            if open_line == 0:
                full_line += 1
                self.check_broken(i)
                for k in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[k][j] = self.field[k - 1][j]

        self.score += full_line * 10
        scores = [self.score, self.resc[0], self.resc[1], self.resc[2]]
        print(scores)
        self.check_age()

    # Function to check the age
    def check_age(self):
        rec1 = math.floor(self.resc[0] / 100)
        rec2 = math.floor(self.resc[1] / 100)
        rec3 = math.floor(self.resc[2] / 100)
        if rec1 >= 1 and rec2 >= 1 and rec3 >= 1 and self.age == "Stone":
            self.age = "Iron Age"
            self.sceneNumber += 1
            scene(self.sceneNumber)
        if rec1 >= 2 and rec2 >= 2 and rec3 >= 2 and self.age == "Iron Age":
            self.age = "Middle Age"
            self.sceneNumber += 1
            scene(self.sceneNumber)
        if rec1 >= 3 and rec2 >= 3 and rec3 >= 3 and self.age == "Middle Age":
            self.age = "Early Modern Age"
            self.sceneNumber += 1
            scene(self.sceneNumber)
        if rec1 >= 4 and rec2 >= 4 and rec3 >= 4 and self.age == "Early Modern Age":
            self.age = "Modern Age"
            self.sceneNumber += 1
            scene(self.sceneNumber)

    def check_broken(self, line):
        # Check each cleared block from the broken line
        resc = []  # Resources popped
        for ind in range(self.width):
            block = self.field[line][ind]
            # Update resources/Check Powerups
            if block == 7:
                self.VERTICAL_CLEAR(ind)
            if block == 8:
                self.SLOWER_DROP()
            if block == 9:
                self.DOUBLE_RESOURCES()
            if block in [10, 11, 12]:
                self.resc[block - 10] += self.resc_gain
                resc.append(block)
        for val in resc:
            self.spawn_rec(val)

        for y in range(10, 13):
            if y not in resc:
                if randint(0, 100) < 20:
                    self.spawn_rec(y)

    # Function drop the object
    def drop(self):
        # Decrement the figure down the y-axis
        while not self.valid_move():
            self.figure.y += 1
        # Checks for a valid move
        self.figure.y -= 1
        self.hold()

    # Function to bring down the block
    def go_down(self):
        # Decrement the figure down the y-axis
        self.figure.y += 1
        # Checks for a valid move
        if self.valid_move():
            self.figure.y -= 1
            self.hold()

    # Function to check after each block has been placed
    def hold(self):
        # Set the field of the tetris game to match the figure positions
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        # Check for any completed lines
        self.break_lines()
        # Create a new figure
        self.new_figure()
        self.can_swap = True
        # Check if the current move was valixd
        if self.valid_move():
            self.state = "game_over"

    # Function to move the block side to side
    def go_side(self, dx):
        # Hold the old x-axis value in case the move is invalid
        old_x = self.figure.x
        # Increment the x-axis accordingly and check if valid
        self.figure.x += dx
        # Check if it is valid, if not then keep the old x position
        if self.valid_move():
            self.figure.x = old_x

    # Function to rotate the figure
    def rotate(self):
        # Hold the current rotation of the figure
        old_rotation = self.figure.rotation
        # Rotate the figure
        self.figure.rotate()
        # Check if it is valid, if not the keep then old rotation
        if self.valid_move():
            self.figure.rotation = old_rotation

    def Crotate(self):  # COUNTERROTATE
        old_rotation = self.figure.rotation
        self.figure.Crotate()
        if self.valid_move():
            self.figure.rotation = old_rotation

    # ---Andy--- Function to swap the figures
    def swap(self):
        # Temporary figure to hold a figure when swapping
        self.temp_figure = None
        # Check if we can swap
        if self.can_swap:
            # Check if it is the first swap and swap the figures
            if self.held_figure is None:
                self.held_figure = self.figure
                self.held_figure.x = 3
                self.held_figure.y = 0
                self.new_figure()
            else:
                temp_figure = self.figure
                self.figure = self.held_figure
                self.figure.x = 3
                self.figure.y = 0
                self.held_figure = temp_figure
            self.can_swap = False

    def has_powerup(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] in range(7, 10):
                    return True
        return False

    def spawn_powerup(self):
        if self.has_powerup():
            return
        positions = []
        # Find all open blocks
        for i in range(self.height):
            for j in range(self.width):
                if -1 < self.field[i][j] < 7:
                    positions.append((i, j))
        # Return if empty
        if len(positions) == 0:
            return
        # Add the power up
        pos = choice(positions)
        self.field[pos[0]][pos[1]] = randint(7, 10)

    def has_rec(self, rec):
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i][j] == rec:
                    return True
        return False

    def spawn_rec(self, rec):
        if self.has_rec(rec):
            return

        positions = []
        # Find all open blocks
        for i in range(self.height):
            for j in range(self.width):
                if -1 < self.field[i][j] < 7:
                    positions.append((i, j))
        # Return if empty
        if len(positions) == 0:
            return
        # Add the resource
        pos = choice(positions)
        self.field[pos[0]][pos[1]] = rec


# Function to get the start the game menu
def game_intro():
    Music.play(-1)
    pygame.display.set_caption("Ages and Resources")
    # Bool to run until told otherwise
    intro = True
    menu = pygame.image.load('art/menu.png')  # load menu
    cred = pygame.image.load('art/credits.png')  # load credits

    # buttons
    score = pygame.Rect(136, 377, 132, 42)  # --kara scoreboard button
    start_game = pygame.Rect(144, 184, 119, 41)
    controls = pygame.Rect(137, 264, 138, 40)
    credits = pygame.Rect(135, 334, 133, 34)
    exit = pygame.Rect(128, 427, 149, 42)

    # Loop
    while intro:
        # Get the event type

        for event in pygame.event.get():
            # Quit
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Click start or escape to start the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # checks if the mouse click was on the button
                if start_game.collidepoint(mouse_pos):
                    scene(sceneNumber)
                    game_loop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    intro = False
            # if Exit is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if exit.collidepoint(mouse_pos):
                    quit()

            # if user clicks button, go to corresponding page
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # if they clicked play

                # if they clicked scoreboard
                if score.collidepoint(mouse_pos):
                    scoreboard()
                    pygame.display.set_caption("Ages and Resources")

                # if they clicked controls
                if controls.collidepoint(mouse_pos):
                    control()
                    pygame.display.set_caption("Ages and Resources")

                # if they clicked credits
                if credits.collidepoint(mouse_pos):
                    credit()
                    pygame.display.set_caption("Ages and Resources")

        # Set the location of each rectangle for the selections
        screen.blit(menu, (0, 0))  # ---kara moved this here so changing pages works
        pygame.draw.rect(screen, (255, 0, 0), start_game, 2)  # start
        pygame.draw.rect(screen, (255, 0, 0), controls, 2)  # controls
        pygame.draw.rect(screen, (255, 0, 0), credits, 2)  # credits
        pygame.draw.rect(screen, (255, 0, 0), score, 2)  # scoreboard
        pygame.draw.rect(screen, (255, 0, 0), exit, 2)
        # Update the window
        pygame.display.update()
        clock.tick(15)


def game_loop():
    # Loop until the user clicks the close button.
    pygame.display.set_caption("Ages and Resources")
    end = pygame.image.load('art/end-screen.png')  # Have end-screen ready
    sceneArray = [
        pygame.image.load('art/background.png'), pygame.image.load('art/background2.png'),
        pygame.image.load('art/b3.png'), pygame.image.load('art/b4.png'),
        pygame.image.load('art/b5.png'), pygame.image.load('art/pixil-frame-0.png')
    ]
    # have background ready
    a = 0  # controls which background it is on
    r1_img = [pygame.image.load('art/wood.png'), pygame.image.load('art/wheat.png'),
              pygame.image.load('art/weapon-mold.png'), pygame.image.load('art/ship-wheel.png'),
              pygame.image.load('art/oil.png'), pygame.image.load('art/nuke.png')]
    r2_img = [pygame.image.load('art/leather.png'), pygame.image.load('art/iron.png'),
              pygame.image.load('art/coin.png'), pygame.image.load('art/plumbing.png'),
              pygame.image.load('art/electronics.png'), pygame.image.load('art/rocket.png')]
    r3_img = [pygame.image.load('art/rock.png'), pygame.image.load('art/stone-block.png'),
              pygame.image.load('art/religious.png'), pygame.image.load('art/education.png'),
              pygame.image.load('art/bills.png'), pygame.image.load('art/solar.png')]

    done = False
    fps = 100
    game = Tetris(20, 10)
    game.age = "Stone"
    counter = 0
    sceneNumber = 0
    screen.blit(sceneArray[a], (0, 0))
    pressing_down = False
    run = False
    rgb = False
    Music.play(sceneNumber)
    font = pygame.font.SysFont(name="Calibri", size=25)

    while not done:
        a = game.sceneNumber
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 10000000:
            counter = 0

        # A timer to make sure that the block are "falling"
        if not run:
            if counter % (fps // game.level) == 0 or pressing_down:
                if game.state == "start":
                    game.go_down()

            # Check for events in the game
            for event in pygame.event.get():
                # Song Loops
                if event.type == Music.Songs.STNEXT:
                    Music.playStoneLoop()
                elif event.type == Music.Songs.INEXT:
                    Music.playIronLoop()
                elif event.type == Music.Songs.MENEXT:
                    Music.playMedLoop()
                elif event.type == Music.Songs.MHNEXT:
                    Music.playMhLoop()
                elif event.type == Music.Songs.MANEXT:
                    Music.playMaLoop()
                elif event.type == Music.Songs.SPNEXT:
                    Music.playSpaceLoop()
                # Check for quit
                if event.type == pygame.QUIT:
                    done = True
                # Check for a key press
                if event.type == pygame.KEYDOWN:
                    # Up key to rotate
                    if event.key == pygame.K_x:
                        game.rotate()
                    if event.key == pygame.K_z:
                        game.Crotate()
                    # Down key to bring it down
                    if event.key == pygame.K_DOWN:
                        pressing_down = True
                    # Move the shape to the left
                    if event.key == pygame.K_LEFT:
                        game.go_side(-1)
                    # Move the shape to the right
                    if event.key == pygame.K_RIGHT:
                        game.go_side(1)
                    # Space to drop the shape
                    if event.key == pygame.K_SPACE:
                        game.drop()
                    # Slash to hold a figure
                    if event.key == pygame.K_c:
                        game.swap()
                    # ---Andy---Pause the game
                    if event.key == pygame.K_ESCAPE:
                        run = True
                    if event.key == pygame.K_f:
                        if not rgb:
                            rgb = True
                        else:
                            rgb = False
                    if event.key == pygame.K_k:
                        game.sceneNumber += 1
                        sceneNumber += 1
                        a += 1
                        Music.play(sceneNumber)
                        scene(sceneNumber)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        pressing_down = False

        else:
            # ---Andy---Check to unpause the game
            for event in pygame.event.get():
                # Check for quit
                if event.type == pygame.QUIT:
                    done = True
                # Check for a key press
                if event.type == pygame.KEYDOWN:
                    # Check for quit
                    if event.type == pygame.QUIT:
                        done = True
                    # Pause the game
                    if event.key == pygame.K_ESCAPE:
                        run = False

        # ---Aleks---Insert background(behind grid)
        screen.blit(sceneArray[a], (0, 0))
        # displays each resource and its current count
        screen.blit(r1_img[sceneNumber], (0, 0))
        screen.blit(r2_img[sceneNumber], (0, 47))
        screen.blit(r3_img[sceneNumber], (0, 94))
        res1_text = font.render(str(game.resc[0]), True, BLACK, BURLYWOOD)
        res2_text = font.render(str(game.resc[1]), True, BLACK, BURLYWOOD)
        res3_text = font.render(str(game.resc[2]), True, BLACK, BURLYWOOD)
        screen.blit(res1_text, (60, 20))
        screen.blit(res2_text, (60, 68))
        screen.blit(res3_text, (60, 110))

        # Check for power up game loop effects
        if game.game_loop_effect == 1 and fps > 25:
            fps -= 75
        game.game_loop_effect = 0

        # Draw the board to the window
        for i in range(game.height):
            for j in range(game.width):
                # ---Aleks---changed grid color to black to enhance shape visibility
                pygame.draw.rect(screen, BLACK, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom],
                                 1)
                if game.field[i][j] > -1:
                    if rgb:
                        pygame.draw.rect(screen, RGB[randint(0, len(RGB) - 1)], [
                            game.x + game.zoom * j + 1, game.y + game.zoom * i + 1,
                            game.zoom - 2, game.zoom - 1
                        ])
                    else:
                        pygame.draw.rect(screen, COLORS[game.field[i][j]], [
                            game.x + game.zoom * j + 1, game.y + game.zoom * i + 1,
                            game.zoom - 2, game.zoom - 1
                        ])
                        if game.field[i][j] in [7, 8, 9]:
                            img = POWERUP_IMGS[game.field[i][j] - 7]
                            scale = round(game.zoom * .80)
                            pos = (game.zoom - scale) // 2
                            transformed = pygame.transform.scale(img, (scale, scale))
                            screen.blit(
                                transformed,
                                (game.x + game.zoom * j + pos, game.y + game.zoom * i + pos, game.zoom, game.zoom)
                            )
        # Draw the shapes
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        if rgb:
                            pygame.draw.rect(screen, RGB[randint(0, len(RGB) - 1)], [
                                game.x + game.zoom * (j + game.figure.x) + 1,
                                game.y + game.zoom * (i + game.figure.y) + 1,
                                game.zoom - 2, game.zoom - 2
                            ])
                        else:
                            pygame.draw.rect(screen, COLORS[game.figure.color], [
                                game.x + game.zoom * (j + game.figure.x) + 1,
                                game.y + game.zoom * (i + game.figure.y) + 1,
                                game.zoom - 2, game.zoom - 2
                            ])

        # ---Andy---Draw a small grid to hold the next figure
        pygame.draw.rect(screen, BLACK, [315, 100, game.zoom + 60, game.zoom + 60], 1)

        # ---Andy---Draw a small grid to hold the next figure
        pygame.draw.rect(screen, BLACK, [315, 200, game.zoom + 60, game.zoom + 60], 1)

        # ---Andy---Draw the next figure that will be used
        if game.next_figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.next_figure.image():
                        if rgb:
                            pygame.draw.rect(screen, RGB[randint(0, len(RGB) - 1)], [
                                315 + game.zoom * j + 1,
                                100 + game.zoom * i + 1,
                                game.zoom - 2, game.zoom - 2
                            ])
                        else:
                            pygame.draw.rect(screen, COLORS[game.next_figure.color], [
                                315 + game.zoom * j + 1,
                                100 + game.zoom * i + 1,
                                game.zoom - 2, game.zoom - 2
                            ])

        # ---Andy---Draw the held figure
        if game.held_figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.held_figure.image():
                        if rgb:
                            pygame.draw.rect(screen, RGB[randint(0, len(RGB) - 1)], [
                                315 + game.zoom * j + 1,
                                200 + game.zoom * i + 1,
                                game.zoom - 2, game.zoom - 2
                            ])
                        else:
                            pygame.draw.rect(screen, COLORS[game.held_figure.color], [
                                315 + game.zoom * j + 1,
                                200 + game.zoom * i + 1,
                                game.zoom - 2, game.zoom - 2
                            ])

        # Fonts and texts
        # font = pygame.font.SysFont('Calibri', 65, True, False)
        # text_game_over = font.render("Game Over", True, (255, 125, 0))

        # print(game.score)

        # Output for game over
        if game.state == "game_over":
            # screen.blit(text_game_over, [20, 200])
            # ---Aleks---Inserted end screen NOT FUNCTIONAL
            # screen.blit(end, (0,0))
            final(game)

        pygame.display.flip()
        clock.tick(fps)


# a simple bubble sort used for the highscores by reference.
def sort_scores(scores):
    for i in range(len(scores)):
        is_sorted = True
        for j in range(len(scores) - i - 1):
            if scores[j][0] < scores[j + 1][0]:
                scores[j], scores[j + 1] = scores[j + 1], scores[j]
                is_sorted = False
        if is_sorted:
            break
    return


# scoreboard page that shows the highscores.
def scoreboard():
    pygame.display.set_caption("Ages and Resources - Scorboard")
    # fonts
    font = pygame.font.SysFont('Calibri', 20)
    title_font = pygame.font.SysFont(name="Calibri", size=30, bold=True)
    # create scoreboard surface of the same window size
    # maybe replace this with an image in the future?
    score_screen = pygame.display.set_mode(size)
    inner = pygame.Rect(30, 45, 340, 255)
    # title
    title = title_font.render("Highscores", True, BLACK)
    # high scores - listing without usernames #
    raw_scores = sql_wrapper.get_highscores()
    sort_scores(raw_scores)
    if SCOREBOARD_LEN < len(raw_scores):
        to_list = SCOREBOARD_LEN
    else:
        to_list = len(raw_scores)
    if len(raw_scores) > 0:
        header = font.render("Score        Age", True, BLACK)
        scores = [[header, (115, 100)]]
        for i in range(to_list):
            score_text = font.render(str(raw_scores[i][0]), True, BLACK)
            age_text = font.render(str(raw_scores[i][1]), True, BLACK)
            score_place = (115, 120 + (i * 20))
            age_place = (200, 120 + (i * 20))
            scores.append([score_text, score_place])
            scores.append([age_text, age_place])
    else:
        no_score_text = font.render("No scores to display", True, BLACK)
        scores = [[no_score_text, (115, 100)]]
    # back button
    back = pygame.Rect(150, 440, 100, 50)
    # back_text = font.render("Back", True, WHITE)
    # update the display and wait for quit or back
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # checks if the mouse click was on the button
                if back.collidepoint(mouse_pos):
                    # go back to the main menu
                    done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
        # draw background
        score_screen.fill(BLACK)
        pygame.draw.rect(score_screen, WHITE, inner)
        # draw title
        score_screen.blit(title, (130, 50))
        # draw back button
        # pygame.draw.rect(score_screen, BLACK, back)
        # score_screen.blit(back_text, (150, 440))
        # draw scores
        for i in range(len(scores)):
            score_screen.blit(scores[i][0], scores[i][1])

        pygame.display.update()
        clock.tick(15)


def control():
    pygame.display.set_caption("Ages and Resources - Controls")
    cont = pygame.image.load('art/controls.png')  # load controls
    cont_screen = pygame.display.set_mode(size)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
        cont_screen.fill((0, 0, 0))
        cont_screen.blit(cont, (0, 0))
        pygame.display.update()
        clock.tick(15)


# use to easily display multiple lines of text in a paragraph form.
# used in scene() to display the stories for the cut scenes.
# adapted from https://stackoverflow.com/a/42015712/13879313
def blit_paragraph(surface, text, pos, max_width, max_height, font, text_color, back_color):
    words = text.split()
    space = font.size(' ')[0]  # width of a space
    x, y = pos
    for word in words:
        word_surface = font.render(word, False, text_color, back_color)
        space_surface = font.render(" ", True, text_color, back_color)
        word_width, word_height = word_surface.get_size()
        # if we have reached the end of the available width,
        #  start on a new line, resetting x and incrementing y.
        if x + word_width >= max_width:
            x = pos[0]
            y += word_height
        surface.blit(word_surface, (x, y))
        x += word_width
        surface.blit(space_surface, (x, y))
        x += space
    return


def scene(sceneNumber):
    sceneArray = [pygame.image.load('art/b1wP.png'), pygame.image.load('art/background2.png'),
                  pygame.image.load('art/b3.png'), pygame.image.load('art/b4.png'),
                  pygame.image.load('art/b5.png'), pygame.image.load('art/pixil-frame-0.png')]
    scene_screen = pygame.display.set_mode(size)
    charArray = [pygame.image.load('art/b1wP.png'), pygame.image.load('art/char2.png'),
                 pygame.image.load('art/char3.png'), pygame.image.load('art/c4.png'),
                 pygame.image.load('art/c5-6.png'), pygame.image.load('art/c5-6.png')]
    font = pygame.font.SysFont(name="Calibri", size=15)
    storyArray = [
        "Alright, kid. We’re gonna stop wandering and try out that hunter-gatherer settlement thing. Gather as much stone and wood as you can! We’ll be using a ton of it for shelter. Oh, and get some leather while you’re at it. The winter will be rough without it. Gather 100 units of each!",
        "I heard you were trying to help out around here. Well, start producing some wheat – it’s plentiful and easy to grow. You won’t regret it. And about those houses . . . they’re going to need some reinforcements. Gather all the iron you can as well. And if you have time, cut that stone out back into blocks; we could repurpose that old stuff for our new designs. I need 200 units of each, if you would.",
        "Rorkshire, the city to the West, almost destroyed our castle! Their weapons are nice, and much better than ours! I’m worried about whether we'll hold up against them, should they attack again. Our gold and history of pacifism makes us a juicy target. The people pray in the church of the Twin Suns for hope, we need more icons. Could you help us rebuild our city, rearm our men, and reaffirm our faith? Collect at least 300 units of weapons molds, gold coins, and religious icons.",
        "I have this idea: it’s like a cart that moves through water. Will you help me build it? Maybe we can write a book about how we build it, too. Hire some more workers. By the way, I had a group of people build me a place just over the river that has running water, and I’d be more than willing to house you there for half the price if you work for me. Gather 400 units each of boats/cars, plumbing pipes, and books, and we’ll have a deal.",
        "Hey! You knocked over my oil lamp! You could have burned this place down! Oh, don’t try telling me about how I should be investing in electric lighting—my lamp works perfectly fine when clumsy people like you aren’t around. You owe me for that lamp—look, the frame is completely shattered. I don’t want coins, lad, I want dollar bills - can you believe we almost had rectangular bills, how stupid! If you really want me to get electric lighting, that’ll be up to how much you give me. Pay up, now. 500 units of oil, electronics, and paper money. Don’t be cheap now!",
        "Commander, we’re prepared for production. While Yuthasia has the most nuclear weapons right now, we have a whole team ready to build up our supply. Yuthasia won’t strike if we have an arsenal too… I hope. We also have a factory for our large scale rocket ships. At this rate, we’ll be the first to colonize Mars, and at that point shouldn’t need to worry about escaping the nuclear war on Earth any longer. Good thing we’ve got solar panel production down pat. Yes, we can still use solar power on Mars. As many panels, bombs, and ships as we can produce? We’re on it, commander. "]
    done = False

    while not done:
        scene_screen.blit(sceneArray[sceneNumber], (0, 0))
        # display the story for this cut scene.
        blit_paragraph(scene_screen, storyArray[sceneNumber], (35, 80), 350, 420, font, BLACK, BURLYWOOD)
        if sceneNumber > 0:
            scene_screen.blit(charArray[sceneNumber], (0, 322))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
        pygame.display.update()
        clock.tick(15)


def credit():
    pygame.display.set_caption("Ages and Resources - Credits")
    cred = pygame.image.load('art/credits.png')  # load controls
    cred_screen = pygame.display.set_mode(size)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
        cred_screen.fill((0, 0, 0))
        cred_screen.blit(cred, (0, 0))
        pygame.display.update()
        clock.tick(15)


def final(game):
    # inserting the score into the highscores database table.
    # if there is room on the scoreboard, insert the value.
    num_scores = sql_wrapper.get_num_highscores()
    if num_scores < SCOREBOARD_LEN:
        sql_wrapper.create_highscore((game.score, game.age))
    else:
        # if there is no room on the scoreboard and the score is higher than
        #  at least one other, take out the lowest score and insert the new score.
        lowest_score = sql_wrapper.get_lowest_highscore()
        if game.score > lowest_score:
            sql_wrapper.delete_highscore(lowest_score)
            sql_wrapper.create_highscore((game.score, game.age))
    # displaying the screen
    pygame.display.set_caption("Ages and Resources - Game Over")
    end = pygame.image.load('art/end-screen.png')  # load end
    end_screen = pygame.display.set_mode(size)
    pygame.mixer.quit()
    font = pygame.font.SysFont(name="Calibri", size=20, bold=True)
    score_text = font.render(str(game.score), True, RED)
    age_text = font.render(game.age, True, RED)
    restart = pygame.Rect(85, 220, 200, 70)
    leave = pygame.Rect(85, 330, 200, 70)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if restart.collidepoint(mouse_pos):
                    done = False
                    game_intro()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if leave.collidepoint(mouse_pos):
                    done = False
                    quit()
        end_screen.fill((0, 0, 0))
        end_screen.blit(end, (0, 0))
        end_screen.blit(score_text, (230, 117))
        end_screen.blit(age_text, (230, 131))
        pygame.draw.rect(screen, (250, 115, 115), restart, 5)
        pygame.draw.rect(screen, (250, 115, 115), leave, 5)

        pygame.display.update()
        clock.tick(15)


game_intro()
game_loop()
pygame.quit()
