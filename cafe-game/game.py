import arcade

from customer import CustomerManager
from food import FoodManager
from levels import LevelManager
from order_system import OrderSystem
from ui import UIManager
from utils import load_texture


class FastFoodGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.game_state = "MENU"
        self.current_level = 1
        self.money = 500
        self.score = 0
        self.level_manager = None
        self.customer_manager = None
        self.food_manager = None
        self.ui_manager = None
        self.order_system = None
        self.background = None
        self.player_sprite = None
        self.equipment_sprites = None
        self.setup_managers()

    def setup_managers(self):
        self.level_manager = LevelManager(self)
        self.customer_manager = CustomerManager(self)
        self.food_manager = FoodManager(self)
        self.ui_manager = UIManager(self)
        self.order_system = OrderSystem(self)

    def setup(self):
        self.background = load_texture("images/main_menu_bg.png")
        self.player_sprite = arcade.Sprite("images/player_idle.png", 0.8)
        self.player_sprite.center_x = 300
        self.player_sprite.center_y = 250
        self.setup_equipment()

    def setup_equipment(self):
        self.equipment_sprites = arcade.SpriteList()
        positions = [(450, 320), (550, 320), (650, 320), (750, 320)]
        equipment = ["grill", "fryer", "ice_cream_machine", "soda_tap"]
        for i, pos in enumerate(positions):
            sprite = arcade.Sprite(f"images/{equipment[i]}.png", 0.7)
            sprite.center_x = pos[0]
            sprite.center_y = pos[1]
            self.equipment_sprites.append(sprite)

    def start_game(self):
        self.game_state = "PLAYING"
        self.current_level = 1
        self.money = 500
        self.score = 0
        self.level_manager.load_level(self.current_level)
        self.customer_manager.setup_customers()
        self.food_manager.reset_inventory()
        self.order_system.reset_orders()
        self.background = load_texture(f"images/level{self.current_level}_bg.png")

    def next_level(self):
        self.current_level += 1
        if self.current_level > 7:
            self.game_state = "GAME_OVER"
            return
        self.level_manager.load_level(self.current_level)
        self.customer_manager.setup_customers()
        self.background = load_texture(f"images/level{self.current_level}_bg.png")

    def game_over(self):
        self.game_state = "GAME_OVER"

    def on_draw(self):
        arcade.start_render()
        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "PLAYING":
            self.draw_game()
        elif self.game_state == "PAUSED":
            self.draw_game()
            self.draw_pause_overlay()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over()

    def draw_menu(self):
        arcade.draw_texture_rectangle(
            self.width // 2, self.height // 2,
            1920, 1080,
            self.background
        )
        arcade.draw_text(
            "FASTFOOD FRENZY",
            self.width // 2, self.height - 150,
            arcade.color.GOLD, 72, anchor_x="center"
        )
        self.ui_manager.draw_menu_buttons()

    def draw_game(self):
        arcade.draw_texture_rectangle(
            self.width // 2, self.height // 2,
            1280, 720,
            self.background
        )
        self.equipment_sprites.draw()
        self.food_manager.draw()
        self.customer_manager.draw()
        self.player_sprite.draw()
        self.ui_manager.draw_hud()
        self.order_system.draw_orders()

    def draw_pause_overlay(self):
        arcade.draw_rectangle_filled(
            self.width // 2, self.height // 2,
            self.width, self.height,
            arcade.color.BLACK_TRANSLUCENT
        )
        arcade.draw_text(
            "PAUSED",
            self.width // 2, self.height // 2,
            arcade.color.WHITE, 64, anchor_x="center"
        )
        arcade.draw_text(
            "Press ESC to resume",
            self.width // 2, self.height // 2 - 80,
            arcade.color.GRAY, 24, anchor_x="center"
        )

    def draw_game_over(self):
        arcade.draw_texture_rectangle(
            self.width // 2, self.height // 2,
            1280, 720,
            self.background
        )
        arcade.draw_text(
            "CAMPAIGN COMPLETE!",
            self.width // 2, self.height - 150,
            arcade.color.GOLD, 54, anchor_x="center"
        )
        arcade.draw_text(
            f"Final Score: {self.score}",
            self.width // 2, self.height - 250,
            arcade.color.WHITE, 36, anchor_x="center"
        )
        arcade.draw_text(
            f"Total Money: ${self.money}",
            self.width // 2, self.height - 300,
            arcade.color.WHITE, 36, anchor_x="center"
        )
        self.ui_manager.draw_menu_buttons(game_over=True)

    def on_update(self, delta_time):
        if self.game_state != "PLAYING":
            return

        self.customer_manager.update(delta_time)
        self.food_manager.update(delta_time)
        self.order_system.update(delta_time)
        self.level_manager.update(delta_time)

        if self.level_manager.is_level_complete():
            self.next_level()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.game_state == "PLAYING":
                self.game_state = "PAUSED" if self.game_state != "PAUSED" else "PLAYING"
            elif self.game_state == "PAUSED":
                self.game_state = "PLAYING"
            elif self.game_state == "MENU":
                self.close()

        if self.game_state == "PLAYING":
            if key == arcade.key.NUM_1:
                self.food_manager.select_ingredient("burger")
            elif key == arcade.key.NUM_2:
                self.food_manager.select_ingredient("fries")
            elif key == arcade.key.NUM_3:
                self.food_manager.select_ingredient("icecream")
            elif key == arcade.key.NUM_4:
                self.food_manager.select_ingredient("drink")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "MENU":
            self.ui_manager.check_menu_click(x, y)
        elif self.game_state == "GAME_OVER":
            self.ui_manager.check_menu_click(x, y, game_over=True)
        elif self.game_state == "PLAYING":
            self.ui_manager.check_hud_click(x, y)
            self.customer_manager.check_customer_click(x, y)
            self.food_manager.check_equipment_click(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_state == "MENU":
            self.ui_manager.update_menu_hover(x, y)
        elif self.game_state == "GAME_OVER":
            self.ui_manager.update_menu_hover(x, y, game_over=True)