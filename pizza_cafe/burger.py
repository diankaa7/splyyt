import arcade
from constants import *


class Burger:
    def __init__(self):
        self.state = BURGER_STATE_BUN
        self.has_bottom_bun = False
        self.has_top_bun = False
        self.has_patty = False
        self.patty_type = None
        self.cook_time = 0
        self.cooked = False
        self.burned = False
        self.ingredients = []
        self.quality = 100
        self.cooking_progress = 0
        self.assembled = False

    def add_bottom_bun(self):
        if self.state == BURGER_STATE_BUN:
            self.has_bottom_bun = True
            if self.has_top_bun:
                self.state = BURGER_STATE_PATTY
            return True
        return False

    def add_top_bun(self):
        if self.state == BURGER_STATE_BUN:
            self.has_top_bun = True
            if self.has_bottom_bun:
                self.state = BURGER_STATE_PATTY
            return True
        return False

    def add_patty(self, patty_type="beef"):
        if self.state == BURGER_STATE_PATTY and self.has_bottom_bun:
            self.has_patty = True
            self.patty_type = patty_type
            self.state = BURGER_STATE_COOKING
            return True
        return False

    def start_cooking(self):
        if self.state == BURGER_STATE_COOKING and self.has_patty:
            self.cook_time = 0
            self.cooking_progress = 0
            return True
        return False

    def update_cooking(self, delta_time):
        if self.state == BURGER_STATE_COOKING:
            self.cook_time += delta_time
            self.cooking_progress = (self.cook_time / GRILL_TIME_MAX) * 100

            if GRILL_TIME_MIN <= self.cook_time <= GRILL_TIME_MAX:
                self.cooked = True
                self.burned = False
                self.quality = 100 - abs(self.cook_time - 9) * 10
            elif self.cook_time > GRILL_TIME_MAX:
                if self.cook_time > GRILL_BURN_TIME:
                    self.burned = True
                    self.cooked = False
                    self.quality = 0
                else:
                    self.quality = max(0, 100 - (self.cook_time - GRILL_TIME_MAX) * 25)

    def finish_cooking(self):
        if self.state == BURGER_STATE_COOKING and self.cooked:
            self.state = BURGER_STATE_TOPPINGS
            return True
        return False

    def add_ingredient(self, ingredient_name):
        if self.state == BURGER_STATE_TOPPINGS and self.cooked:
            self.ingredients.append(ingredient_name)
            return True
        return False

    def start_assembling(self):
        if self.state == BURGER_STATE_TOPPINGS and self.cooked:
            self.state = BURGER_STATE_ASSEMBLING
            return True
        return False

    def finish_assembling(self):
        if self.state == BURGER_STATE_ASSEMBLING:
            self.assembled = True
            self.state = BURGER_STATE_COMPLETE
            return True
        return False

    def get_ingredient_count(self, ingredient_name):
        count = 0
        for ing in self.ingredients:
            if ing == ingredient_name:
                count += 1
        return count

    def draw(self):
        if self.state == BURGER_STATE_BUN:
            arcade.draw_text("Добавьте булочки!", BURGER_X, BURGER_Y,
                             TEXT_COLOR, FONT_SIZE + 4, anchor_x="center")
            return

        bun_color = (222, 184, 135)
        patty_color = (139, 69, 19) if self.patty_type == "beef" else (255, 200, 150)

        if self.has_bottom_bun:
            arcade.draw_rectangle_filled(BURGER_X, BURGER_Y - 60, BURGER_WIDTH, 15, bun_color)

        if self.has_patty:
            if self.state == BURGER_STATE_COOKING:
                if self.cooked and not self.burned:
                    cooked_color = (101, 67, 33)
                elif self.burned:
                    cooked_color = (50, 25, 0)
                else:
                    cooked_color = patty_color
            else:
                cooked_color = (101, 67, 33) if self.cooked else patty_color

            arcade.draw_rectangle_filled(BURGER_X, BURGER_Y - 20, BURGER_WIDTH - 20, 20, cooked_color)

        y_offset = -20
        for ing in self.ingredients:
            y_offset += 12
            color = INGREDIENT_COLORS.get(ing, (255, 255, 255))
            if ing == "lettuce":
                arcade.draw_rectangle_filled(BURGER_X, BURGER_Y + y_offset, BURGER_WIDTH - 10, 8, color)
            elif ing == "tomato":
                arcade.draw_ellipse_filled(BURGER_X, BURGER_Y + y_offset, BURGER_WIDTH - 20, 10, color)
            elif ing == "cheese":
                arcade.draw_rectangle_filled(BURGER_X, BURGER_Y + y_offset, BURGER_WIDTH - 10, 8, color)
            elif ing == "onions":
                arcade.draw_circle_filled(BURGER_X - 40, BURGER_Y + y_offset, 5, color)
                arcade.draw_circle_filled(BURGER_X + 40, BURGER_Y + y_offset, 5, color)
            elif ing == "pickles":
                for i in range(3):
                    arcade.draw_ellipse_filled(BURGER_X - 30 + i * 30, BURGER_Y + y_offset, 15, 8, color)
            elif ing == "bacon":
                arcade.draw_rectangle_filled(BURGER_X, BURGER_Y + y_offset, BURGER_WIDTH - 15, 6, color)
            else:
                arcade.draw_rectangle_filled(BURGER_X, BURGER_Y + y_offset, BURGER_WIDTH - 15, 10, color)

        if self.has_top_bun and self.state != BURGER_STATE_BUN:
            top_y = BURGER_Y + y_offset + 20 if self.ingredients else BURGER_Y + 10
            arcade.draw_ellipse_filled(BURGER_X, top_y, BURGER_WIDTH, 20, bun_color)

        if self.state == BURGER_STATE_COOKING:
            if self.cooked and not self.burned:
                arcade.draw_text("ГОТОВО!", BURGER_X, BURGER_Y + 80,
                                 (0, 200, 0), 22, anchor_x="center", bold=True)
                arcade.draw_text(f"Качество: {int(self.quality)}%", BURGER_X, BURGER_Y + 110,
                                 (100, 255, 100), 18, anchor_x="center")
            elif self.burned:
                arcade.draw_text("СГОРЕЛО!", BURGER_X, BURGER_Y + 80,
                                 (255, 50, 50), 22, anchor_x="center", bold=True)
            else:
                progress = min(100, int((self.cook_time / GRILL_TIME_MAX) * 100))
                arcade.draw_text(f"Жарка: {progress}%", BURGER_X, BURGER_Y + 80,
                                 (255, 255, 200), 18, anchor_x="center")
                bar_width = 200
                bar_height = 15
                fill_width = (self.cooking_progress / 100) * bar_width
                arcade.draw_rectangle_filled(BURGER_X - bar_width / 2 + fill_width / 2,
                                             BURGER_Y + 100, fill_width, bar_height,
                                             (255, int(255 - self.cooking_progress * 2.55), 0))
                arcade.draw_rectangle_outline(BURGER_X, BURGER_Y + 100,
                                              bar_width, bar_height, (255, 255, 255))

        if self.state == BURGER_STATE_PATTY and not self.has_patty:
            arcade.draw_text("Добавьте котлету!", BURGER_X, BURGER_Y,
                             TEXT_COLOR, FONT_SIZE + 4, anchor_x="center")

        if self.state == BURGER_STATE_TOPPINGS:
            arcade.draw_text("Добавьте ингредиенты!", BURGER_X, BURGER_Y - 100,
                             TEXT_COLOR, FONT_SIZE, anchor_x="center")

        if self.state == BURGER_STATE_ASSEMBLING:
            arcade.draw_text("Соберите бургер!", BURGER_X, BURGER_Y - 100,
                             TEXT_COLOR, FONT_SIZE, anchor_x="center")

    def reset(self):
        self.state = BURGER_STATE_BUN
        self.has_bottom_bun = False
        self.has_top_bun = False
        self.has_patty = False
        self.patty_type = None
        self.cook_time = 0
        self.cooked = False
        self.burned = False
        self.ingredients = []
        self.quality = 100
        self.cooking_progress = 0
        self.assembled = False

