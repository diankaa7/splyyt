import math
import random

from burger import Burger
from customers import Customer
from drink import Drink
from ingredients import Ingredient, IngredientButton
from orders import Order
from pizza import Pizza
from ui_elements import *


class PizzaGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.game_state = "start"
        self.level = 1
        self.money = 0
        self.money_target = LEVEL_MONEY_TARGETS[0]
        self.customers_served = 0
        self.customers_target = LEVEL_CUSTOMER_COUNTS[0]
        self.level_time_left = LEVEL_TIME_LIMITS[0]

        self.pizza = None
        self.burger = None
        self.drink = None
        self.current_order = None
        self.order_timer = 0
        self.order_active = False
        self.selected_ingredient = None
        self.selected_drink_type = None

        self.ingredients = {}
        self.ingredient_buttons = []
        self.drink_buttons = []
        self.ui_elements = {}
        self.customer = None

        self.cut_start = None
        self.cut_end = None
        self.is_cutting = False
        self.cut_mode = False

        self.message_display = None
        self.game_over_reason = ""

        self.background_texture = None
        self.pizza_board_texture = None
        self.order_pad_texture = None
        self.kitchen_background = None
        self.order_background = None

        self.current_tab = "cooking"
        self.order_queue = []
        self.active_orders = []

        self.setup()

    def setup(self):
        self.pizza = Pizza()
        self.burger = Burger()
        self.drink = Drink()
        self.customer = Customer(CUSTOMER_X, CUSTOMER_Y)
        self.message_display = MessageDisplay(SCREEN_WIDTH // 2, 100)

        self.load_textures()
        self.create_ingredients()
        self.create_drink_buttons()
        self.create_ui_elements()

        self.start_new_order()

    def load_textures(self):
        try:
            self.background_texture = arcade.load_texture("images/background.png")
        except:
            self.background_texture = None

        try:
            self.kitchen_background = arcade.load_texture("images/background_main.jpg")
        except:
            self.kitchen_background = None

        try:
            self.order_background = arcade.load_texture("images/background_main.jpg")
        except:
            self.order_background = None

        try:
            self.pizza_board_texture = arcade.load_texture("images/pizza_board.png")
        except:
            self.pizza_board_texture = None

        try:
            self.order_pad_texture = arcade.load_texture("images/order_pad.png")
        except:
            self.order_pad_texture = None

    def create_ingredients(self):
        all_ingredients = [
            ("pepperoni", INGREDIENT_PRICES["pepperoni"], INGREDIENT_COLORS["pepperoni"]),
            ("mushrooms", INGREDIENT_PRICES["mushrooms"], INGREDIENT_COLORS["mushrooms"]),
            ("peppers", INGREDIENT_PRICES["peppers"], INGREDIENT_COLORS["peppers"]),
            ("onions", INGREDIENT_PRICES["onions"], INGREDIENT_COLORS["onions"]),
            ("olives", INGREDIENT_PRICES["olives"], INGREDIENT_COLORS["olives"]),
            ("tomato", INGREDIENT_PRICES["tomato"], INGREDIENT_COLORS["tomato"]),
            ("sausage", INGREDIENT_PRICES["sausage"], INGREDIENT_COLORS["sausage"]),
            ("basil", INGREDIENT_PRICES["basil"], INGREDIENT_COLORS["basil"]),
            ("pineapple", INGREDIENT_PRICES["pineapple"], INGREDIENT_COLORS["pineapple"]),
            ("ham", INGREDIENT_PRICES["ham"], INGREDIENT_COLORS["ham"]),
            ("bacon", INGREDIENT_PRICES["bacon"], INGREDIENT_COLORS["bacon"]),
            ("garlic", INGREDIENT_PRICES["garlic"], INGREDIENT_COLORS["garlic"])
        ]

        self.ingredients = {}
        self.ingredient_buttons = []

        available_in_level = INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]

        y_pos = INGREDIENT_BUTTONS_Y_START
        for name, price, color in all_ingredients:
            try:
                texture = arcade.load_texture(f"images/{name}.png")
            except:
                texture = None

            ingredient = Ingredient(name, price, color, texture)
            ingredient.available = (name in available_in_level) or (name == "cheese")
            self.ingredients[name] = ingredient

            button = IngredientButton(ingredient, INGREDIENT_BUTTONS_X, y_pos)
            button.is_active = ingredient.available
            self.ingredient_buttons.append(button)
            y_pos -= INGREDIENT_BUTTON_SPACING

    def create_drink_buttons(self):
        burger_ingredients = [
            ("lettuce", INGREDIENT_PRICES["lettuce"], INGREDIENT_COLORS["lettuce"]),
            ("tomato", INGREDIENT_PRICES["tomato"], INGREDIENT_COLORS["tomato"]),
            ("cheese", INGREDIENT_PRICES["cheese"], INGREDIENT_COLORS["cheese"]),
            ("onions", INGREDIENT_PRICES["onions"], INGREDIENT_COLORS["onions"]),
            ("pickles", INGREDIENT_PRICES["pickles"], INGREDIENT_COLORS["pickles"]),
            ("bacon", INGREDIENT_PRICES["bacon"], INGREDIENT_COLORS["bacon"]),
            ("mayonnaise", INGREDIENT_PRICES["mayonnaise"], INGREDIENT_COLORS["mayonnaise"]),
            ("ketchup", INGREDIENT_PRICES["ketchup"], INGREDIENT_COLORS["ketchup"])
        ]

        available_burger_ingredients = BURGER_INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]
        for name, price, color in burger_ingredients:
            if name not in self.ingredients:
                try:
                    texture = arcade.load_texture(f"images/{name}.png")
                except:
                    texture = None
                ingredient = Ingredient(name, price, color, texture)
                ingredient.available = name in available_burger_ingredients
                self.ingredients[name] = ingredient

    def create_ui_elements(self):
        self.ui_elements = {
            "start_button": Button(START_BUTTON_X, 250,
                                   BUTTON_WIDTH, BUTTON_HEIGHT, "НАЧАТЬ ИГРУ"),
            "exit_button": Button(EXIT_BUTTON_X, 150,
                                  BUTTON_WIDTH, BUTTON_HEIGHT, "ВЫХОД"),
            "restart_button": Button(RESTART_BUTTON_X, 200,
                                     BUTTON_WIDTH, BUTTON_HEIGHT, "ЗАНОВО"),
            "continue_button": Button(CONTINUE_BUTTON_X, 300,
                                      BUTTON_WIDTH, BUTTON_HEIGHT, "ДАЛЕЕ"),
            "oven_button": Button(OVEN_X, OVEN_Y, OVEN_WIDTH, OVEN_HEIGHT, "ПЕЧЬ"),
            "cut_button": Button(CUT_BUTTON_X, CUT_BUTTON_Y,
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "РЕЗАТЬ"),
            "submit_button": Button(SUBMIT_BUTTON_X, SUBMIT_BUTTON_Y,
                                    BUTTON_WIDTH, BUTTON_HEIGHT, "ПОДАТЬ"),
            "dough_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 90,
                                   BUTTON_WIDTH, BUTTON_HEIGHT, "ТЕСТО"),
            "sauce_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 45,
                                   BUTTON_WIDTH, BUTTON_HEIGHT, "СОУС"),
            "cheese_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START,
                                    BUTTON_WIDTH, BUTTON_HEIGHT, "СЫР"),
            "grill_button": Button(GRILL_X, GRILL_Y, GRILL_WIDTH, GRILL_HEIGHT, "ГРИЛЬ"),
            "drink_machine_button": Button(DRINK_MACHINE_X, DRINK_MACHINE_Y,
                                          DRINK_MACHINE_WIDTH, DRINK_MACHINE_HEIGHT, "НАПИТОК"),
            "assemble_button": Button(ASSEMBLE_BUTTON_X, ASSEMBLE_BUTTON_Y,
                                     BUTTON_WIDTH, BUTTON_HEIGHT, "СОБРАТЬ"),
            "bottom_bun_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 135,
                                        BUTTON_WIDTH, BUTTON_HEIGHT, "НИЖНЯЯ БУЛОЧКА"),
            "top_bun_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 90,
                                     BUTTON_WIDTH, BUTTON_HEIGHT, "ВЕРХНЯЯ БУЛОЧКА"),
            "beef_patty_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 45,
                                        BUTTON_WIDTH, BUTTON_HEIGHT, "ГОВЯЖЬЯ КОТЛЕТА"),
            "chicken_patty_button": Button(INGREDIENT_BUTTONS_X + 210, INGREDIENT_BUTTONS_Y_START + 45,
                                           BUTTON_WIDTH, BUTTON_HEIGHT, "КУРИНАЯ КОТЛЕТА"),
            "ice_button": Button(INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 135,
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "ЛЕД"),
            "order_tab": Button(ORDER_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT, "ПРИНЯТИЕ ЗАКАЗОВ"),
            "cooking_tab": Button(COOKING_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT, "ГОТОВКА"),
        }

        try:
            self.ui_elements["oven_button"].texture = arcade.load_texture("images/oven.png")
        except:
            pass

        self.timer_display = TimerDisplay(TIMER_DISPLAY_X, TIMER_DISPLAY_Y)
        self.money_display = MoneyDisplay(MONEY_DISPLAY_X, MONEY_DISPLAY_Y)
        self.level_display = LevelDisplay(LEVEL_DISPLAY_X, LEVEL_DISPLAY_Y)

        try:
            self.timer_display.texture = arcade.load_texture("images/timer_icon.png")
            self.money_display.texture = arcade.load_texture("images/money_icon.png")
            self.level_display.texture = arcade.load_texture("images/level_icon.png")
        except:
            pass

        self.update_ui_visibility()

    def update_ui_visibility(self):
        for element in self.ui_elements.values():
            element.is_visible = False

        if self.game_state == "start":
            self.ui_elements["start_button"].is_visible = True
            self.ui_elements["exit_button"].is_visible = True

            self.ui_elements["start_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["start_button"].y = 250
            self.ui_elements["exit_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["exit_button"].y = 150

        elif self.game_state == "game":
            self.ui_elements["order_tab"].is_visible = True
            self.ui_elements["cooking_tab"].is_visible = True
            self.ui_elements["order_tab"].x = ORDER_TAB_X
            self.ui_elements["order_tab"].y = TAB_Y
            self.ui_elements["cooking_tab"].x = COOKING_TAB_X
            self.ui_elements["cooking_tab"].y = TAB_Y

            if self.current_tab == "cooking":
                self.ui_elements["submit_button"].is_visible = True
                self.ui_elements["submit_button"].x = SUBMIT_BUTTON_X
                self.ui_elements["submit_button"].y = SUBMIT_BUTTON_Y

                if self.current_order and self.current_order.order_type == "pizza":
                    self.ui_elements["oven_button"].is_visible = True
                    self.ui_elements["cut_button"].is_visible = True
                    self.ui_elements["dough_button"].is_visible = True
                    self.ui_elements["sauce_button"].is_visible = True
                    self.ui_elements["cheese_button"].is_visible = True
                    self.ui_elements["oven_button"].x = OVEN_X
                    self.ui_elements["oven_button"].y = OVEN_Y
                    self.ui_elements["cut_button"].x = CUT_BUTTON_X
                    self.ui_elements["cut_button"].y = CUT_BUTTON_Y
                    self.ui_elements["dough_button"].x = INGREDIENT_BUTTONS_X
                    self.ui_elements["dough_button"].y = INGREDIENT_BUTTONS_Y_START + 90
                    self.ui_elements["sauce_button"].x = INGREDIENT_BUTTONS_X
                    self.ui_elements["sauce_button"].y = INGREDIENT_BUTTONS_Y_START + 45
                    self.ui_elements["cheese_button"].x = INGREDIENT_BUTTONS_X
                    self.ui_elements["cheese_button"].y = INGREDIENT_BUTTONS_Y_START
            elif self.current_order and self.current_order.order_type == "burger":
                self.ui_elements["grill_button"].is_visible = True
                self.ui_elements["assemble_button"].is_visible = True
                self.ui_elements["bottom_bun_button"].is_visible = True
                self.ui_elements["top_bun_button"].is_visible = True
                self.ui_elements["beef_patty_button"].is_visible = True
                self.ui_elements["chicken_patty_button"].is_visible = True
                self.ui_elements["grill_button"].x = GRILL_X
                self.ui_elements["grill_button"].y = GRILL_Y
                self.ui_elements["assemble_button"].x = ASSEMBLE_BUTTON_X
                self.ui_elements["assemble_button"].y = ASSEMBLE_BUTTON_Y
                self.ui_elements["bottom_bun_button"].x = INGREDIENT_BUTTONS_X
                self.ui_elements["bottom_bun_button"].y = INGREDIENT_BUTTONS_Y_START + 135
                self.ui_elements["top_bun_button"].x = INGREDIENT_BUTTONS_X
                self.ui_elements["top_bun_button"].y = INGREDIENT_BUTTONS_Y_START + 90
                self.ui_elements["beef_patty_button"].x = INGREDIENT_BUTTONS_X
                self.ui_elements["beef_patty_button"].y = INGREDIENT_BUTTONS_Y_START + 45
                self.ui_elements["chicken_patty_button"].x = INGREDIENT_BUTTONS_X + 210
                self.ui_elements["chicken_patty_button"].y = INGREDIENT_BUTTONS_Y_START + 45
            elif self.current_order and self.current_order.order_type == "drink":
                self.ui_elements["drink_machine_button"].is_visible = True
                self.ui_elements["ice_button"].is_visible = True
                self.ui_elements["drink_machine_button"].x = DRINK_MACHINE_X
                self.ui_elements["drink_machine_button"].y = DRINK_MACHINE_Y
                self.ui_elements["ice_button"].x = INGREDIENT_BUTTONS_X
                self.ui_elements["ice_button"].y = INGREDIENT_BUTTONS_Y_START + 135

        elif self.game_state == "level_complete":
            self.ui_elements["continue_button"].is_visible = True
            self.ui_elements["restart_button"].is_visible = True

            self.ui_elements["continue_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["continue_button"].y = 300
            self.ui_elements["restart_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["restart_button"].y = 200

        elif self.game_state == "game_over":
            self.ui_elements["restart_button"].is_visible = True
            self.ui_elements["exit_button"].is_visible = True

            self.ui_elements["restart_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["restart_button"].y = 300
            self.ui_elements["exit_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["exit_button"].y = 200

        elif self.game_state == "game_complete":
            self.ui_elements["restart_button"].is_visible = True
            self.ui_elements["exit_button"].is_visible = True

            self.ui_elements["restart_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["restart_button"].y = 300
            self.ui_elements["exit_button"].x = SCREEN_WIDTH // 2
            self.ui_elements["exit_button"].y = 200
    def check_level_complete(self):
        return (self.customers_served >= self.customers_target and
                self.money >= self.money_target)

    def advance_level(self):
        if self.level < 7:
            self.level += 1
            self.money_target = LEVEL_MONEY_TARGETS[self.level - 1]
            self.customers_target = LEVEL_CUSTOMER_COUNTS[self.level - 1]
            self.level_time_left = LEVEL_TIME_LIMITS[self.level - 1]
            self.customers_served = 0
            return True
        return False

    def on_draw(self):
        self.clear()

        if self.background_texture:
            arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                          SCREEN_WIDTH, SCREEN_HEIGHT,
                                          self.background_texture)

        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "game":
            self.draw_game_screen()
        elif self.game_state == "level_complete":
            self.draw_level_complete_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "game_complete":
            self.draw_game_complete_screen()

    def draw_start_screen(self):
        arcade.draw_text("CAFE CHEF DELUXE", SCREEN_WIDTH // 2, 650,
                         (255, 230, 0), TITLE_FONT_SIZE,
                         anchor_x="center", anchor_y="center", bold=True)

        arcade.draw_text("Приготовь пиццу, бургеры и напитки для каждого клиента!",
                         SCREEN_WIDTH // 2, 590, TEXT_COLOR, FONT_SIZE + 2,
                         anchor_x="center", anchor_y="center")

        arcade.draw_text("Как играть:", SCREEN_WIDTH // 2, 520,
                         (255, 255, 200), FONT_SIZE,
                         anchor_x="center", anchor_y="center", bold=True)

        instructions = [
            "1. Выполняй заказы клиентов вовремя",
            "2. Пицца: тесто, соус, сыр, топпинги, печь, резать",
            "3. Бургер: булочки, котлета, гриль, ингредиенты, собрать",
            "4. Напитки: выбери тип, наполни, добавь лед",
            "5. Заработай достаточно денег для перехода на следующий уровень",
            "6. Пройди все 7 уровней и стань шеф-поваром!"
        ]

        y_pos = 470
        for instruction in instructions:
            arcade.draw_text(instruction, SCREEN_WIDTH // 2, y_pos,
                             TEXT_COLOR, FONT_SIZE - 2,
                             anchor_x="center", anchor_y="center")
            y_pos -= 32

        self.ui_elements["start_button"].draw()
        self.ui_elements["exit_button"].draw()

    def draw_game_screen(self):
        if self.current_tab == "cooking":
            if self.kitchen_background:
                arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                              SCREEN_WIDTH, SCREEN_HEIGHT,
                                              self.kitchen_background)
            else:
                arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, KITCHEN_BG_COLOR)

            if self.current_order and self.current_order.order_type == "pizza":
                if self.pizza_board_texture:
                    arcade.draw_texture_rectangle(PIZZA_X, PIZZA_Y,
                                                  PIZZA_RADIUS * 2.5, PIZZA_RADIUS * 2.5,
                                                  self.pizza_board_texture)
                self.pizza.draw()
            elif self.current_order and self.current_order.order_type == "burger":
                arcade.draw_rectangle_filled(BURGER_X, BURGER_Y - 30, BURGER_WIDTH + 100, BURGER_HEIGHT + 200,
                                             (200, 180, 160))
                self.burger.draw()
            elif self.current_order and self.current_order.order_type == "drink":
                arcade.draw_rectangle_filled(DRINK_X - 100, DRINK_Y - 100, 300, 300, (220, 220, 220))
                self.drink.draw()

            for button in self.ingredient_buttons:
                if self.current_order and self.current_order.order_type == "burger":
                    if button.ingredient.name in BURGER_INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]:
                        button.draw()
                elif self.current_order and self.current_order.order_type == "pizza":
                    button.draw()

            for drink_name in DRINKS_PER_LEVEL[min(self.level - 1, 6)]:
                if drink_name not in self.ingredients:
                    color = DRINK_COLORS.get(drink_name, (200, 200, 200))
                    price = DRINK_PRICES.get(drink_name, 2)
                    try:
                        texture = arcade.load_texture(f"images/{drink_name}.png")
                    except:
                        texture = None
                    ingredient = Ingredient(drink_name, price, color, texture)
                    ingredient.available = True
                    self.ingredients[drink_name] = ingredient

            if self.current_order and self.current_order.order_type == "drink":
                y_pos = INGREDIENT_BUTTONS_Y_START
                for drink_name in DRINKS_PER_LEVEL[min(self.level - 1, 6)]:
                    if drink_name in self.ingredients:
                        button = IngredientButton(self.ingredients[drink_name],
                                                 INGREDIENT_BUTTONS_X, y_pos)
                        button.is_active = True
                        button.draw()
                        y_pos -= INGREDIENT_BUTTON_SPACING

            if self.selected_ingredient:
                arcade.draw_text(f"Выбрано: {self.selected_ingredient.name.capitalize()}",
                                 INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 160,
                                 (255, 255, 200), FONT_SIZE, anchor_x="center", bold=True)

            if self.selected_drink_type:
                arcade.draw_text(f"Напиток: {self.selected_drink_type.capitalize()}",
                                 INGREDIENT_BUTTONS_X, INGREDIENT_BUTTONS_Y_START + 160,
                                 (200, 240, 255), FONT_SIZE, anchor_x="center", bold=True)

            if self.cut_mode:
                arcade.draw_text("РЕЖИМ РЕЗКИ - проведите 4 линии через пиццу",
                                 PIZZA_X, PIZZA_Y - PIZZA_RADIUS - 40,
                                 (255, 100, 100), FONT_SIZE, anchor_x="center", bold=True)

            if self.is_cutting and self.cut_start:
                arcade.draw_line(self.cut_start[0], self.cut_start[1],
                                 self.cut_end[0], self.cut_end[1],
                                 (255, 0, 0), 3)

        elif self.current_tab == "orders":
            if self.order_background:
                arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                              SCREEN_WIDTH, SCREEN_HEIGHT,
                                              self.order_background)
            else:
                arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, ORDER_BG_COLOR)

            arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                         SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150,
                                         (250, 248, 240, 240))
            arcade.draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                          SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150,
                                          (180, 160, 140))

            arcade.draw_text("ЗАКАЗЫ КЛИЕНТОВ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
                             (100, 80, 60), BIG_FONT_SIZE + 10,
                             anchor_x="center", anchor_y="center", bold=True)

            if self.current_order:
                order_x = SCREEN_WIDTH // 2
                order_y = SCREEN_HEIGHT // 2 + 100
                if self.order_pad_texture:
                    arcade.draw_texture_rectangle(order_x, order_y,
                                                  ORDER_DISPLAY_WIDTH * 1.2, ORDER_DISPLAY_HEIGHT * 1.2,
                                                  self.order_pad_texture)
                self.current_order.draw(order_x, order_y)

            if len(self.order_queue) > 0:
                arcade.draw_text("СЛЕДУЮЩИЕ ЗАКАЗЫ:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250,
                                 (100, 80, 60), FONT_SIZE + 5, anchor_x="center", bold=True)
                y_offset = 300
                for i, order in enumerate(self.order_queue[:3]):
                    order.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - y_offset)
                    y_offset += 200

            self.customer.draw()

        arcade.draw_rectangle_filled(ORDER_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT,
                                     ORDER_TAB_ACTIVE_COLOR if self.current_tab == "orders" else ORDER_TAB_COLOR)
        arcade.draw_rectangle_outline(ORDER_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT,
                                      (255, 255, 255))
        arcade.draw_text("ПРИНЯТИЕ ЗАКАЗОВ", ORDER_TAB_X, TAB_Y,
                         (255, 255, 255), FONT_SIZE + 5,
                         anchor_x="center", anchor_y="center", bold=True)

        arcade.draw_rectangle_filled(COOKING_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT,
                                     COOKING_TAB_ACTIVE_COLOR if self.current_tab == "cooking" else COOKING_TAB_COLOR)
        arcade.draw_rectangle_outline(COOKING_TAB_X, TAB_Y, TAB_WIDTH, TAB_HEIGHT,
                                      (255, 255, 255))
        arcade.draw_text("ГОТОВКА", COOKING_TAB_X, TAB_Y,
                         (255, 255, 255), FONT_SIZE + 5,
                         anchor_x="center", anchor_y="center", bold=True)

        for key in self.ui_elements:
            if self.ui_elements[key].is_visible and key not in ["order_tab", "cooking_tab"]:
                self.ui_elements[key].draw()

        self.timer_display.time_left = self.order_timer
        self.timer_display.total_time = self.current_order.time_limit if self.current_order else 60
        self.timer_display.draw()

        self.money_display.money = self.money
        self.money_display.target = self.money_target
        self.money_display.draw()

        self.level_display.level = self.level
        self.level_display.customers_served = self.customers_served
        self.level_display.total_customers = self.customers_target
        self.level_display.draw()

        level_time_color = (255, 255, 255)
        if self.level_time_left < 30:
            level_time_color = (255, 100, 100)
        elif self.level_time_left < 60:
            level_time_color = (255, 200, 100)

        arcade.draw_text(f"Время уровня: {int(self.level_time_left)}с",
                         SCREEN_WIDTH - 150, 850, level_time_color,
                         FONT_SIZE, anchor_x="center", bold=True)

        self.message_display.draw()

    def draw_level_complete_screen(self):
        arcade.draw_text(f"Уровень {self.level - 1} пройден!", SCREEN_WIDTH // 2, 600,
                         (100, 255, 100), TITLE_FONT_SIZE,
                         anchor_x="center", bold=True)
        arcade.draw_text(f"Заработано: ${self.money}", SCREEN_WIDTH // 2, 520,
                         (255, 255, 255), BIG_FONT_SIZE, anchor_x="center")

        if self.level <= 7:
            arcade.draw_text(f"Следующий уровень: {self.level}", SCREEN_WIDTH // 2, 470,
                             (255, 255, 200), FONT_SIZE, anchor_x="center")

            new_ingredients = []
            current_ingredients = INGREDIENTS_PER_LEVEL[max(0, self.level - 2)]
            next_ingredients = INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]

            for ing in next_ingredients:
                if ing not in current_ingredients and ing != "cheese":
                    new_ingredients.append(ing.capitalize())

            if new_ingredients:
                arcade.draw_text("Новые ингредиенты:", SCREEN_WIDTH // 2, 420,
                                 (255, 200, 100), FONT_SIZE, anchor_x="center", bold=True)

                y_pos = 380
                for ing in new_ingredients:
                    arcade.draw_text(f"• {ing}", SCREEN_WIDTH // 2, y_pos,
                                     (255, 255, 200), FONT_SIZE, anchor_x="center")
                    y_pos -= 30

        self.ui_elements["continue_button"].draw()
        self.ui_elements["restart_button"].draw()

    def draw_game_over_screen(self):
        arcade.draw_text("ИГРА ОКОНЧЕНА", SCREEN_WIDTH // 2, 600,
                         (255, 100, 100), TITLE_FONT_SIZE,
                         anchor_x="center", bold=True)
        arcade.draw_text(f"Причина: {self.game_over_reason}", SCREEN_WIDTH // 2, 540,
                         (255, 255, 255), FONT_SIZE + 2, anchor_x="center")
        arcade.draw_text(f"Вы достигли уровня {self.level}", SCREEN_WIDTH // 2, 490,
                         (255, 255, 255), FONT_SIZE, anchor_x="center")
        arcade.draw_text(f"Заработано: ${self.money}", SCREEN_WIDTH // 2, 450,
                         (255, 255, 255), FONT_SIZE, anchor_x="center")
        arcade.draw_text(f"Обслужено клиентов: {self.customers_served}", SCREEN_WIDTH // 2, 410,
                         (255, 255, 255), FONT_SIZE, anchor_x="center")

        self.ui_elements["restart_button"].draw()
        self.ui_elements["exit_button"].draw()

    def draw_game_complete_screen(self):
        arcade.draw_text("ПОБЕДА!", SCREEN_WIDTH // 2, 600,
                         (100, 255, 100), TITLE_FONT_SIZE,
                         anchor_x="center", bold=True)
        arcade.draw_text("Вы прошли все 7 уровней!", SCREEN_WIDTH // 2, 540,
                         (255, 255, 255), BIG_FONT_SIZE, anchor_x="center")
        arcade.draw_text(f"Итоговый счет: ${self.money}", SCREEN_WIDTH // 2, 490,
                         (255, 255, 0), BIG_FONT_SIZE, anchor_x="center", bold=True)
        arcade.draw_text(f"Обслужено клиентов: {self.customers_served}", SCREEN_WIDTH // 2, 440,
                         (255, 255, 255), FONT_SIZE, anchor_x="center")

        rating = ""
        if self.money >= 500:
            rating = "⭐⭐⭐⭐⭐ ШЕФ-ПОВАР МАСТЕР!"
        elif self.money >= 400:
            rating = "⭐⭐⭐⭐ ОТЛИЧНЫЙ ПОВАР!"
        elif self.money >= 300:
            rating = "⭐⭐⭐ ХОРОШИЙ ПОВАР"
        else:
            rating = "⭐⭐ НАЧИНАЮЩИЙ ПОВАР"

        arcade.draw_text(rating, SCREEN_WIDTH // 2, 380,
                         (255, 215, 0), FONT_SIZE + 4,
                         anchor_x="center", bold=True)

        self.ui_elements["restart_button"].draw()
        self.ui_elements["exit_button"].draw()

    def on_update(self, delta_time):
        if self.game_state == "game":
            self.level_time_left -= delta_time
            self.customer.update(delta_time)
            self.message_display.update(delta_time)

            if self.order_active:
                self.order_timer -= delta_time
                if self.order_timer <= 0:
                    self.order_active = False
                    patience_check = self.customer.leave()
                    if patience_check:
                        self.money -= self.current_order.penalty // 2
                        self.message_display.show_message(
                            f"{self.current_order.customer_name} ушел, но оставил половину оплаты", 3)
                    else:
                        self.money -= self.current_order.penalty
                        self.message_display.show_message(f"{self.current_order.customer_name} ушел без оплаты!", 3)
                    self.start_new_order()

            if self.pizza and self.pizza.state == STATE_COOKING:
                self.pizza.update_cooking(delta_time)

            if self.burger and self.burger.state == BURGER_STATE_COOKING:
                self.burger.update_cooking(delta_time)

            if self.drink and self.drink.state == DRINK_STATE_FILLING:
                self.drink.update_filling(delta_time)

            if self.level_time_left <= 0:
                self.game_over_reason = "Время уровня истекло"
                self.game_state = "game_over"
                self.update_ui_visibility()

            if self.check_level_complete():
                if self.advance_level():
                    self.game_state = "level_complete"
                    self.update_ui_visibility()
                else:
                    self.game_state = "game_complete"
                    self.update_ui_visibility()

            if self.money < 0:
                self.game_over_reason = "Закончились деньги"
                self.game_state = "game_over"
                self.update_ui_visibility()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_state == "start":
            for button in ["start_button", "exit_button"]:
                self.ui_elements[button].check_hover(x, y)

        elif self.game_state == "game":
            for button in self.ingredient_buttons:
                button.check_hover(x, y)

            for key in self.ui_elements:
                if self.ui_elements[key].is_visible:
                    self.ui_elements[key].check_hover(x, y)

            if self.is_cutting and self.cut_start:
                self.cut_end = (x, y)

        elif self.game_state == "level_complete":
            for button in ["continue_button", "restart_button"]:
                if self.ui_elements[button].is_visible:
                    self.ui_elements[button].check_hover(x, y)

        elif self.game_state in ["game_over", "game_complete"]:
            for button in ["restart_button", "exit_button"]:
                if self.ui_elements[button].is_visible:
                    self.ui_elements[button].check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.game_state == "start":
            if self.ui_elements["start_button"].is_clicked(x, y):
                self.game_state = "game"
                self.update_ui_visibility()
                self.setup()
            elif self.ui_elements["exit_button"].is_clicked(x, y):
                arcade.close_window()

        elif self.game_state == "game":
            if self.ui_elements["order_tab"].is_clicked(x, y):
                self.current_tab = "orders"
                self.update_ui_visibility()
            elif self.ui_elements["cooking_tab"].is_clicked(x, y):
                self.current_tab = "cooking"
                self.update_ui_visibility()

            elif self.current_tab == "orders":
                if self.current_order:
                    order_rect_x = SCREEN_WIDTH // 2
                    order_rect_y = SCREEN_HEIGHT // 2 + 100
                    if (abs(x - order_rect_x) < ORDER_DISPLAY_WIDTH // 2 and
                        abs(y - order_rect_y) < ORDER_DISPLAY_HEIGHT // 2):
                        if not self.order_active:
                            self.order_active = True
                            self.order_timer = self.current_order.time_limit
                            self.current_tab = "cooking"
                            self.update_ui_visibility()
                            self.message_display.show_message("Заказ принят! Перейдите на вкладку готовки", 3)

            if self.current_tab == "cooking":
                if self.cut_mode:
                    if self.is_cutting:
                        return

                    distance_to_pizza = math.sqrt((x - PIZZA_X) ** 2 + (y - PIZZA_Y) ** 2)
                    if distance_to_pizza < PIZZA_RADIUS * 1.5:
                        self.is_cutting = True
                        self.cut_start = (x, y)
                        self.cut_end = (x, y)

                elif self.ui_elements["dough_button"].is_clicked(x, y):
                 if self.pizza.add_dough():
                    self.message_display.show_message("Тесто добавлено!", 1)

            elif self.ui_elements["sauce_button"].is_clicked(x, y):
                if self.pizza.add_sauce():
                    sauce_level = "немного"
                    if self.pizza.sauce_coverage > 80:
                        sauce_level = "много"
                    elif self.pizza.sauce_coverage > 50:
                        sauce_level = "нормально"
                    self.message_display.show_message(f"Соус добавлен ({sauce_level})", 1)

            elif self.ui_elements["cheese_button"].is_clicked(x, y):
                if self.pizza.add_cheese():
                    cheese_level = "немного"
                    if self.pizza.cheese_coverage > 80:
                        cheese_level = "много"
                    elif self.pizza.cheese_coverage > 50:
                        cheese_level = "нормально"
                    self.message_display.show_message(f"Сыр добавлен ({cheese_level})", 1)

            elif self.ui_elements["oven_button"].is_clicked(x, y):
                if self.pizza.start_cooking():
                    self.message_display.show_message("Пицца в печи!", 2)

            elif self.ui_elements["cut_button"].is_clicked(x, y):
                if self.pizza.start_cutting():
                    self.cut_mode = True
                    self.message_display.show_message("Режим резки активирован!", 2)

            elif self.ui_elements["submit_button"].is_clicked(x, y):
                if self.pizza.state == STATE_COMPLETE and self.order_active:
                    success, feedback, score = self.current_order.check_pizza(self.pizza)

                    patience_check = self.customer.leave()

                    if success:
                        self.money += self.current_order.reward
                        self.customers_served += 1

                        if score >= 90:
                            self.message_display.show_message(f"ИДЕАЛЬНО! +${self.current_order.reward}", 3)
                        elif score >= 80:
                            self.message_display.show_message(f"Отлично! +${self.current_order.reward}", 3)
                        elif score >= 70:
                            self.message_display.show_message(f"Хорошо! +${self.current_order.reward}", 3)
                        else:
                            self.message_display.show_message(f"Принято. +${self.current_order.reward}", 3)
                    else:
                        self.money -= self.current_order.penalty
                        if patience_check:
                            self.message_display.show_message(f"Не принято: {feedback} -${self.current_order.penalty}",
                                                              3)
                        else:
                            self.message_display.show_message(f"Отвергнуто: {feedback} -${self.current_order.penalty}",
                                                              3)

                    self.start_new_order()
                elif self.pizza.state != STATE_COMPLETE:
                    self.message_display.show_message("Пицца не готова к подаче!", 2)
                elif not self.order_active:
                    self.message_display.show_message("Нет активного заказа!", 2)

            elif self.current_order and self.current_order.order_type == "burger":
                if self.ui_elements["bottom_bun_button"].is_clicked(x, y):
                    if self.burger.add_bottom_bun():
                        self.message_display.show_message("Нижняя булочка добавлена!", 1)

                elif self.ui_elements["top_bun_button"].is_clicked(x, y):
                    if self.burger.add_top_bun():
                        self.message_display.show_message("Верхняя булочка добавлена!", 1)

                elif self.ui_elements["beef_patty_button"].is_clicked(x, y):
                    if self.burger.add_patty("beef"):
                        self.message_display.show_message("Говяжья котлета добавлена!", 1)

                elif self.ui_elements["chicken_patty_button"].is_clicked(x, y):
                    if self.burger.add_patty("chicken"):
                        self.message_display.show_message("Куриная котлета добавлена!", 1)

                elif self.ui_elements["grill_button"].is_clicked(x, y):
                    if self.burger.start_cooking():
                        self.message_display.show_message("Котлета на гриле!", 2)
                    elif self.burger.finish_cooking():
                        self.message_display.show_message("Котлета готова!", 2)

                elif self.ui_elements["assemble_button"].is_clicked(x, y):
                    if self.burger.start_assembling():
                        self.message_display.show_message("Режим сборки активирован!", 1)
                    elif self.burger.finish_assembling():
                        self.message_display.show_message("Бургер собран!", 2)

                elif self.ui_elements["submit_button"].is_clicked(x, y):
                    if self.burger.state == BURGER_STATE_COMPLETE and self.order_active:
                        success, feedback, score = self.current_order.check_burger(self.burger)
                        patience_check = self.customer.leave()

                        if success:
                            self.money += self.current_order.reward
                            self.customers_served += 1
                            if score >= 90:
                                self.message_display.show_message(f"ИДЕАЛЬНО! +${self.current_order.reward}", 3)
                            elif score >= 80:
                                self.message_display.show_message(f"Отлично! +${self.current_order.reward}", 3)
                            else:
                                self.message_display.show_message(f"Хорошо! +${self.current_order.reward}", 3)
                        else:
                            self.money -= self.current_order.penalty
                            self.message_display.show_message(f"Не принято: {feedback} -${self.current_order.penalty}", 3)

                        self.start_new_order()

                else:
                    for ing_button in self.ingredient_buttons:
                        if ing_button.is_clicked(x, y) and ing_button.is_active:
                            if ing_button.ingredient.name in BURGER_INGREDIENTS_PER_LEVEL[min(self.level - 1, 6)]:
                                self.selected_ingredient = ing_button.ingredient
                                self.message_display.show_message(f"Выбран {ing_button.ingredient.name.capitalize()}", 1)

                    if self.selected_ingredient:
                        if self.burger.add_ingredient(self.selected_ingredient.name):
                            self.money -= self.selected_ingredient.price
                            self.message_display.show_message(f"{self.selected_ingredient.name.capitalize()} добавлен", 0.5)

            elif self.current_order and self.current_order.order_type == "drink":
                for drink_name in DRINKS_PER_LEVEL[min(self.level - 1, 6)]:
                    if drink_name in self.ingredients:
                        button = IngredientButton(self.ingredients[drink_name],
                                                   INGREDIENT_BUTTONS_X,
                                                   INGREDIENT_BUTTONS_Y_START - 
                                                   DRINKS_PER_LEVEL[min(self.level - 1, 6)].index(drink_name) * INGREDIENT_BUTTON_SPACING)
                        if button.is_clicked(x, y):
                            if self.drink.set_drink_type(drink_name):
                                self.selected_drink_type = drink_name
                                self.message_display.show_message(f"Выбран {drink_name.capitalize()}", 1)

                if self.ui_elements["drink_machine_button"].is_clicked(x, y):
                    if self.drink.state == DRINK_STATE_FILLING:
                        if self.drink.finish_filling():
                            self.message_display.show_message("Напиток наполнен!", 2)
                    elif self.drink.state == DRINK_STATE_EMPTY and self.selected_drink_type:
                        if self.drink.set_drink_type(self.selected_drink_type):
                            self.message_display.show_message("Наполнение начато!", 1)

                elif self.ui_elements["ice_button"].is_clicked(x, y):
                    if self.drink.add_ice():
                        self.message_display.show_message("Лед добавлен!", 1)

                elif self.ui_elements["submit_button"].is_clicked(x, y):
                    if self.drink.state == DRINK_STATE_COMPLETE and self.order_active:
                        success, feedback, score = self.current_order.check_drink(self.drink)
                        patience_check = self.customer.leave()

                        if success:
                            self.money += self.current_order.reward
                            self.customers_served += 1
                            if score >= 90:
                                self.message_display.show_message(f"ИДЕАЛЬНО! +${self.current_order.reward}", 3)
                            elif score >= 80:
                                self.message_display.show_message(f"Отлично! +${self.current_order.reward}", 3)
                            else:
                                self.message_display.show_message(f"Хорошо! +${self.current_order.reward}", 3)
                        else:
                            self.money -= self.current_order.penalty
                            self.message_display.show_message(f"Не принято: {feedback} -${self.current_order.penalty}", 3)

                        self.start_new_order()

            else:
                if self.current_order and self.current_order.order_type == "pizza":
                    for ing_button in self.ingredient_buttons:
                        if ing_button.is_clicked(x, y) and ing_button.is_active:
                            self.selected_ingredient = ing_button.ingredient
                            self.cut_mode = False
                            self.message_display.show_message(f"Выбран {ing_button.ingredient.name.capitalize()}", 1)

                    if self.selected_ingredient and not self.cut_mode:
                        distance_to_pizza = math.sqrt((x - PIZZA_X) ** 2 + (y - PIZZA_Y) ** 2)
                        if distance_to_pizza < PIZZA_RADIUS:
                            if self.pizza.add_ingredient(self.selected_ingredient.name,
                                                         x - PIZZA_X, y - PIZZA_Y):
                                self.money -= self.selected_ingredient.price
                                self.message_display.show_message(f"{self.selected_ingredient.name.capitalize()} добавлен",
                                                                  0.5)

        elif self.game_state == "level_complete":
            if self.ui_elements["continue_button"].is_clicked(x, y):
                self.game_state = "game"
                self.update_ui_visibility()
                self.create_ingredients()
                self.setup()
            elif self.ui_elements["restart_button"].is_clicked(x, y):
                self.restart_game()

        elif self.game_state == "game_over":
            if self.ui_elements["restart_button"].is_clicked(x, y):
                self.restart_game()
            elif self.ui_elements["exit_button"].is_clicked(x, y):
                arcade.close_window()

        elif self.game_state == "game_complete":
            if self.ui_elements["restart_button"].is_clicked(x, y):
                self.restart_game()
            elif self.ui_elements["exit_button"].is_clicked(x, y):
                arcade.close_window()

    def on_mouse_release(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.game_state == "game" and self.is_cutting:
            if self.cut_start:
                pizza_x1 = self.cut_start[0] - PIZZA_X
                pizza_y1 = self.cut_start[1] - PIZZA_Y
                pizza_x2 = x - PIZZA_X
                pizza_y2 = y - PIZZA_Y

                if self.pizza.add_cut(pizza_x1, pizza_y1, pizza_x2, pizza_y2):
                    cuts_left = 4 - len(self.pizza.cut_lines)
                    if cuts_left > 0:
                        self.message_display.show_message(f"Линия разреза добавлена. Осталось: {cuts_left}", 1)
                    else:
                        self.message_display.show_message("Пицца разрезана на 8 кусочков!", 2)
                        self.cut_mode = False

            self.is_cutting = False
            self.cut_start = None
            self.cut_end = None

    def restart_game(self):
        self.level = 1
        self.money = 0
        self.money_target = LEVEL_MONEY_TARGETS[0]
        self.customers_served = 0
        self.customers_target = LEVEL_CUSTOMER_COUNTS[0]
        self.level_time_left = LEVEL_TIME_LIMITS[0]

        self.game_state = "game"
        self.game_over_reason = ""
        self.update_ui_visibility()
        self.setup()

    def start_new_order(self):
        self.pizza = Pizza()
        self.burger = Burger()
        self.drink = Drink()
        self.selected_ingredient = None
        self.selected_drink_type = None
        self.cut_mode = False
        self.is_cutting = False
        self.cut_start = None
        self.cut_end = None

        if len(self.order_queue) > 0:
            self.current_order = self.order_queue.pop(0)
            self.order_active = False
        else:
            try:
                self.current_order = Order(self.level)
                self.current_order.load_from_file("requests.json")
            except:
                self.current_order = Order(self.level)
            self.order_active = False

        if self.current_order:
            self.order_timer = self.current_order.time_limit
            self.customer.set_customer(self.level, self.current_order.customer_name, self.current_order.customer_mood)

            if random.random() < 0.3 and self.level > 2:
                for _ in range(random.randint(1, 2)):
                    try:
                        new_order = Order(self.level)
                        new_order.load_from_file("requests.json")
                    except:
                        new_order = Order(self.level)
                    if len(self.order_queue) < 3:
                        self.order_queue.append(new_order)
            self.update_ui_visibility()