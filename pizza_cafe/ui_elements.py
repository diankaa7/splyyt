import arcade
from constants import *


class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = BUTTON_HOVER_COLOR
        self.is_hovered = False
        self.is_visible = True
        self.is_active = True
        self.texture = None

    def draw(self):
        if not self.is_visible:
            return

        if not self.is_active:
            color = (150, 150, 150)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, color)

        if self.texture:
            arcade.draw_texture_rectangle(self.x, self.y,
                                          self.width * 0.8, self.height * 0.8,
                                          self.texture)

        if self.text:
            text_color = TEXT_COLOR if self.is_active else (200, 200, 200)
            arcade.draw_text(self.text, self.x, self.y, text_color, FONT_SIZE,
                             anchor_x="center", anchor_y="center", bold=True)

    def check_hover(self, mouse_x, mouse_y):
        if not self.is_visible or not self.is_active:
            self.is_hovered = False
            return False

        self.is_hovered = (
                abs(mouse_x - self.x) < self.width / 2 and
                abs(mouse_y - self.y) < self.height / 2
        )
        return self.is_hovered

    def is_clicked(self, mouse_x, mouse_y):
        if not self.is_visible or not self.is_active:
            return False

        return (
                abs(mouse_x - self.x) < self.width / 2 and
                abs(mouse_y - self.y) < self.height / 2
        )


class ProgressBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = 0
        self.max_value = 100
        self.color = (0, 200, 0)
        self.bg_color = (100, 100, 100)

    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.bg_color)
        fill_width = (self.value / self.max_value) * self.width
        arcade.draw_rectangle_filled(self.x - self.width / 2 + fill_width / 2,
                                     self.y, fill_width, self.height, self.color)
        arcade.draw_rectangle_outline(self.x, self.y, self.width, self.height,
                                      (255, 255, 255))


class TimerDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_left = 0
        self.total_time = 0
        self.texture = None

    def draw(self):
        if self.texture:
            arcade.draw_texture_rectangle(self.x - 40, self.y, 40, 40, self.texture)

        time_color = (255, 255, 255)
        if self.time_left < 10:
            time_color = (255, 100, 100)
        elif self.time_left < 30:
            time_color = (255, 200, 100)

        arcade.draw_text(f"{int(self.time_left)}с", self.x + 20, self.y,
                         time_color, FONT_SIZE, anchor_x="left", anchor_y="center", bold=True)

        if self.total_time > 0:
            bar_width = 200
            bar_height = 15
            fill_width = (self.time_left / self.total_time) * bar_width
            bar_color = (0, 200, 0)

            if self.time_left < self.total_time * 0.3:
                bar_color = (255, 100, 100)
            elif self.time_left < self.total_time * 0.6:
                bar_color = (255, 200, 100)

            arcade.draw_rectangle_filled(self.x - bar_width / 2 + fill_width / 2,
                                         self.y - 25, fill_width, bar_height, bar_color)
            arcade.draw_rectangle_outline(self.x, self.y - 25,
                                          bar_width, bar_height, (255, 255, 255))


class MoneyDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.money = 0
        self.target = 0
        self.texture = None

    def draw(self):
        if self.texture:
            arcade.draw_texture_rectangle(self.x - 40, self.y, 40, 40, self.texture)

        arcade.draw_text(f"${self.money}", self.x + 20, self.y,
                         (255, 255, 255), FONT_SIZE, anchor_x="left", anchor_y="center", bold=True)

        arcade.draw_text(f"Цель: ${self.target}", self.x, self.y - 30,
                         (255, 255, 0), FONT_SIZE, anchor_x="center", anchor_y="center")

        progress = min(1.0, self.money / self.target) if self.target > 0 else 0
        bar_width = 200
        bar_height = 15
        fill_width = progress * bar_width

        arcade.draw_rectangle_filled(self.x - bar_width / 2 + fill_width / 2,
                                     self.y - 50, fill_width, bar_height,
                                     (255, 215, 0))
        arcade.draw_rectangle_outline(self.x, self.y - 50,
                                      bar_width, bar_height, (255, 255, 255))


class LevelDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.customers_served = 0
        self.total_customers = 0
        self.texture = None

    def draw(self):
        if self.texture:
            arcade.draw_texture_rectangle(self.x - 40, self.y, 40, 40, self.texture)

        arcade.draw_text(f"Уровень {self.level}", self.x + 20, self.y,
                         (255, 255, 255), FONT_SIZE, anchor_x="left", anchor_y="center", bold=True)

        arcade.draw_text(f"Клиенты: {self.customers_served}/{self.total_customers}",
                         self.x, self.y - 30, (255, 255, 255), FONT_SIZE, anchor_x="center")

        progress = self.customers_served / self.total_customers if self.total_customers > 0 else 0
        bar_width = 200
        bar_height = 15
        fill_width = progress * bar_width

        arcade.draw_rectangle_filled(self.x - bar_width / 2 + fill_width / 2,
                                     self.y - 50, fill_width, bar_height,
                                     (100, 200, 255))
        arcade.draw_rectangle_outline(self.x, self.y - 50,
                                      bar_width, bar_height, (255, 255, 255))


class MessageDisplay:
    def __init__(self, x, y, width=400, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.message = ""
        self.timer = 0
        self.duration = 2
        self.is_visible = False

    def show_message(self, message, duration=2):
        self.message = message
        self.timer = duration
        self.duration = duration
        self.is_visible = True

    def update(self, delta_time):
        if self.is_visible and self.timer > 0:
            self.timer -= delta_time
            if self.timer <= 0:
                self.is_visible = False

    def draw(self):
        if self.is_visible and self.message:
            alpha = min(255, int((self.timer / self.duration) * 255))
            bg_color = (50, 50, 50, alpha)
            text_color = (255, 255, 255, alpha)

            arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, bg_color)
            arcade.draw_text(self.message, self.x, self.y, text_color, FONT_SIZE,
                             anchor_x="center", anchor_y="center", bold=True)