import arcade
from constants import *


class Drink:
    def __init__(self):
        self.state = DRINK_STATE_EMPTY
        self.drink_type = None
        self.fill_time = 0
        self.fill_progress = 0
        self.filled = False
        self.fill_level = 0
        self.ice = False
        self.quality = 100

    def set_drink_type(self, drink_type):
        if self.state == DRINK_STATE_EMPTY:
            self.drink_type = drink_type
            self.state = DRINK_STATE_FILLING
            self.fill_time = 0
            self.fill_progress = 0
            return True
        return False

    def update_filling(self, delta_time):
        if self.state == DRINK_STATE_FILLING:
            self.fill_time += delta_time
            self.fill_progress = (self.fill_time / FILL_TIME_MAX) * 100
            self.fill_level = min(100, (self.fill_time / FILL_TIME_MAX) * 100)

            if FILL_TIME_MIN <= self.fill_time <= FILL_TIME_MAX:
                self.filled = True
                self.quality = 100 - abs(self.fill_time - 3) * 15
            elif self.fill_time > FILL_TIME_MAX:
                self.quality = max(50, 100 - (self.fill_time - FILL_TIME_MAX) * 20)

    def finish_filling(self):
        if self.state == DRINK_STATE_FILLING and self.filled:
            self.state = DRINK_STATE_COMPLETE
            return True
        return False

    def add_ice(self):
        if self.state == DRINK_STATE_COMPLETE:
            self.ice = True
            return True
        return False

    def draw(self):
        cup_color = (200, 200, 200)
        rim_color = (150, 150, 150)

        arcade.draw_ellipse_filled(DRINK_X, DRINK_Y - 30, DRINK_RADIUS * 1.5, DRINK_RADIUS * 0.5, rim_color)
        arcade.draw_ellipse_outline(DRINK_X, DRINK_Y - 30, DRINK_RADIUS * 1.5, DRINK_RADIUS * 0.5, (100, 100, 100), 3)

        if self.state == DRINK_STATE_EMPTY:
            arcade.draw_triangle_filled(DRINK_X, DRINK_Y - 30, DRINK_X - DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2,
                                        DRINK_X + DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2, cup_color)
            arcade.draw_triangle_outline(DRINK_X, DRINK_Y - 30, DRINK_X - DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2,
                                         DRINK_X + DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2, (100, 100, 100), 3)
            arcade.draw_text("Выберите напиток!", DRINK_X, DRINK_Y + 80,
                             TEXT_COLOR, FONT_SIZE + 4, anchor_x="center")
            return

        drink_color = DRINK_COLORS.get(self.drink_type, (200, 200, 200))
        fill_height = DRINK_RADIUS * 2 * (self.fill_level / 100)

        bottom_y = DRINK_Y - DRINK_RADIUS * 2
        top_y = bottom_y + fill_height

        if fill_height > 0:
            points = [
                (DRINK_X, bottom_y + fill_height),
                (DRINK_X - DRINK_RADIUS * (1 - fill_height / (DRINK_RADIUS * 2)), bottom_y),
                (DRINK_X + DRINK_RADIUS * (1 - fill_height / (DRINK_RADIUS * 2)), bottom_y)
            ]
            arcade.draw_triangle_filled(points[0][0], points[0][1], points[1][0], points[1][1],
                                        points[2][0], points[2][1], drink_color)

        arcade.draw_triangle_outline(DRINK_X, DRINK_Y - 30, DRINK_X - DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2,
                                     DRINK_X + DRINK_RADIUS, DRINK_Y - DRINK_RADIUS * 2, (100, 100, 100), 3)

        if self.ice and self.filled:
            for i in range(3):
                for j in range(2):
                    ice_x = DRINK_X - 15 + i * 15
                    ice_y = DRINK_Y - 60 + j * 10
                    if ice_y < top_y - 10:
                        arcade.draw_circle_filled(ice_x, ice_y, 4, (200, 240, 255))

        if self.state == DRINK_STATE_FILLING:
            if self.filled:
                arcade.draw_text("ГОТОВО!", DRINK_X, DRINK_Y + 80,
                                 (0, 200, 0), 22, anchor_x="center", bold=True)
                arcade.draw_text(f"Качество: {int(self.quality)}%", DRINK_X, DRINK_Y + 110,
                                 (100, 255, 100), 18, anchor_x="center")
            else:
                progress = min(100, int((self.fill_time / FILL_TIME_MAX) * 100))
                arcade.draw_text(f"Наполнение: {progress}%", DRINK_X, DRINK_Y + 80,
                                 (200, 200, 255), 18, anchor_x="center")
                bar_width = 150
                bar_height = 15
                fill_width = (self.fill_progress / 100) * bar_width
                arcade.draw_rectangle_filled(DRINK_X - bar_width / 2 + fill_width / 2,
                                             DRINK_Y + 100, fill_width, bar_height,
                                             drink_color)
                arcade.draw_rectangle_outline(DRINK_X, DRINK_Y + 100,
                                              bar_width, bar_height, (255, 255, 255))

        if self.state == DRINK_STATE_COMPLETE:
            arcade.draw_text(f"{self.drink_type.upper()}", DRINK_X, DRINK_Y + 80,
                             drink_color, FONT_SIZE, anchor_x="center", bold=True)
            if self.ice:
                arcade.draw_text("Со льдом", DRINK_X, DRINK_Y + 110,
                                 (200, 240, 255), 16, anchor_x="center")

    def reset(self):
        self.state = DRINK_STATE_EMPTY
        self.drink_type = None
        self.fill_time = 0
        self.fill_progress = 0
        self.filled = False
        self.fill_level = 0
        self.ice = False
        self.quality = 100

