import math

import arcade

from constants import *


class Pizza:
    def __init__(self):
        self.ingredients = []
        self.state = STATE_DOUGH
        self.cook_time = 0
        self.cooked = False
        self.burned = False
        self.slices = 8
        self.cut_lines = []
        self.sauce_coverage = 0
        self.cheese_coverage = 0
        self.ingredient_distribution = []
        self.cooking_progress = 0
        self.quality = 100
        self.has_dough = False
        self.has_sauce = False
        self.has_cheese = False

    def add_dough(self):
        if self.state == STATE_DOUGH:
            self.has_dough = True
            self.state = STATE_SAUCE
            return True
        return False

    def add_sauce(self, amount=25):
        if self.state == STATE_SAUCE and self.has_dough:
            self.sauce_coverage = min(100, self.sauce_coverage + amount)
            if self.sauce_coverage >= 70:
                self.has_sauce = True
                self.state = STATE_CHEESE
            return True
        return False

    def add_cheese(self, amount=25):
        if self.state == STATE_CHEESE and self.has_sauce:
            self.cheese_coverage = min(100, self.cheese_coverage + amount)
            if self.cheese_coverage >= 70:
                self.has_cheese = True
                self.state = STATE_TOPPINGS
            return True
        return False

    def add_ingredient(self, ingredient_name, x, y):
        if self.state == STATE_TOPPINGS and self.has_cheese:
            distance = math.sqrt(x ** 2 + y ** 2)
            if distance <= PIZZA_RADIUS:
                self.ingredients.append({
                    "name": ingredient_name,
                    "x": x,
                    "y": y
                })

                distribution_zone = int(distance / (PIZZA_RADIUS / 3))
                self.ingredient_distribution.append(distribution_zone)
                return True
        return False

    def start_cooking(self):
        if self.state == STATE_TOPPINGS and len(self.ingredients) > 0:
            self.state = STATE_COOKING
            self.cook_time = 0
            self.cooking_progress = 0
            return True
        return False

    def update_cooking(self, delta_time):
        if self.state == STATE_COOKING:
            self.cook_time += delta_time
            self.cooking_progress = (self.cook_time / COOK_TIME_MAX) * 100

            if COOK_TIME_MIN <= self.cook_time <= COOK_TIME_MAX:
                self.cooked = True
                self.burned = False
                self.quality = 100 - abs(self.cook_time - 11.5) * 8
            elif self.cook_time > COOK_TIME_MAX:
                if self.cook_time > BURN_TIME:
                    self.burned = True
                    self.cooked = False
                    self.quality = 0
                else:
                    self.quality = max(0, 100 - (self.cook_time - COOK_TIME_MAX) * 20)

    def start_cutting(self):
        if self.state == STATE_COOKING and self.cooked:
            self.state = STATE_CUTTING
            return True
        return False

    def add_cut(self, x1, y1, x2, y2):
        if self.state == STATE_CUTTING:
            self.cut_lines.append((x1, y1, x2, y2))
            if len(self.cut_lines) >= 4:
                self.state = STATE_COMPLETE

                cut_quality = self.check_cut_quality()
                self.quality *= cut_quality
            return True
        return False

    def check_cut_quality(self):
        if len(self.cut_lines) < 4:
            return 0.5

        angles = []
        for x1, y1, x2, y2 in self.cut_lines:
            angle = math.atan2(y2 - y1, x2 - x1)
            angles.append(angle)

        angle_variance = 0
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                diff = abs(angles[i] - angles[j]) % (math.pi / 2)
                angle_variance += min(diff, math.pi / 2 - diff)

        avg_variance = angle_variance / 6
        return max(0.5, 1.0 - avg_variance * 2)

    def draw(self):
        arcade.draw_circle_filled(PIZZA_X, PIZZA_Y, PIZZA_RADIUS + 10, (160, 120, 80))
        arcade.draw_circle_filled(PIZZA_X, PIZZA_Y, PIZZA_RADIUS, PIZZA_CRUST_COLOR)

        if self.sauce_coverage > 0:
            sauce_radius = PIZZA_RADIUS * (self.sauce_coverage / 100) * 0.95
            arcade.draw_circle_filled(PIZZA_X, PIZZA_Y, sauce_radius, PIZZA_SAUCE_COLOR)

        if self.cheese_coverage > 0:
            cheese_radius = PIZZA_RADIUS * (self.cheese_coverage / 100) * 0.9
            arcade.draw_circle_filled(PIZZA_X, PIZZA_Y, cheese_radius, CHEESE_COLOR)

        for ingredient in self.ingredients:
            ing_x = PIZZA_X + ingredient["x"]
            ing_y = PIZZA_Y + ingredient["y"]
            color = INGREDIENT_COLORS.get(ingredient["name"], (255, 255, 255))
            arcade.draw_circle_filled(ing_x, ing_y, INGREDIENT_SIZE // 2, color)

        if self.state == STATE_COOKING:
            if self.cooked and not self.burned:
                arcade.draw_text("ГОТОВО!", PIZZA_X, PIZZA_Y + PIZZA_RADIUS + 30,
                                 (0, 200, 0), 22, anchor_x="center", bold=True)
                arcade.draw_text(f"Качество: {int(self.quality)}%", PIZZA_X, PIZZA_Y + PIZZA_RADIUS + 55,
                                 (100, 255, 100), 18, anchor_x="center")
            elif self.burned:
                arcade.draw_text("СГОРЕЛО!", PIZZA_X, PIZZA_Y + PIZZA_RADIUS + 30,
                                 (255, 50, 50), 22, anchor_x="center", bold=True)
            else:
                progress = min(100, int((self.cook_time / COOK_TIME_MAX) * 100))
                arcade.draw_text(f"Приготовление: {progress}%",
                                 PIZZA_X, PIZZA_Y + PIZZA_RADIUS + 30,
                                 (255, 255, 200), 18, anchor_x="center")

                bar_width = 200
                bar_height = 15
                fill_width = (self.cooking_progress / 100) * bar_width

                arcade.draw_rectangle_filled(PIZZA_X - bar_width / 2 + fill_width / 2,
                                             PIZZA_Y + PIZZA_RADIUS + 50,
                                             fill_width, bar_height,
                                             (255, int(255 - self.cooking_progress * 2.55), 0))
                arcade.draw_rectangle_outline(PIZZA_X, PIZZA_Y + PIZZA_RADIUS + 50,
                                              bar_width, bar_height, (255, 255, 255))

        for line in self.cut_lines:
            x1, y1, x2, y2 = line
            arcade.draw_line(PIZZA_X + x1, PIZZA_Y + y1,
                             PIZZA_X + x2, PIZZA_Y + y2,
                             (0, 0, 0), 4)

        if self.state == STATE_DOUGH and not self.has_dough:
            arcade.draw_text("Добавьте тесто!", PIZZA_X, PIZZA_Y,
                             (255, 255, 255), 24, anchor_x="center")
        elif self.state == STATE_SAUCE and not self.has_sauce:
            arcade.draw_text("Добавьте соус!", PIZZA_X, PIZZA_Y,
                             (255, 255, 255), 24, anchor_x="center")
        elif self.state == STATE_CHEESE and not self.has_cheese:
            arcade.draw_text("Добавьте сыр!", PIZZA_X, PIZZA_Y,
                             (255, 255, 255), 24, anchor_x="center")
        elif self.state == STATE_TOPPINGS and len(self.ingredients) == 0:
            arcade.draw_text("Добавьте топпинги!", PIZZA_X, PIZZA_Y,
                             (255, 255, 255), 24, anchor_x="center")

    def get_ingredient_count(self, ingredient_name):
        count = 0
        for ing in self.ingredients:
            if ing["name"] == ingredient_name:
                count += 1
        return count

    def get_ingredient_distribution(self):
        if not self.ingredient_distribution:
            return [0, 0, 0]

        zones = [0, 0, 0]
        for zone in self.ingredient_distribution:
            if 0 <= zone < 3:
                zones[zone] += 1

        total = sum(zones)
        if total > 0:
            zones = [z / total for z in zones]

        return zones

    def reset(self):
        self.ingredients = []
        self.state = STATE_DOUGH
        self.cook_time = 0
        self.cooked = False
        self.burned = False
        self.cut_lines = []
        self.sauce_coverage = 0
        self.cheese_coverage = 0
        self.ingredient_distribution = []
        self.cooking_progress = 0
        self.quality = 100
        self.has_dough = False
        self.has_sauce = False
        self.has_cheese = False