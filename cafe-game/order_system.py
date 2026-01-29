import arcade
import random
from utils import format_time


class Order:
    def __init__(self, game, customer_type):
        self.game = game
        self.customer_type = customer_type
        self.items = self.generate_order()
        self.elapsed_time = 0.0
        self.max_time = self.calculate_max_time()
        self.completed = False
        self.success = False
        # Позиция карточки заказа: правый верхний угол экрана
        card_width, card_height = 280, 130
        margin_right, margin_top = 24, 90
        self.x = game.width - margin_right - card_width // 2
        self.y = game.height - margin_top - card_height // 2

    def generate_order(self):
        items = []
        if random.random() > 0.3:
            items.append(self.generate_burger())
        if random.random() > 0.5:
            items.append("fries")
        if random.random() > 0.4:
            items.append(self.generate_drink())
        if random.random() > 0.7 and self.game.current_level > 3:
            items.append(self.generate_icecream())
        return items

    def generate_burger(self):
        ingredients = ["patty", "cheese"]
        burger = ["base"]
        for ingredient in ingredients:
            if random.random() > 0.5 or len(burger) == 1:
                burger.append(ingredient)
        burger.append("top")
        return burger

    def generate_drink(self):
        drinks = ["cola", "water"]
        return random.choice(drinks)

    def generate_icecream(self):
        flavors = ["default", "chocolate"]
        return random.choice(flavors)

    def calculate_max_time(self):
        base_time = 30
        if any(isinstance(item, list) for item in self.items):
            base_time += 15
        if "fries" in self.items:
            base_time += 10
        if any(item in ["default", "chocolate"] for item in self.items):
            base_time += 5
        return base_time * (1.5 - self.game.current_level * 0.1)

    def update(self, delta_time):
        if self.completed:
            return

        self.elapsed_time += delta_time
        if self.elapsed_time > self.max_time:
            self.success = False
            self.completed = True
            self.game.money -= 15
            self.game.customer_manager.remove_angry_customers()

    def complete_order(self, prepared_items):
        if self.completed:
            return False

        self.completed = True
        score = 0
        penalty = 0

        for item in self.items:
            if isinstance(item, list):  # Burger
                if not prepared_items.get("burger") or not self.validate_burger(item, prepared_items["burger"]):
                    penalty += 30
                else:
                    score += 50
            elif item == "fries":
                if not prepared_items.get("fries"):
                    penalty += 20
                else:
                    score += 30
            elif item in ["cola", "water"]:
                if not prepared_items.get("drink") or prepared_items["drink"] != item:
                    penalty += 15
                else:
                    score += 25
            elif item in ["default", "chocolate"]:
                if not prepared_items.get("icecream") or prepared_items["icecream"] != item:
                    penalty += 15
                else:
                    score += 25

        self.success = score > penalty
        if self.success:
            # Гарантированная награда за выполненный заказ: база + за пункты
            reward = 50 + max(0, score - penalty)
            self.game.money += reward
            self.game.score += reward
        else:
            self.game.money -= penalty // 2
            self.game.customer_manager.remove_angry_customers()

        return self.success

    def validate_burger(self, required, prepared):
        if len(required) != len(prepared):
            return False
        for i in range(len(required)):
            if required[i] != prepared[i]:
                return False
        return True

    @staticmethod
    def _item_label_ru(item):
        """Русское название пункта заказа."""
        if item == "fries":
            return "Картошка"
        if item == "cola":
            return "Кола"
        if item == "water":
            return "Вода"
        if item == "default":
            return "Мороженое ваниль"
        if item == "chocolate":
            return "Мороженое шоколад"
        return item.capitalize()

    @staticmethod
    def format_burger_layers(burger_list):
        """Форматирует список слоёв бургера для отображения (base, patty, cheese, top -> читаемый текст)."""
        if not burger_list or not isinstance(burger_list, list):
            return "Custom Burger"
        names = []
        for layer in burger_list:
            if layer == "base":
                names.append("низ булки")
            elif layer == "top":
                names.append("верх булки")
            elif layer == "patty":
                names.append("котлета")
            elif layer == "cheese":
                names.append("сыр")
            else:
                names.append(layer)
        return "Бургер: " + ", ".join(names)

    def draw(self):
        rect = arcade.types.XYWH(self.x, self.y, 280, 130)
        arcade.draw_rect_filled(rect, arcade.color.LIGHT_BROWN)
        arcade.draw_rect_outline(rect, arcade.color.DARK_BROWN)

        y_offset = self.y + 40
        arcade.draw_text(
            f"УРОВЕНЬ {self.game.current_level}",
            self.x - 130, y_offset,
            arcade.color.RED, 18
        )

        time_left = max(0, self.max_time - self.elapsed_time)
        arcade.draw_text(
            f"ВРЕМЯ: {format_time(time_left)}",
            self.x + 20, y_offset,
            arcade.color.BLUE, 18,
            anchor_x="right"
        )

        y_offset -= 30
        arcade.draw_text(
            "ЗАКАЗ:",
            self.x - 130, y_offset,
            arcade.color.BLACK, 20
        )

        for item in self.items:
            y_offset -= 25
            if isinstance(item, list):
                arcade.draw_text(
                    Order.format_burger_layers(item),
                    self.x - 110, y_offset,
                    arcade.color.DARK_BROWN, 16
                )
            else:
                label = self._item_label_ru(item)
                arcade.draw_text(
                    label,
                    self.x - 110, y_offset,
                    arcade.color.BLACK, 18
                )


class OrderSystem:
    def __init__(self, game):
        self.game = game
        self.active_orders = []
        self.order_cooldown = 0
        # Only one active order at a time for strict queue behavior
        self.max_orders = 1

    def reset_orders(self):
        self.active_orders = []
        self.order_cooldown = 0

    def update(self, delta_time):
        self.order_cooldown -= delta_time
        # Spawn new order only when there are no active orders and no customers,
        # so clients and orders arrive strictly one by one.
        if (
            self.order_cooldown <= 0
            and len(self.active_orders) < self.max_orders
            and not self.game.customer_manager.customers
        ):
            self.spawn_order()
            self.game.customer_manager.spawn_customer()
            self.order_cooldown = max(8 - self.game.current_level, 2)

        for order in self.active_orders[:]:
            order.update(delta_time)
            if order.completed:
                self.active_orders.remove(order)

    def spawn_order(self):
        customer_types = ["standard"]
        customer_type = random.choice(customer_types)
        self.active_orders.append(Order(self.game, customer_type))

    def submit_order(self, prepared_items):
        if not self.active_orders:
            return False

        success = self.active_orders[0].complete_order(prepared_items)
        if success:
            arcade.play_sound(arcade.load_sound("sounds/success.wav"))
        else:
            arcade.play_sound(arcade.load_sound("sounds/fail.wav"))
        self.active_orders.pop(0)
        return success

    def draw_orders(self):
        for order in self.active_orders:
            order.draw()

    def get_current_order(self):
        return self.active_orders[0] if self.active_orders else None