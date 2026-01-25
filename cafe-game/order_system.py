import arcade
import random
from utils import load_texture, format_time


class Order:
    def __init__(self, game, customer_type):
        self.game = game
        self.customer_type = customer_type
        self.items = self.generate_order()
        self.start_time = arcade.get_fps()
        self.max_time = self.calculate_max_time()
        self.completed = False
        self.success = False
        self.x = random.randint(900, 1100)
        self.y = random.randint(400, 600)
        self.ticket_texture = load_texture("images/order_ticket.png")

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
        ingredients = ["patty", "cheese", "lettuce", "tomato", "sauce"]
        burger = ["base"]
        for ingredient in ingredients:
            if random.random() > 0.5 or len(burger) == 1:
                burger.append(ingredient)
        burger.append("top")
        return burger

    def generate_drink(self):
        drinks = ["cola", "sprite", "water"]
        return random.choice(drinks)

    def generate_icecream(self):
        flavors = ["vanilla", "chocolate", "strawberry"]
        return random.choice(flavors)

    def calculate_max_time(self):
        base_time = 30
        if any(isinstance(item, list) for item in self.items):
            base_time += 15
        if "fries" in self.items:
            base_time += 10
        if "icecream" in self.items or any("icecream" in str(item) for item in self.items):
            base_time += 5
        return base_time * (1.5 - self.game.current_level * 0.1)

    def update(self, delta_time):
        if self.completed:
            return

        elapsed = (arcade.get_fps() - self.start_time) / 60
        if elapsed > self.max_time:
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
            elif item in ["cola", "sprite", "water"]:
                if not prepared_items.get("drink") or prepared_items["drink"] != item:
                    penalty += 15
                else:
                    score += 25
            elif item in ["vanilla", "chocolate", "strawberry"]:
                if not prepared_items.get("icecream") or prepared_items["icecream"] != item:
                    penalty += 15
                else:
                    score += 25

        self.success = score > penalty
        if self.success:
            reward = max(40, score - penalty)
            self.game.money += reward
            self.game.score += reward
            self.game.customer_manager.add_happy_effect(self.x, self.y)
        else:
            self.game.money -= penalty // 2
            self.game.customer_manager.add_angry_effect(self.x, self.y)

        return self.success

    def validate_burger(self, required, prepared):
        if len(required) != len(prepared):
            return False
        for i in range(len(required)):
            if required[i] != prepared[i]:
                return False
        return True

    def draw(self):
        arcade.draw_texture_rectangle(
            self.x, self.y,
            300, 150,
            self.ticket_texture
        )

        y_offset = self.y + 40
        arcade.draw_text(
            f"LEVEL {self.game.current_level}",
            self.x - 120, y_offset,
            arcade.color.RED, 18
        )

        elapsed = (arcade.get_fps() - self.start_time) / 60
        time_left = max(0, self.max_time - elapsed)
        arcade.draw_text(
            f"TIME: {format_time(time_left)}",
            self.x + 20, y_offset,
            arcade.color.BLUE, 18,
            anchor_x="right"
        )

        y_offset -= 30
        arcade.draw_text(
            "ORDER:",
            self.x - 120, y_offset,
            arcade.color.BLACK, 20
        )

        for item in self.items:
            y_offset -= 25
            if isinstance(item, list):
                arcade.draw_text(
                    "Custom Burger",
                    self.x - 100, y_offset,
                    arcade.color.DARK_BROWN, 18
                )
            else:
                arcade.draw_text(
                    item.capitalize(),
                    self.x - 100, y_offset,
                    arcade.color.BLACK, 18
                )


class OrderSystem:
    def __init__(self, game):
        self.game = game
        self.active_orders = []
        self.order_cooldown = 0
        self.max_orders = 3

    def reset_orders(self):
        self.active_orders = []
        self.order_cooldown = 0

    def update(self, delta_time):
        self.order_cooldown -= delta_time
        if self.order_cooldown <= 0 and len(self.active_orders) < self.max_orders:
            self.spawn_order()
            self.order_cooldown = max(8 - self.game.current_level, 2)

        for order in self.active_orders[:]:
            order.update(delta_time)
            if order.completed:
                self.active_orders.remove(order)

    def spawn_order(self):
        customer_types = ["casual", "business", "family", "teen"]
        customer_type = random.choice(customer_types)
        self.active_orders.append(Order(self.game, customer_type))

    def submit_order(self, prepared_items):
        if not self.active_orders:
            return False

        success = self.active_orders[0].complete_order(prepared_items)
        arcade.play_sound(arcade.load_sound("sounds/success_sound.wav" if success else "sounds/fail_sound.wav"))
        self.active_orders.pop(0)
        return success

    def draw_orders(self):
        for order in self.active_orders:
            order.draw()

    def get_current_order(self):
        return self.active_orders[0] if self.active_orders else None