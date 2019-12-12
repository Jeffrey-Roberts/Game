# All graphics and sound from https://kenney.nl

import arcade
import os

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Game"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.85
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 1
PLAYER_JUMP_SPEED = 18

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 35
PLAYER_START_Y = 640

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


class MenuView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_texture_rectangle((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2),
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      arcade.load_texture("Backgrounds/backgroundMenu.png"))

        arcade.draw_text("Click to advance", SCREEN_WIDTH/2, 25,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        instructions_view = InstructionView()
        self.window.show_view(instructions_view)


class InstructionView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_texture_rectangle((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2),
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      arcade.load_texture("Backgrounds/backgroundForest.png"))

        arcade.draw_text("Instructions", SCREEN_WIDTH/2, SCREEN_HEIGHT-75,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # -- Jump
        arcade.draw_texture_rectangle(SCREEN_WIDTH/3, SCREEN_HEIGHT-145, 80, 80,
                                      arcade.load_texture("UI/flatDark/flatDark35.png"))

        arcade.draw_text("Jump", SCREEN_WIDTH/2, SCREEN_HEIGHT-160,
                         arcade.color.BLACK, font_size=35, anchor_x="center")

        arcade.draw_texture_rectangle(SCREEN_WIDTH/3 + 325, SCREEN_HEIGHT-135, 96, 96,
                                      arcade.load_texture("Characters/platformChar_jump.png"))

        # -- Left
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3, SCREEN_HEIGHT - 230, 80, 80,
                                      arcade.load_texture("UI/flatDark/flatDark36.png"))

        arcade.draw_text("Left", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 245,
                         arcade.color.BLACK, font_size=35, anchor_x="center")

        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3 + 325, SCREEN_HEIGHT - 225, 96, 96,
                                      arcade.load_texture("Characters/platformChar_walk1MIRROR.png"))

        # -- Down
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3, SCREEN_HEIGHT - 315, 80, 80,
                                      arcade.load_texture("UI/flatDark/flatDark37.png"))

        arcade.draw_text("Down", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 330,
                         arcade.color.BLACK, font_size=35, anchor_x="center")

        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3 + 325, SCREEN_HEIGHT - 310, 96, 96,
                                      arcade.load_texture("Characters/platformChar_climb1.png"))

        # -- Right
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3, SCREEN_HEIGHT - 400, 80, 80,
                                      arcade.load_texture("UI/flatDark/flatDark38.png"))

        arcade.draw_text("Right", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 415,
                         arcade.color.BLACK, font_size=35, anchor_x="center")

        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3 + 325, SCREEN_HEIGHT - 390, 96, 96,
                                      arcade.load_texture("Characters/platformChar_walk1.png"))

        # -- Interact
        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3, SCREEN_HEIGHT - 485, 80, 80,
                                      arcade.load_texture("UI/flatDark/flatDark39.png"))

        arcade.draw_text("Interact", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 500,
                         arcade.color.BLACK, font_size=35, anchor_x="center")

        arcade.draw_texture_rectangle(SCREEN_WIDTH / 3 + 325, SCREEN_HEIGHT - 465, 96, 96,
                                      arcade.load_texture("Characters/platformChar_Duck.png"))

        arcade.draw_text("Click to advance", SCREEN_WIDTH/2, 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup(1)
        self.window.show_view(game_view)


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename, scale=CHARACTER_SCALING),
        arcade.load_texture(filename, scale=CHARACTER_SCALING, mirrored=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -40], [22, -40], [22, 15], [-22, 15]]

        # --- Load Textures ---
        main_path = "characters/platformChar"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_happy.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(1, 3):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb1.png", scale=CHARACTER_SCALING)
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb2.png", scale=CHARACTER_SCALING)
        self.climbing_textures.append(texture)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Jumping animation
        if self.jumping and not self.is_on_ladder:
            if self.change_y >= 0:
                self.texture = self.jump_texture_pair[self.character_face_direction]
            else:
                self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 1:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer for the game
        """

        # Call the parent class and set up the window
        super().__init__()

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Background
        self.background = None
        self.game_over_sound = False

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.interact_pressed = False

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.moving_wall_list = None
        self.background_list = None
        self.ladder_list = None
        self.player_list = None
        self.foreground_list = None
        self.door_list = None
        self.deadly_list = None
        self.lives_list = None
        self.coin_block_list = None

        self.player_sprite = None
        self.physics_engine = None

        # Used to keep track of scrolling
        self.view_bottom = 0
        self.view_left = 0
        self.end_of_map = 0

        # Keep track of the score
        self.score = 0

        # Keep track of lives
        self.lives = 3

        # Levels
        self.level = 1

        # Time Taken
        self.time_taken = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.interact_sound = arcade.load_sound("sounds/upgrade5.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.hurt_sound = arcade.load_sound("sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound("sounds/hit1.wav")
        self.game_over_sound = arcade.load_sound("sounds/gameover2.wav")
        self.victory_sound = arcade.load_sound("sounds/secret4.wav")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Background
        if self.level == 1:
            self.background = arcade.load_texture("Backgrounds/backgroundEmpty.png")

        if self.level == 2:
            self.background = arcade.load_texture("Backgrounds/backgroundEmpty2.png")

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.moving_wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.door_list = arcade.SpriteList()
        self.deadly_list = arcade.SpriteList()
        self.lives_list = arcade.SpriteList()
        self.coin_block_list = arcade.SpriteList()

        # Player setup
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        map_name = f"Level{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(my_map, "Platforms", TILE_SCALING)

        # -- Background objects
        self.background_list = arcade.tilemap.process_layer(my_map, "Background", TILE_SCALING)

        # -- Background objects
        self.ladder_list = arcade.tilemap.process_layer(my_map, "Ladders", TILE_SCALING)

        # -- Foreground Objects
        self.foreground_list = arcade.tilemap.process_layer(my_map, "Foreground", TILE_SCALING)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, "Coins", TILE_SCALING)

        # -- Coin blocks
        self.coin_block_list = arcade.tilemap.process_layer(my_map, "Coin Blocks", TILE_SCALING)

        # -- Door
        self.door_list = arcade.tilemap.process_layer(my_map, "Door", TILE_SCALING)

        # -- Deadly objects
        self.deadly_list = arcade.tilemap.process_layer(my_map, "Deadly", TILE_SCALING)

        # -- Lives
        for x in range(self.lives):
            heart = arcade.Sprite("HUD/hudHeart_full.png", TILE_SCALING)
            self.lives_list.append(heart)

        # Set background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

        # -- Level 2 Obstacles
        if self.level == 2:

            # Group 1
            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 17 + 32
            wall.center_y = GRID_PIXEL_SIZE * 5 + 32
            wall.change_x = -7 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 26
            wall.boundary_left = GRID_PIXEL_SIZE * 9
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            # Group 2
            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 34 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 3 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 37 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 5 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 34 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 7 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 37 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 9 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 34 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 11 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 37 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 13 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 34 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 15 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 37 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 17 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 34 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 19 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 37 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 21 + 32)
            wall.change_x = 2 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 37
            wall.boundary_left = GRID_PIXEL_SIZE * 33
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            # Group 3
            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 70 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 16 + 32)
            wall.change_x = 7 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 76
            wall.boundary_left = GRID_PIXEL_SIZE * 70
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 82 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 16 + 32)
            wall.change_x = 7 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 82
            wall.boundary_left = GRID_PIXEL_SIZE * 76
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 82 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 16 + 32)
            wall.change_x = 7 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 88
            wall.boundary_left = GRID_PIXEL_SIZE * 82
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

            wall = arcade.Sprite("Ground/Stone/stoneHalf.png", TILE_SCALING)
            wall.center_x = GRID_PIXEL_SIZE * 94 + 32
            wall.center_y = (GRID_PIXEL_SIZE * 16 + 32)
            wall.change_x = 7 * TILE_SCALING
            wall.boundary_right = GRID_PIXEL_SIZE * 94
            wall.boundary_left = GRID_PIXEL_SIZE * 88
            self.moving_wall_list.append(wall)
            self.wall_list.append(wall)

    def setup_game(self):
        self.score = 0
        self.time_taken = 0

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Background
        arcade.draw_texture_rectangle(self.view_left + (SCREEN_WIDTH / 2), self.view_bottom + (SCREEN_HEIGHT / 2),
                                      SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Draw sprites
        self.wall_list.draw()
        self.background_list.draw()
        self.ladder_list.draw()
        self.coin_list.draw()
        self.door_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()
        self.deadly_list.draw()
        self.coin_block_list.draw()
        self.lives_list.draw()

        if self.level == 2:
            self.moving_wall_list.draw()

        # Draw score
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, self.view_left + 10, self.view_bottom + 30,
                         arcade.color.BLACK, font_size=20)

        # Draw time
        time_taken_formatted = f"{round(self.time_taken, 2)}"
        arcade.draw_text(f"Time: {time_taken_formatted}",
                         self.view_left + 10,
                         self.view_bottom + 10,
                         arcade.color.BLACK,
                         font_size=20,)

        # Game Over Check
        if len(self.lives_list) == 0 and self.lives == 0:
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            self.window.show_view(game_over_view)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if len(self.lives_list) != 0 and self.lives != 0:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up_pressed = True
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down_pressed = True
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = True

        self.process_keychange()

        if key == arcade.key.E:
            self.interact_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if len(self.lives_list) != 0 and self.lives != 0:
            if key == arcade.key.UP or key == arcade.key.W:
                self.up_pressed = False
                self.jump_needs_reset = False
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.down_pressed = False
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.left_pressed = False
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.right_pressed = False

        self.process_keychange()

        if key == arcade.key.E:
            self.interact_pressed = False

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.physics_engine.update()

        self.time_taken += delta_time

        # --- Interaction Check ---

        # Deadly collision
        if arcade.check_for_collision_with_list(self.player_sprite, self.deadly_list) or self.player_sprite.bottom <= 0:
            self.player_sprite.center_x = 1/2 * GRID_PIXEL_SIZE
            self.player_sprite.center_y = PLAYER_START_Y
            self.player_sprite.change_y = 0
            self.lives -= 1
            arcade.play_sound(self.hurt_sound)
            if len(self.lives_list) > 0:
                self.lives_list[0].kill()
            if self.lives == 0:
                arcade.play_sound(self.game_over_sound)

        # Door collision
        if arcade.check_for_collision_with_list(self.player_sprite, self.door_list) and self.interact_pressed:
            if self.level == 2:
                arcade.play_sound(self.victory_sound)
                victory_view = VictoryView()
                victory_view.time_taken = self.time_taken
                self.window.show_view(victory_view)
            else:
                self.player_sprite.center_x = GRID_PIXEL_SIZE / 2
                self.level += 1
                arcade.play_sound(self.interact_sound)
                self.setup(self.level)

        # Coin Block collision
        coin_block_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                   self.coin_block_list)
        for block in coin_block_hit_list:
            self.score += 1
            self.window.score += 1
            hit_points = int(block.properties['hit_points'])
            arcade.play_sound(self.collect_coin_sound)
            arcade.play_sound(self.hit_sound)
            hit_points -= 1
            block.properties['hit_points'] = str(hit_points)
            self.player_sprite.change_y = -1

            if hit_points == 0:
                block.remove_from_sprite_lists()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.player_list.update_animation(delta_time)
        self.deadly_list.update_animation(delta_time)
        self.foreground_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)

        # Wall boundary detection
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # Coin collision
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        for coin in coin_hit_list:

            # Figure out how many points this coin is worth
            if 'Points' not in coin.properties:
                print("Warning, collected a coin without a Points property.")
                self.score += 1
                self.window.score += 1
            else:
                points = int(coin.properties['Points'])
                self.score += points
                self.window.score += points

            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)

        # --- Manage Scrolling ---
        changed_viewport = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        # Lives counter
        for i in range(len(self.lives_list)):
            self.lives_list[i].center_y = self.view_bottom + (SCREEN_HEIGHT * 15 / 16)
            self.lives_list[i].center_x = self.view_left + 32 + 64 * i


class VictoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_taken = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("You Win!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time: {time_taken_formatted}",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2 - 25,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

        output_total = f"Final Score: {self.window.score}"
        arcade.draw_text(output_total, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 25,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup(1)
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_taken = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 75,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to restart", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time: {time_taken_formatted}",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2 - 25,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

        output_total = f"Final Score: {self.window.score}"
        arcade.draw_text(output_total, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 25,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup(1)
        self.window.show_view(game_view)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.score = 0
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
