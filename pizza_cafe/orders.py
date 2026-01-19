import json
import os
import random
import arcade
from constants import *


class Order:
    def __init__(self, level):
        self.level = level
        self.order_type = random.choice(ORDER_TYPES)
        self.requirements = {}
        self.sauce_required = True
        self.cheese_required = True
        self.dough_required = True
        self.patty_type = None
        self.drink_type = None
        self.drink_size = "medium"
        self.ice_required = False
        self.time_limit = 60
        self.reward_base = 15
        self.reward = 15
        self.penalty = 5
        self.customer_name = ""
        self.customer_mood = "neutral"
        self.special_requests = []
        self.generate_order()

    def generate_order(self):
        self.requirements = {}
        self.order_type = random.choice(ORDER_TYPES)

        if self.order_type == "pizza":
            self.generate_pizza_order()
        elif self.order_type == "burger":
            self.generate_burger_order()
        elif self.order_type == "drink":
            self.generate_drink_order()

        self.time_limit = max(30, 75 - self.level * 5)
        self.reward_base = 10 + self.level * 3
        self.reward = self.reward_base

        customers = ["Анна", "Михаил", "София", "Алексей", "Екатерина",
                     "Дмитрий", "Ольга", "Иван", "Мария", "Сергей"]
        self.customer_name = random.choice(customers)

        moods = ["neutral", "happy", "impatient", "picky", "generous"]
        weights = [0.4, 0.2, 0.2, 0.1, 0.1]
        self.customer_mood = random.choices(moods, weights=weights, k=1)[0]

        if self.customer_mood == "impatient":
            self.time_limit = int(self.time_limit * 0.7)
        elif self.customer_mood == "generous":
            self.reward = int(self.reward * 1.5)

        self.special_requests = []
        if random.random() < 0.3:
            if self.order_type == "pizza":
                requests = ["Побольше соуса", "Двойной сыр", "Хрустящая корочка",
                           "Без подгорания", "Равномерное распределение"]
            elif self.order_type == "burger":
                requests = ["Двойной сыр", "Без подгорания", "Дополнительно соуса",
                           "Хрустящая котлета"]
            else:
                requests = ["Со льдом", "Без льда", "Большой стакан", "Маленький стакан"]
            self.special_requests = random.sample(requests, random.randint(1, 2))

    def generate_pizza_order(self):
        self.sauce_required = random.random() > 0.1
        self.cheese_required = random.random() > 0.2
        self.dough_required = True

        available_ingredients = INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]

        num_ingredients = random.randint(
            min(1, self.level),
            min(3 + self.level // 2, len(available_ingredients))
        )

        selected_ingredients = random.sample(available_ingredients,
                                             min(num_ingredients, len(available_ingredients)))

        for ing in selected_ingredients:
            if ing != "cheese":
                min_count = 1
                max_count = 2 + self.level // 2
                self.requirements[ing] = random.randint(min_count, max_count)

    def generate_burger_order(self):
        self.patty_type = random.choice(["beef", "chicken"])
        available_ingredients = BURGER_INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]

        num_ingredients = random.randint(
            min(2, self.level),
            min(4 + self.level // 2, len(available_ingredients) + 1)
        )

        selected_ingredients = random.sample(available_ingredients,
                                             min(num_ingredients, len(available_ingredients)))

        for ing in selected_ingredients:
            min_count = 1
            max_count = 2 if ing in ["cheese", "bacon", "mayonnaise", "ketchup"] else 3
            self.requirements[ing] = random.randint(min_count, max_count)

    def generate_drink_order(self):
        available_drinks = DRINKS_PER_LEVEL[min(self.level - 1, 6)]
        self.drink_type = random.choice(available_drinks)
        self.drink_size = random.choice(["small", "medium", "large"])
        self.ice_required = random.random() > 0.3

    def load_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

                level_data = None
                for item in data:
                    if item.get("level") == self.level:
                        level_data = item
                        break

                if level_data and "orders" in level_data:
                    order_data = random.choice(level_data["orders"])
                    self.order_type = order_data.get("order_type", "pizza")
                    self.requirements = order_data.get("requirements", {})
                    self.sauce_required = order_data.get("sauce_required", True)
                    self.cheese_required = order_data.get("cheese_required", True)
                    self.time_limit = order_data.get("time_limit", 60)
                    self.reward = order_data.get("reward", 20)
                    self.penalty = order_data.get("penalty", 5)

                    customers = ["Анна", "Михаил", "София", "Алексей", "Екатерина"]
                    self.customer_name = random.choice(customers)
        else:
            self.generate_order()

    def check_pizza(self, pizza):
        feedback = []
        score = 0
        max_score = 100

        if pizza.burned:
            return False, "Пицца сгорела! -100%", 0

        if not pizza.cooked:
            return False, "Пицца не приготовлена!", 0

        if len(pizza.cut_lines) < 4:
            return False, "Пицца не порезана!", 0

        if self.dough_required and not pizza.has_dough:
            return False, "Нет теста!", 0

        if self.sauce_required:
            if pizza.sauce_coverage < 50:
                feedback.append("Мало соуса")
                score -= 20
            elif pizza.sauce_coverage > 90:
                feedback.append("Слишком много соуса")
                score -= 10

        if self.cheese_required:
            if pizza.cheese_coverage < 50:
                feedback.append("Мало сыра")
                score -= 20
            elif pizza.cheese_coverage > 90:
                feedback.append("Слишком много сыра")
                score -= 10

        ingredient_score = 0
        for ingredient, required_count in self.requirements.items():
            actual_count = pizza.get_ingredient_count(ingredient)

            if actual_count < required_count:
                feedback.append(f"Не хватает {ingredient}: {actual_count}/{required_count}")
                ingredient_score -= 30
            elif actual_count > required_count * 2:
                feedback.append(f"Слишком много {ingredient}")
                ingredient_score -= 15
            else:
                diff = abs(actual_count - required_count)
                if diff == 0:
                    ingredient_score += 20
                elif diff <= 2:
                    ingredient_score += 10

        distribution = pizza.get_ingredient_distribution()
        distribution_variance = sum((d - 0.33) ** 2 for d in distribution)

        if distribution_variance > 0.05:
            feedback.append("Топпинги распределены неравномерно")
            score -= 10

        quality_bonus = pizza.quality / 100

        final_score = max(0, 50 + ingredient_score + score)
        final_score *= quality_bonus

        if "Равномерное распределение" in self.special_requests:
            if distribution_variance > 0.02:
                feedback.append("Клиент просил равномерное распределение")
                final_score *= 0.7

        if "Без подгорания" in self.special_requests and pizza.quality < 80:
            feedback.append("Клиент просил без подгорания")
            final_score *= 0.8

        success = final_score >= 60

        if success:
            if final_score >= 90:
                feedback.append("ИДЕАЛЬНО! +50% к оплате")
                self.reward = int(self.reward * 1.5)
            elif final_score >= 80:
                feedback.append("Отлично! +25% к оплате")
                self.reward = int(self.reward * 1.25)
            elif final_score >= 70:
                feedback.append("Хорошо! +10% к оплате")
                self.reward = int(self.reward * 1.1)
            else:
                feedback.append("Удовлетворительно")
        else:
            feedback.append("Неудовлетворительно")

        feedback_text = ", ".join(feedback[:3])
        if not feedback_text:
            feedback_text = "В порядке" if success else "Не соответствует заказу"

        return success, feedback_text, int(final_score)

    def check_burger(self, burger):
        feedback = []
        score = 0

        if burger.burned:
            return False, "Бургер сгорел! -100%", 0

        if not burger.cooked:
            return False, "Котлета не прожарена!", 0

        if not burger.assembled:
            return False, "Бургер не собран!", 0

        if burger.patty_type != self.patty_type:
            feedback.append(f"Неправильный тип котлеты")
            score -= 30

        if not burger.has_bottom_bun or not burger.has_top_bun:
            return False, "Нет булочек!", 0

        ingredient_score = 0
        for ingredient, required_count in self.requirements.items():
            actual_count = burger.get_ingredient_count(ingredient)

            if actual_count < required_count:
                feedback.append(f"Не хватает {ingredient}: {actual_count}/{required_count}")
                ingredient_score -= 25
            elif actual_count > required_count * 2:
                feedback.append(f"Слишком много {ingredient}")
                ingredient_score -= 10
            else:
                diff = abs(actual_count - required_count)
                if diff == 0:
                    ingredient_score += 15
                elif diff == 1:
                    ingredient_score += 10

        quality_bonus = burger.quality / 100

        final_score = max(0, 50 + ingredient_score + score)
        final_score *= quality_bonus

        if "Без подгорания" in self.special_requests and burger.quality < 80:
            feedback.append("Клиент просил без подгорания")
            final_score *= 0.8

        success = final_score >= 60

        if success:
            if final_score >= 90:
                feedback.append("ИДЕАЛЬНО! +50% к оплате")
                self.reward = int(self.reward * 1.5)
            elif final_score >= 80:
                feedback.append("Отлично! +25% к оплате")
                self.reward = int(self.reward * 1.25)
            elif final_score >= 70:
                feedback.append("Хорошо! +10% к оплате")
                self.reward = int(self.reward * 1.1)

        feedback_text = ", ".join(feedback[:3]) if feedback else ("В порядке" if success else "Не соответствует заказу")
        return success, feedback_text, int(final_score)

    def check_drink(self, drink):
        feedback = []
        score = 0

        if not drink.filled:
            return False, "Напиток не наполнен!", 0

        if drink.drink_type != self.drink_type:
            return False, f"Неправильный напиток! Заказан {self.drink_type}, получен {drink.drink_type}", 0

        if self.ice_required and not drink.ice:
            feedback.append("Нет льда")
            score -= 15

        if not self.ice_required and drink.ice:
            feedback.append("Лед не нужен")
            score -= 10

        fill_level_target = {"small": 60, "medium": 80, "large": 100}.get(self.drink_size, 80)
        fill_diff = abs(drink.fill_level - fill_level_target)

        if fill_diff > 20:
            feedback.append("Неправильный размер")
            score -= 20
        elif fill_diff > 10:
            feedback.append("Размер почти правильный")
            score -= 5

        quality_bonus = drink.quality / 100

        final_score = max(0, 50 + score)
        final_score *= quality_bonus

        success = final_score >= 60

        if success:
            if final_score >= 90:
                feedback.append("ИДЕАЛЬНО! +50% к оплате")
                self.reward = int(self.reward * 1.5)
            elif final_score >= 80:
                feedback.append("Отлично! +25% к оплате")
                self.reward = int(self.reward * 1.25)
            elif final_score >= 70:
                feedback.append("Хорошо! +10% к оплате")
                self.reward = int(self.reward * 1.1)

        feedback_text = ", ".join(feedback[:3]) if feedback else ("В порядке" if success else "Не соответствует заказу")
        return success, feedback_text, int(final_score)

    def draw(self, x, y):
        arcade.draw_rectangle_filled(x, y, ORDER_DISPLAY_WIDTH, ORDER_DISPLAY_HEIGHT,
                                     (255, 250, 240, 240))
        arcade.draw_rectangle_outline(x, y, ORDER_DISPLAY_WIDTH, ORDER_DISPLAY_HEIGHT,
                                      (100, 80, 60))

        order_type_text = {"pizza": "ПИЦЦА", "burger": "БУРГЕР", "drink": "НАПИТОК"}.get(self.order_type, "ЗАКАЗ")
        arcade.draw_text(order_type_text, x, y + ORDER_DISPLAY_HEIGHT // 2 - 30,
                         (150, 80, 40), BIG_FONT_SIZE,
                         anchor_x="center", anchor_y="center", bold=True)

        arcade.draw_text(f"Клиент: {self.customer_name}",
                         x - ORDER_DISPLAY_WIDTH // 2 + 20,
                         y + ORDER_DISPLAY_HEIGHT // 2 - 70,
                         TEXT_COLOR_DARK, FONT_SIZE, anchor_x="left")

        mood_text = {
            "neutral": "Нейтральный",
            "happy": "Довольный",
            "impatient": "Нетерпеливый",
            "picky": "Придирчивый",
            "generous": "Щедрый"
        }.get(self.customer_mood, "Нейтральный")

        mood_color = {
            "neutral": (100, 100, 100),
            "happy": (0, 150, 0),
            "impatient": (255, 150, 0),
            "picky": (255, 100, 100),
            "generous": (0, 100, 200)
        }.get(self.customer_mood, (100, 100, 100))

        arcade.draw_text(f"Настроение: {mood_text}",
                         x - ORDER_DISPLAY_WIDTH // 2 + 20,
                         y + ORDER_DISPLAY_HEIGHT // 2 - 100,
                         mood_color, FONT_SIZE, anchor_x="left")

        y_offset = 140

        if self.order_type == "pizza":
            if self.dough_required:
                arcade.draw_text("✓ Тесто", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
                y_offset += 25

            if self.sauce_required:
                arcade.draw_text("✓ Соус", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
                y_offset += 25

            if self.cheese_required:
                arcade.draw_text("✓ Сыр", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
                y_offset += 25

            arcade.draw_text("Топпинги:", x - ORDER_DISPLAY_WIDTH // 2 + 20,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left", bold=True)
            y_offset += 25

            for ingredient, count in self.requirements.items():
                ing_name = ingredient.capitalize()
                arcade.draw_text(f"✓ {ing_name}: {count}",
                                 x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left")
                y_offset += 22

        elif self.order_type == "burger":
            patty_text = "Говяжья" if self.patty_type == "beef" else "Куриная"
            arcade.draw_text(f"✓ Котлета: {patty_text}", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
            y_offset += 25

            arcade.draw_text("Ингредиенты:", x - ORDER_DISPLAY_WIDTH // 2 + 20,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left", bold=True)
            y_offset += 25

            for ingredient, count in self.requirements.items():
                ing_name = ingredient.capitalize()
                arcade.draw_text(f"✓ {ing_name}: {count}",
                                 x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left")
                y_offset += 22

        elif self.order_type == "drink":
            drink_name = self.drink_type.capitalize()
            arcade.draw_text(f"✓ {drink_name}", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
            y_offset += 25

            size_text = {"small": "Маленький", "medium": "Средний", "large": "Большой"}.get(self.drink_size, "Средний")
            arcade.draw_text(f"Размер: {size_text}", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left")
            y_offset += 25

            ice_text = "Со льдом" if self.ice_required else "Без льда"
            arcade.draw_text(f"{ice_text}", x - ORDER_DISPLAY_WIDTH // 2 + 30,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left")
            y_offset += 25

        if self.special_requests:
            y_offset += 10
            arcade.draw_text("Особые пожелания:", x - ORDER_DISPLAY_WIDTH // 2 + 20,
                             y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                             (200, 100, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)
            y_offset += 25

            for request in self.special_requests:
                arcade.draw_text(f"• {request}",
                                 x - ORDER_DISPLAY_WIDTH // 2 + 30,
                                 y + ORDER_DISPLAY_HEIGHT // 2 - y_offset,
                                 (150, 80, 0), ORDER_FONT_SIZE - 2, anchor_x="left")
                y_offset += 22

        y_offset += 20
        arcade.draw_text(f"Время: {int(self.time_limit)} сек",
                         x - ORDER_DISPLAY_WIDTH // 2 + 20,
                         y - ORDER_DISPLAY_HEIGHT // 2 + 60,
                         TEXT_COLOR_DARK, ORDER_FONT_SIZE, anchor_x="left")

        arcade.draw_text(f"Оплата: ${self.reward}",
                         x - ORDER_DISPLAY_WIDTH // 2 + 20,
                         y - ORDER_DISPLAY_HEIGHT // 2 + 30,
                         (0, 150, 0), ORDER_FONT_SIZE, anchor_x="left", bold=True)

        if self.customer_mood == "impatient":
            arcade.draw_text("ТОРОПИТСЯ!", x, y - ORDER_DISPLAY_HEIGHT // 2 + 10,
                             (255, 100, 0), ORDER_FONT_SIZE,
                             anchor_x="center", bold=True)
        elif self.customer_mood == "generous":
            arcade.draw_text("ЩЕДРЫЙ ЧАЕВЫЕ!", x, y - ORDER_DISPLAY_HEIGHT // 2 + 10,
                             (0, 150, 200), ORDER_FONT_SIZE,
                             anchor_x="center", bold=True)
