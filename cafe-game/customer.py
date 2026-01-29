import arcade
import random
import os
from utils import get_texture_display_size


class Customer:
    # Опциональные текстуры по настроению (любое разрешение масштабируется под body_size)
    TEXTURE_PATHS = {
        "idle": "images/customer_idle.png",
        "happy": "images/customer_happy.png",
        "angry": "images/customer_angry.png",
    }

    def __init__(self, game, customer_type, textures=None):
        self.game = game
        self.customer_type = customer_type
        self.center_x = -100
        self.center_y = 350
        self.target_x = random.randint(100, 300)
        self.speed = 0.5 + random.random() * 0.5
        self.state = "entering"
        self.wait_time = 0
        self.max_wait = self.calculate_max_wait()
        self.order_submitted = False

        # textures: dict mood -> texture (если None, рисуем фигурами)
        self._textures = textures or {}
        self.body_width = 70
        self.body_height = 90
        self.head_radius = 18
        self.mood = "idle"  # idle | happy | angry

        self._skin_color = arcade.color.BISQUE
        self._outline = arcade.color.BLACK

        palettes = [
            (arcade.color.LIGHT_BLUE, arcade.color.BLUE),
            (arcade.color.LIGHT_GREEN, arcade.color.DARK_GREEN),
            (arcade.color.SALMON_PINK, arcade.color.DARK_RED),
            (arcade.color.BEIGE, arcade.color.BROWN),
        ]
        self._body_color, self._accent_color = random.choice(palettes)

    def calculate_max_wait(self):
        base_wait = 45
        return base_wait

    def update(self, delta_time):
        if self.state == "entering":
            self.center_x += self.speed
            if self.center_x >= self.target_x:
                self.center_x = self.target_x
                self.state = "waiting"
                self.wait_time = 0

        elif self.state == "leaving_happy" or self.state == "leaving_angry":
            self.center_x -= self.speed * 1.5
            if self.center_x < -100:
                self.game.customer_manager.customers.remove(self)

        elif self.state == "completed":
            self.state = "leaving_happy"

        self.update_mood()

    def update_mood(self):
        if self.state in ("leaving_angry",):
            self.mood = "angry"
            return

        if self.state in ("leaving_happy",):
            self.mood = "happy"
            return

        self.mood = "idle"

    def draw(self):
        x = self.center_x
        y = self.center_y

        tex = self._textures.get(self.mood)
        if tex is not None:
            dw, dh = get_texture_display_size(
                tex, self.body_width, self.body_height, fit_inside=True
            )
            rect = arcade.types.XYWH(x, y, dw, dh)
            arcade.draw_texture_rect(tex, rect)
            # Индикатор настроения поверх картинки
            head_y = y + self.body_height / 2 + 8
            indicator_y = head_y + 12
            if self.mood == "happy":
                arcade.draw_text("❤", x, indicator_y, arcade.color.PINK, 14, anchor_x="center")
            elif self.mood == "angry":
                arcade.draw_text("!", x, indicator_y, arcade.color.RED, 18, anchor_x="center")
            return

        # Рисуем фигурами, если текстур нет
        arcade.draw_ellipse_filled(x, y - self.body_height / 2 - 8, self.body_width * 0.9, 12, (0, 0, 0, 80))

        leg_h = 28
        leg_w = 10
        leg_y = y - self.body_height / 2 - leg_h / 2 + 4
        leg_left = arcade.types.XYWH(x - 12, leg_y, leg_w, leg_h)
        leg_right = arcade.types.XYWH(x + 12, leg_y, leg_w, leg_h)
        arcade.draw_rect_filled(leg_left, arcade.color.DARK_GRAY)
        arcade.draw_rect_filled(leg_right, arcade.color.DARK_GRAY)

        body_rect = arcade.types.XYWH(x, y, self.body_width, self.body_height)
        arcade.draw_rect_filled(body_rect, self._body_color)
        arcade.draw_rect_outline(body_rect, self._outline)

        stripe_h = 10
        stripe_rect = arcade.types.XYWH(x, y + 8, self.body_width * 0.9, stripe_h)
        arcade.draw_rect_filled(stripe_rect, self._accent_color)

        head_y = y + self.body_height / 2 + self.head_radius - 6
        arcade.draw_circle_filled(x, head_y, self.head_radius, self._skin_color)
        arcade.draw_circle_outline(x, head_y, self.head_radius, self._outline, 2)

        arm_y = y + self.body_height / 4
        arcade.draw_line(x - self.body_width / 2, arm_y, x - self.body_width / 2 - 10, arm_y - 8,
                         self._outline, 3)
        arcade.draw_line(x + self.body_width / 2, arm_y, x + self.body_width / 2 + 10, arm_y - 8,
                         self._outline, 3)

        eye_dx = 6
        eye_y = head_y + 4
        arcade.draw_circle_filled(x - eye_dx, eye_y, 2.2, self._outline)
        arcade.draw_circle_filled(x + eye_dx, eye_y, 2.2, self._outline)

        if self.mood == "happy":
            arcade.draw_arc_outline(x, head_y - 5, 16, 10, self._outline, 200, 340, 2)
        elif self.mood == "angry":
            arcade.draw_arc_outline(x, head_y - 3, 16, 10, self._outline, 20, 160, 2)
            arcade.draw_line(x - 10, head_y + 8, x - 2, head_y + 6, self._outline, 2)
            arcade.draw_line(x + 10, head_y + 8, x + 2, head_y + 6, self._outline, 2)
        else:
            arcade.draw_line(x - 6, head_y - 6, x + 6, head_y - 6, self._outline, 2)

        indicator_y = head_y + self.head_radius + 8
        if self.mood == "happy":
            arcade.draw_text("❤", x, indicator_y, arcade.color.PINK, 14, anchor_x="center")
        elif self.mood == "angry":
            arcade.draw_text("!", x, indicator_y, arcade.color.RED, 18, anchor_x="center")

    def on_order_complete(self, success):
        self.order_submitted = True
        if success:
            self.state = "completed"
            self.mood = "happy"
        else:
            self.state = "leaving_angry"
            self.mood = "angry"


def _load_customer_textures():
    """Загружает текстуры посетителей (idle/happy/angry). Любое разрешение — масштабируется при отрисовке."""
    from utils import load_texture
    textures = {}
    for mood, path in Customer.TEXTURE_PATHS.items():
        if os.path.exists(path):
            try:
                textures[mood] = load_texture(path)
            except Exception:
                pass
    return textures if textures else None


class CustomerManager:
    def __init__(self, game):
        self.game = game
        self.customers = []
        self.spawn_timer = 0
        self._customer_textures = _load_customer_textures()

    def setup_customers(self):
        self.customers = []
        self.spawn_timer = 0

    def update(self, delta_time):
        for customer in self.customers[:]:
            customer.update(delta_time)

    def spawn_customer(self):
        customer_type = "standard"
        customer = Customer(self.game, customer_type, textures=self._customer_textures)
        self.customers.append(customer)
        arcade.play_sound(arcade.load_sound("sounds/order.wav"))

    def draw(self):
        for customer in self.customers:
            customer.draw()

    def check_customer_click(self, x, y):
        for customer in self.customers:
            if (abs(x - customer.center_x) < 50 and
                    abs(y - customer.center_y) < 100 and
                    customer.state == "waiting" and
                    not customer.order_submitted):
                success = self.game.order_system.submit_order(self.game.food_manager.get_prepared_items())
                customer.on_order_complete(success)
                return

    def remove_angry_customers(self):
        for customer in self.customers[:]:
            if customer.state == "waiting" and not customer.order_submitted:
                customer.state = "leaving_angry"