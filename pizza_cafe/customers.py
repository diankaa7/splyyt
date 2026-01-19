import arcade

from constants import *


class Customer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.texture = None
        self.patience = 100
        self.max_patience = 100
        self.is_waiting = False
        self.wait_time = 0
        self.max_wait_time = 60
        self.mood = "neutral"
        self.name = ""
        self.expression_timer = 0
        self.current_expression = "neutral"

    def set_customer(self, level, name="", mood="neutral"):
        self.name = name
        self.mood = mood
        self.is_waiting = True
        self.wait_time = 0

        if mood == "impatient":
            self.max_wait_time = 40
            self.patience = 80
        elif mood == "picky":
            self.max_wait_time = 70
            self.patience = 60
        else:
            self.max_wait_time = 60
            self.patience = 100

        self.max_patience = self.patience

        try:
            texture_path = f"images/customer{min(level, 7)}.png"
            self.texture = arcade.load_texture(texture_path)
        except:
            self.texture = None

    def update(self, delta_time):
        if self.is_waiting:
            self.wait_time += delta_time
            self.patience = max(0, self.max_patience -
                                (self.wait_time / self.max_wait_time) * 100)

            if self.wait_time > self.max_wait_time * 0.7:
                self.current_expression = "angry"
                self.expression_timer = 1
            elif self.wait_time > self.max_wait_time * 0.4:
                self.current_expression = "impatient"
                self.expression_timer = 1
            else:
                if self.expression_timer <= 0:
                    self.current_expression = self.mood

        if self.expression_timer > 0:
            self.expression_timer -= delta_time

    def draw(self):
        if self.texture:
            arcade.draw_texture_rectangle(self.x, self.y, 120, 180, self.texture)

        if self.is_waiting:
            patience_bar_width = 100
            patience_bar_height = 10
            fill_width = (self.patience / 100) * patience_bar_width

            bar_color = (0, 200, 0)
            if self.patience < 30:
                bar_color = (255, 50, 50)
            elif self.patience < 60:
                bar_color = (255, 150, 50)

            arcade.draw_rectangle_filled(self.x, self.y + 110,
                                         patience_bar_width, patience_bar_height,
                                         (100, 100, 100))
            arcade.draw_rectangle_filled(self.x - patience_bar_width / 2 + fill_width / 2,
                                         self.y + 110, fill_width, patience_bar_height,
                                         bar_color)
            arcade.draw_rectangle_outline(self.x, self.y + 110,
                                          patience_bar_width, patience_bar_height,
                                          (255, 255, 255))

            if self.name:
                arcade.draw_text(self.name, self.x, self.y + 130,
                                 TEXT_COLOR_DARK, FONT_SIZE,
                                 anchor_x="center", anchor_y="center", bold=True)

            if self.current_expression == "angry":
                arcade.draw_text("☹️", self.x, self.y + 90,
                                 (255, 50, 50), 30, anchor_x="center")
            elif self.current_expression == "impatient":
                arcade.draw_text("😠", self.x, self.y + 90,
                                 (255, 150, 50), 30, anchor_x="center")
            elif self.current_expression == "happy":
                arcade.draw_text("😊", self.x, self.y + 90,
                                 (50, 200, 50), 30, anchor_x="center")
            elif self.current_expression == "picky":
                arcade.draw_text("🤨", self.x, self.y + 90,
                                 (200, 150, 50), 30, anchor_x="center")

    def leave(self):
        self.is_waiting = False
        return self.patience > 30