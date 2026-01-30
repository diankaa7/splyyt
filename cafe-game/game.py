import arcade
import os
from levels import LevelManager
from customer import CustomerManager
from food import FoodManager
from ui import UIManager
from order_system import OrderSystem, Order
from utils import load_texture, get_texture_display_size
from chef import Chef


class FastFoodGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.game_state = "MENU"
        self.show_cooking_frame = False
        self.level_complete_timer = 0.0
        self.current_level = 1
        self.money = 500
        self.score = 0
        self.level_manager = None
        self.customer_manager = None
        self.food_manager = None
        self.ui_manager = None
        self.order_system = None
        self.background = None
        self.chef = None
        self.equipment_sprites = None
        self.setup_managers()

    def setup_managers(self):
        self.level_manager = LevelManager(self)
        self.customer_manager = CustomerManager(self)
        self.food_manager = FoodManager(self)
        self.ui_manager = UIManager(self)
        self.order_system = OrderSystem(self)

    def setup(self):
        self.background = load_texture("images/main_menu_bg.png")
        chef_tex = None
        for path in ("images/chef.png", "images/player_idle.png"):
            if os.path.exists(path):
                chef_tex = load_texture(path)
                break
        self.chef = Chef(center_x=300, center_y=250, texture=chef_tex)
        self.setup_equipment()

    EQUIPMENT_DISPLAY_SIZE = 140

    def setup_equipment(self):
        self.equipment_sprites = arcade.SpriteList()
        positions = [(400, 280), (560, 280), (720, 280), (880, 280)]
        equipment = ["grill", "fryer", "ice_cream_machine", "soda_tap"]
        for i, pos in enumerate(positions):
            sprite = arcade.Sprite()
            tex = load_texture(f"images/{equipment[i]}.png")
            sprite.texture = tex
            dw, dh = get_texture_display_size(tex, self.EQUIPMENT_DISPLAY_SIZE, self.EQUIPMENT_DISPLAY_SIZE)
            tw, th = getattr(tex, "width", 64), getattr(tex, "height", 64)
            sprite.scale = dw / tw if tw else 1.0
            sprite.center_x = pos[0]
            sprite.center_y = pos[1]
            self.equipment_sprites.append(sprite)

    def start_game(self):
        self.game_state = "PLAYING"
        self.current_level = 1
        self.money = 500
        self.score = 0
        self.level_manager.load_level(self.current_level)
        self.customer_manager.setup_customers()
        self.food_manager.reset_inventory()
        self.order_system.reset_orders()
        self.background = load_texture("images/level_bg.png")

    def next_level(self):
        self.current_level += 1
        if self.current_level > 7:
            self.game_state = "GAME_OVER"
            return
        self.level_manager.load_level(self.current_level)
        self.customer_manager.setup_customers()
        self.background = load_texture("images/level_bg.png")

    def game_over(self):
        self.game_state = "GAME_OVER"

    def on_draw(self):
        self.clear()
        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "PLAYING":
            if self.show_cooking_frame:
                self.draw_cooking_frame()
            else:
                self.draw_game()
        elif self.game_state == "LEVEL_COMPLETE":
            self.draw_game()
            self.draw_level_complete_overlay()
        elif self.game_state == "PAUSED":
            self.draw_game()
            self.draw_pause_overlay()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over()

    def draw_menu(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, 1920, 1080)
        arcade.draw_texture_rect(self.background, rect)
        self.ui_manager.draw_menu_buttons()

    def draw_game(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, 1280, 720)
        arcade.draw_texture_rect(self.background, rect)
        self.customer_manager.draw()
        if self.chef:
            self.chef.draw()
        self.order_system.draw_orders()
        self.ui_manager.draw_hud()

    def draw_cooking_frame(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, 1280, 720)
        arcade.draw_texture_rect(self.background, rect)

        overlay_rect = arcade.types.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_rect_filled(overlay_rect, (0, 0, 0, 100))

        title_bg = arcade.types.XYWH(self.width // 2, self.height - 50, 400, 80)
        arcade.draw_rect_filled(title_bg, (50, 50, 50, 220))
        arcade.draw_rect_outline(title_bg, arcade.color.GOLD, 3)
        
        arcade.draw_text(
            "КУХНЯ — РЕЖИМ ГОТОВКИ",
            self.width // 2, self.height - 50,
            arcade.color.WHITE, 32, anchor_x="center", bold=True
        )

        self.equipment_sprites.draw()

        self.food_manager.draw_cooking_view()

        # Draw current order info (if any) — правый верхний угол
        if self.order_system.active_orders:
            order = self.order_system.active_orders[0]
            panel_w, panel_h = 280, 200
            margin_r, margin_t = 24, 90
            cx = self.width - margin_r - panel_w // 2
            cy = self.height - margin_t - panel_h // 2
            order_bg = arcade.types.XYWH(cx, cy, panel_w, panel_h)
            arcade.draw_rect_filled(order_bg, (50, 50, 50, 240))
            arcade.draw_rect_outline(order_bg, arcade.color.BLUE, 3)
            
            arcade.draw_text(
                "ТЕКУЩИЙ ЗАКАЗ:",
                cx, cy + 80,
                arcade.color.WHITE, 18, anchor_x="center", bold=True
            )
            
            y_offset = cy + 50
            for item in order.items:
                y_offset -= 25
                if isinstance(item, list):
                    arcade.draw_text(
                        Order.format_burger_layers(item),
                        cx, y_offset,
                        arcade.color.WHITE, 14, anchor_x="center"
                    )
                else:
                    arcade.draw_text(
                        Order._item_label_ru(item),
                        cx, y_offset,
                        arcade.color.WHITE, 16, anchor_x="center"
                    )
            
            time_left = max(0, order.max_time - order.elapsed_time)
            arcade.draw_text(
                f"Время: {int(time_left)}с",
                cx, cy - 80,
                arcade.color.RED, 18, anchor_x="center", bold=True
            )

        instruction_bg = arcade.types.XYWH(self.width // 2, 50, 800, 70)
        arcade.draw_rect_filled(instruction_bg, (0, 0, 0, 220))
        arcade.draw_rect_outline(instruction_bg, arcade.color.GREEN, 2)
        
        arcade.draw_text(
            "Кликайте по ингредиентам и оборудованию | K или ESC — вернуться",
            self.width // 2, 65,
            arcade.color.WHITE, 16, anchor_x="center", anchor_y="center", bold=True
        )
        arcade.draw_text(
            "Бургер: добавляйте только слои из ТЕКУЩЕГО ЗАКАЗА, затем нажмите ГРИЛЬ.",
            self.width // 2, 40,
            arcade.color.LIGHT_GRAY, 12, anchor_x="center", anchor_y="center"
        )

    def draw_pause_overlay(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_rect_filled(rect, arcade.color.BLACK_TRANSLUCENT)
        arcade.draw_text(
            "ПАУЗА",
            self.width // 2, self.height // 2,
            arcade.color.WHITE, 64, anchor_x="center"
        )
        arcade.draw_text(
            "Нажмите ESC для продолжения",
            self.width // 2, self.height // 2 - 80,
            arcade.color.GRAY, 24, anchor_x="center"
        )

    def draw_level_complete_overlay(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, self.width, self.height)
        arcade.draw_rect_filled(rect, (0, 0, 0, 160))
        arcade.draw_text(
            "УРОВЕНЬ ЗАВЕРШЁН",
            self.width // 2, self.height // 2 + 40,
            arcade.color.GOLD, 56, anchor_x="center"
        )
        arcade.draw_text(
            "Подождите, загружается следующий уровень...",
            self.width // 2, self.height // 2 - 20,
            arcade.color.WHITE, 24, anchor_x="center"
        )

    def draw_game_over(self):
        rect = arcade.types.XYWH(self.width // 2, self.height // 2, 1280, 720)
        arcade.draw_texture_rect(self.background, rect)
        arcade.draw_text(
            "КАМПАНИЯ ПРОЙДЕНА!",
            self.width // 2, self.height - 150,
            arcade.color.GOLD, 54, anchor_x="center"
        )
        arcade.draw_text(
            f"Итоговый счёт: {self.score}",
            self.width // 2, self.height - 250,
            arcade.color.WHITE, 36, anchor_x="center"
        )
        arcade.draw_text(
            f"Всего денег: ${self.money}",
            self.width // 2, self.height - 300,
            arcade.color.WHITE, 36, anchor_x="center"
        )
        self.ui_manager.draw_menu_buttons(game_over=True)

    def on_update(self, delta_time):
        if self.game_state == "PLAYING":
            self.customer_manager.update(delta_time)
            self.food_manager.update(delta_time)
            self.order_system.update(delta_time)
            self.level_manager.update(delta_time)
            if self.level_manager.is_level_complete():
                self.game_state = "LEVEL_COMPLETE"
                self.level_complete_timer = 0.0
        elif self.game_state == "LEVEL_COMPLETE":
            self.level_complete_timer += delta_time
            if self.level_complete_timer >= 3.0:
                self.next_level()
                if self.game_state != "GAME_OVER":
                    self.game_state = "PLAYING"

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.game_state == "PLAYING" and self.show_cooking_frame:
                self.show_cooking_frame = False
                return

            if self.game_state == "PLAYING":
                self.game_state = "PAUSED" if self.game_state != "PAUSED" else "PLAYING"
            elif self.game_state == "PAUSED":
                self.game_state = "PLAYING"
            elif self.game_state == "MENU":
                self.close()

        if self.game_state == "PLAYING":
            if key == arcade.key.K:
                self.show_cooking_frame = not self.show_cooking_frame
            elif self.show_cooking_frame:
                if key == arcade.key.NUM_1:
                    self.food_manager.select_ingredient("burger")
                elif key == arcade.key.NUM_2:
                    self.food_manager.select_ingredient("fries")
                elif key == arcade.key.NUM_3:
                    self.food_manager.select_ingredient("icecream")
                elif key == arcade.key.NUM_4:
                    self.food_manager.select_ingredient("drink")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "MENU":
            self.ui_manager.check_menu_click(x, y)
        elif self.game_state == "GAME_OVER":
            self.ui_manager.check_menu_click(x, y, game_over=True)
        elif self.game_state == "PLAYING":
            self.ui_manager.check_hud_click(x, y)
            if self.show_cooking_frame:
                self.food_manager.check_equipment_click(x, y)
            else:
                self.customer_manager.check_customer_click(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_state == "MENU":
            self.ui_manager.update_menu_hover(x, y)
        elif self.game_state == "GAME_OVER":
            self.ui_manager.update_menu_hover(x, y, game_over=True)