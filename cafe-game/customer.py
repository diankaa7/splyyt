import arcade
import random
from utils import load_texture


class Customer:
    def __init__(self, game, customer_type):
        self.game = game
        self.customer_type = customer_type
        self.textures = self.load_textures()
        self.current_texture = self.textures["idle"]
        self.center_x = -100
        self.center_y = 350
        self.target_x = random.randint(100, 300)
        self.speed = 0.5 + random.random() * 0.5
        self.state = "entering"
        self.wait_time = 0
        self.max_wait = self.calculate_max_wait()
        self.order_submitted = False
        self.sprite = arcade.Sprite()
        self.sprite.texture = self.current_texture
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def load_textures(self):
        return {
            "idle": load_texture(f"images/{self.customer_type}_idle.png"),
            "happy": load_texture(f"images/{self.customer_type}_happy.png"),
            "angry": load_texture(f"images/{self.customer_type}_angry.png")
        }

    def calculate_max_wait(self):
        base_wait = 45
        if self.customer_type == "business":
            return base_wait * 0.7
        elif self.customer_type == "family":
            return base_wait * 1.3
        elif self.customer_type == "teen":
            return base_wait * 1.5
        return base_wait

    def update(self, delta_time):
        if self.state == "entering":
            self.center_x += self.speed
            if self.center_x >= self.target_x:
                self.center_x = self.target_x
                self.state = "waiting"
                self.wait_time = 0

        elif self.state == "waiting":
            self.wait_time += delta_time
            if self.wait_time > self.max_wait:
                self.state = "leaving_angry"
                self.center_x = self.target_x

        elif self.state == "leaving_happy" or self.state == "leaving_angry":
            self.center_x -= self.speed * 1.5
            if self.center_x < -100:
                self.game.customer_manager.customers.remove(self)

        elif self.state == "completed":
            self.state = "leaving_happy"

        self.update_texture()
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update_texture(self):
        if self.state == "waiting":
            if "order_system" in dir(self.game) and self.game.order_system.get_current_order():
                current_order = self.game.order_system.get_current_order()
                elapsed = (arcade.get_fps() - current_order.start_time) / 60
                if elapsed > current_order.max_time * 0.7:
                    self.current_texture = self.textures["angry"]
                else:
                    self.current_texture = self.textures["idle"]
        elif self.state == "leaving_angry":
            self.current_texture = self.textures["angry"]
        else:
            self.current_texture = self.textures["idle"]

        self.sprite.texture = self.current_texture

    def draw(self):
        self.sprite.draw()

    def on_order_complete(self, success):
        self.order_submitted = True
        if success:
            self.state = "completed"
            self.current_texture = self.textures["happy"]
        else:
            self.state = "leaving_angry"


class CustomerManager:
    def __init__(self, game):
        self.game = game
        self.customers = []
        self.spawn_timer = 0
        self.customer_types = ["casual", "business", "family", "teen"]
        self.effects = []

    def setup_customers(self):
        self.customers = []
        self.spawn_timer = 0
        self.effects = []

    def update(self, delta_time):
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0 and len(self.customers) < 3:
            self.spawn_customer()
            self.spawn_timer = max(10 - self.game.current_level * 0.5, 3)

        for customer in self.customers[:]:
            customer.update(delta_time)

        for effect in self.effects[:]:
            effect["time"] -= delta_time
            if effect["time"] <= 0:
                self.effects.remove(effect)

    def spawn_customer(self):
        customer_type = random.choice(self.customer_types)
        customer = Customer(self.game, customer_type)
        self.customers.append(customer)
        arcade.play_sound(arcade.load_sound("sounds/order_sound.wav"))

    def draw(self):
        for customer in self.customers:
            customer.draw()

        for effect in self.effects:
            arcade.draw_texture_rectangle(
                effect["x"], effect["y"],
                80, 80,
                effect["texture"],
                alpha=effect["time"] * 50
            )

    def check_customer_click(self, x, y):
        for customer in self.customers:
            if (abs(x - customer.center_x) < 50 and
                    abs(y - customer.center_y) < 100 and
                    customer.state == "waiting" and
                    not customer.order_submitted):
                self.game.order_system.submit_order(self.game.food_manager.get_prepared_items())
                customer.on_order_complete(True)
                return

    def add_happy_effect(self, x, y):
        self.effects.append({
            "x": x,
            "y": y,
            "texture": load_texture("images/sparkle_effect.png"),
            "time": 1.0
        })

    def add_angry_effect(self, x, y):
        self.effects.append({
            "x": x,
            "y": y,
            "texture": load_texture("images/smoke_effect.png"),
            "time": 1.5
        })

    def remove_angry_customers(self):
        for customer in self.customers[:]:
            if customer.state == "waiting" and not customer.order_submitted:
                customer.state = "leaving_angry"