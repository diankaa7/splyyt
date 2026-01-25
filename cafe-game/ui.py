import arcade
from utils import load_texture


class Button:
    def __init__(self, x, y, texture, callback, text="", text_color=arcade.color.WHITE):
        self.x = x
        self.y = y
        self.texture = texture
        self.width = texture.width
        self.height = texture.height
        self.callback = callback
        self.text = text
        self.text_color = text_color
        self.hovered = False

    def draw(self):
        arcade.draw_texture_rectangle(
            self.x, self.y,
            self.width, self.height,
            self.texture
        )
        if self.text:
            arcade.draw_text(
                self.text,
                self.x, self.y - 10,
                self.text_color, 24, anchor_x="center", anchor_y="center"
            )

    def check_click(self, x, y):
        if (self.x - self.width / 2 < x < self.x + self.width / 2 and
                self.y - self.height / 2 < y < self.y + self.height / 2):
            self.callback()
            return True
        return False

    def check_hover(self, x, y):
        self.hovered = (self.x - self.width / 2 < x < self.x + self.width / 2 and
                        self.y - self.height / 2 < y < self.y + self.height / 2)
        return self.hovered


class UIManager:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.money_icon = load_texture()
        self.timer_icon = load_texture()
        self.trash_texture = load_texture()
        self.setup_menu_buttons()

    def setup_menu_buttons(self):
        start_btn = Button(
            self.game.width // 2, self.game.height // 2,
            load_texture(),
            self.game.start_game,
            "START GAME"
        )
        exit_btn = Button(
            self.game.width // 2, self.game.height // 2 - 100,
            load_texture(),
            self.game.close,
            "EXIT GAME"
        )
        self.buttons = [start_btn, exit_btn]

    def draw_menu_buttons(self, game_over=False):
        for button in self.buttons:
            button.draw()

        if game_over:
            arcade.draw_text(
                "REPLAY?",
                self.game.width // 2, self.game.height // 2 + 200,
                arcade.color.GOLD, 48, anchor_x="center"
            )

    def update_menu_hover(self, x, y, game_over=False):
        for button in self.buttons:
            button.check_hover(x, y)

    def check_menu_click(self, x, y, game_over=False):
        for button in self.buttons:
            if button.check_click(x, y):
                return True
        return False

    def draw_hud(self):
        # Money display
        arcade.draw_texture_rectangle(80, 680, 40, 40, self.money_icon)
        arcade.draw_text(f"${self.game.money}", 110, 675, arcade.color.GOLD, 24)

        # Timer display
        time_left = self.game.level_manager.get_time_remaining()
        arcade.draw_texture_rectangle(80, 630, 40, 40, self.timer_icon)
        arcade.draw_text(f"{time_left}s", 110, 625, arcade.color.RED, 24)

        # Score display
        arcade.draw_text(f"SCORE: {self.game.score}", 80, 580, arcade.color.WHITE, 20)

        # Level display
        arcade.draw_text(
            f"LEVEL {self.game.current_level}",
            self.game.width - 100, 680,
            arcade.color.BLUE, 24, anchor_x="right"
        )

        # Trash can
        arcade.draw_texture_rectangle(1200, 650, 60, 60, self.trash_texture)

        # Objective
        obj_score = self.game.level_manager.current_level.objective_score
        arcade.draw_text(
            f"OBJECTIVE: {self.game.score}/{obj_score}",
            self.game.width - 150, 630,
            arcade.color.YELLOW, 20, anchor_x="right"
        )

    def check_hud_click(self, x, y):
        # Check trash can click
        if (1170 < x < 1230) and (620 < y < 680):
            self.game.food_manager.reset_inventory()
            return True
        return False