import arcade
from utils import load_texture


class Button:
    def __init__(self, x, y, width, height, color, callback, text="", text_color=arcade.color.WHITE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.callback = callback
        self.text = text
        self.text_color = text_color
        self.hovered = False

    def draw(self):
        color = arcade.color.GRAY if self.hovered else self.color
        rect = arcade.types.XYWH(self.x, self.y, self.width, self.height)
        arcade.draw_rect_filled(rect, color)
        arcade.draw_rect_outline(rect, arcade.color.BLACK)
        if self.text:
            arcade.draw_text(
                self.text,
                self.x, self.y,
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
        self.setup_menu_buttons()

    # Расстояние между центрами кнопок (высота кнопки 60 → зазор 80px)
    BUTTON_SPACING = 140

    def setup_menu_buttons(self):
        center_x = self.game.width // 2
        center_y = self.game.height // 2

        start_btn = Button(
            center_x, center_y,
            200, 60, arcade.color.DARK_GREEN,
            self.game.start_game,
            "НАЧАТЬ ИГРУ"
        )
        exit_btn = Button(
            center_x, center_y - self.BUTTON_SPACING,
            200, 60, arcade.color.DARK_RED,
            self.game.close,
            "ВЫХОД"
        )
        self.buttons = [start_btn, exit_btn]

    def _apply_menu_button_positions(self, game_over=False):
        """Задаёт позиции кнопок: на экране Game Over сдвигаем вниз, чтобы не пересекались с текстом."""
        cx = self.game.width // 2
        cy = self.game.height // 2
        if game_over:
            self.buttons[0].y = cy - 80
            self.buttons[1].y = cy - 80 - self.BUTTON_SPACING
        else:
            self.buttons[0].y = cy
            self.buttons[1].y = cy - self.BUTTON_SPACING

    def draw_menu_buttons(self, game_over=False):
        self._apply_menu_button_positions(game_over)
        for button in self.buttons:
            button.draw()

        if game_over:
            arcade.draw_text(
                "ИГРА ЗАВЕРШЕНА",
                self.game.width // 2, self.game.height // 2 + 150,
                arcade.color.GOLD, 48, anchor_x="center"
            )
            arcade.draw_text(
                f"СЧЁТ: {self.game.score}",
                self.game.width // 2, self.game.height // 2 + 80,
                arcade.color.WHITE, 36, anchor_x="center"
            )
            arcade.draw_text(
                f"ДЕНЬГИ: ${self.game.money}",
                self.game.width // 2, self.game.height // 2 + 30,
                arcade.color.GREEN, 36, anchor_x="center"
            )

    def update_menu_hover(self, x, y, game_over=False):
        self._apply_menu_button_positions(game_over)
        for button in self.buttons:
            button.check_hover(x, y)

    def check_menu_click(self, x, y, game_over=False):
        self._apply_menu_button_positions(game_over)
        for button in self.buttons:
            if button.check_click(x, y):
                return True
        return False

    def draw_hud(self):
        """На основном экране: только таблица денег/времени и кнопка перехода на кухню."""
        # Панель: деньги, счёт, время (слева сверху)
        panel_rect = arcade.types.XYWH(150, 680, 280, 80)
        arcade.draw_rect_filled(panel_rect, arcade.color.DARK_GRAY)
        arcade.draw_rect_outline(panel_rect, arcade.color.BLACK)

        arcade.draw_text(f"ДЕНЬГИ: ${self.game.money}", 150, 700, arcade.color.GOLD, 20, anchor_x="center")
        arcade.draw_text(f"СЧЁТ: {self.game.score}", 150, 680, arcade.color.WHITE, 20, anchor_x="center")
        time_left = self.game.level_manager.get_time_remaining()
        arcade.draw_text(f"ВРЕМЯ: {time_left}с", 150, 660, arcade.color.RED, 20, anchor_x="center")

        # Кнопка перехода на кухню (справа сверху)
        kitchen_bg = arcade.types.XYWH(1150, 680, 100, 50)
        arcade.draw_rect_filled(kitchen_bg, arcade.color.DARK_GREEN)
        arcade.draw_rect_outline(kitchen_bg, arcade.color.BLACK, 2)
        arcade.draw_text(
            "КУХНЯ",
            1150, 680,
            arcade.color.WHITE, 16, anchor_x="center", anchor_y="center", bold=True
        )

    def check_hud_click(self, x, y):
        # Кнопка перехода на кухню (1150, 680, 100x50)
        if (1100 <= x <= 1200) and (655 <= y <= 705):
            self.game.show_cooking_frame = not self.game.show_cooking_frame
            return True
        return False