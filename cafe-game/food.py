import arcade
from utils import load_texture


class FoodItem:
    def __init__(self, name, texture_path, position, scale=0.6):
        self.name = name
        self.texture = load_texture(texture_path)  # Исправлено: добавлен аргумент texture_path
        self.sprite = arcade.Sprite(texture_path, scale)
        self.sprite.center_x = position[0]
        self.sprite.center_y = position[1]
        self.is_prepared = False
        self.preparation_time = 0
        self.preparation_progress = 0

    def start_preparing(self, time_required):
        self.is_prepared = False
        self.preparation_time = time_required
        self.preparation_progress = 0

    def update(self, delta_time):
        if not self.is_prepared and self.preparation_time > 0:
            self.preparation_progress += delta_time
            if self.preparation_progress >= self.preparation_time:
                self.is_prepared = True
                arcade.play_sound(arcade.load_sound("sounds/cooking_sound.wav"))

    def draw(self):
        self.sprite.draw()
        if not self.is_prepared and self.preparation_time > 0:
            progress = self.preparation_progress / self.preparation_time
            width = self.sprite.width * progress
            arcade.draw_rectangle_filled(
                self.sprite.center_x - self.sprite.width / 2 + width / 2,
                self.sprite.center_y - self.sprite.height / 2 - 15,
                width, 8,
                arcade.color.GREEN
            )
            arcade.draw_rectangle_outline(
                self.sprite.center_x - self.sprite.width / 2 + self.sprite.width / 2,
                self.sprite.center_y - self.sprite.height / 2 - 15,
                self.sprite.width, 8,
                arcade.color.BLACK
            )


class FoodManager:
    def __init__(self, game):
        self.game = game
        self.inventory = {}
        self.selected_ingredient = None
        self.burger_assembly = []
        self.fries = FoodItem("fries", "images/fries_raw.png", (450, 450))
        self.icecream = None
        self.drink = None
        self.equipped_items = {}
        self.setup_inventory()

    def setup_inventory(self):
        ingredients = [
            ("burger_base", "images/burger_base.png", (100, 600)),
            ("burger_patty", "images/burger_patty.png", (100, 500)),
            ("burger_cheese", "images/burger_cheese.png", (100, 400)),
            ("burger_lettuce", "images/burger_lettuce.png", (100, 300)),
            ("burger_tomato", "images/burger_tomato.png", (100, 200)),
            ("burger_sauce", "images/burger_sauce.png", (100, 100)),
            ("burger_top", "images/burger_top.png", (200, 600)),
            ("fries", "images/fries_raw.png", (200, 500)),
            ("icecream_vanilla", "images/icecream_vanilla.png", (200, 400)),
            ("icecream_chocolate", "images/icecream_chocolate.png", (200, 300)),
            ("icecream_strawberry", "images/icecream_strawberry.png", (200, 200)),
            ("drink_cola", "images/cup_cola.png", (300, 600)),
            ("drink_sprite", "images/cup_sprite.png", (300, 500)),
            ("drink_water", "images/cup_water.png", (300, 400)),
        ]

        for name, path, position in ingredients:
            item = FoodItem(name, path, position, 0.4)
            item.sprite.center_x = position[0]
            item.sprite.center_y = position[1]
            self.inventory[name] = item

    def reset_inventory(self):
        self.burger_assembly = []
        self.fries = FoodItem("fries", "images/fries_raw.png", (450, 450))
        self.icecream = None
        self.drink = None
        self.equipped_items = {}

    def select_ingredient(self, category):
        if category == "burger":
            self.selected_ingredient = "burger_base"
        elif category == "fries":
            self.start_cooking_fries()
        elif category == "icecream":
            self.selected_ingredient = "icecream_vanilla"
        elif category == "drink":
            self.selected_ingredient = "drink_cola"

    def start_cooking_fries(self):
        self.fries = FoodItem("fries", "images/fries_raw.png", (550, 450))
        self.fries.start_preparing(3.0)

    def add_burger_ingredient(self, ingredient):
        if ingredient == "burger_base" and not self.burger_assembly:
            self.burger_assembly.append("base")
        elif self.burger_assembly and ingredient.startswith("burger_"):
            if ingredient == "burger_patty":
                self.burger_assembly.append("patty")
            elif ingredient == "burger_cheese":
                self.burger_assembly.append("cheese")
            elif ingredient == "burger_lettuce":
                self.burger_assembly.append("lettuce")
            elif ingredient == "burger_tomato":
                self.burger_assembly.append("tomato")
            elif ingredient == "burger_sauce":
                self.burger_assembly.append("sauce")
            elif ingredient == "burger_top" and len(self.burger_assembly) > 1:
                self.burger_assembly.append("top")

    def prepare_icecream(self, flavor):
        self.icecream = FoodItem(flavor, f"images/icecream_{flavor}.png", (650, 450))
        self.icecream.is_prepared = True

    def prepare_drink(self, drink_type):
        self.drink = FoodItem(drink_type, f"images/cup_{drink_type}.png", (750, 450))
        self.drink.is_prepared = True

    def check_equipment_click(self, x, y):
        for item in self.inventory.values():
            if (abs(x - item.sprite.center_x) < 30 and
                    abs(y - item.sprite.center_y) < 30):
                if "burger" in item.name:
                    self.add_burger_ingredient(item.name)
                elif "fries" in item.name:
                    self.start_cooking_fries()
                elif "icecream" in item.name:
                    self.prepare_icecream(item.name.split("_")[1])
                elif "drink" in item.name:
                    self.prepare_drink(item.name.split("_")[1])
                return

        equipment_areas = [
            (450, 320, 150, 150, "grill"),
            (550, 320, 150, 150, "fryer"),
            (650, 320, 150, 150, "ice_cream_machine"),
            (750, 320, 150, 150, "soda_tap")
        ]

        for area in equipment_areas:
            if (area[0] - area[2] / 2 < x < area[0] + area[2] / 2 and
                    area[1] - area[3] / 2 < y < area[1] + area[3] / 2):
                if area[4] == "grill" and self.burger_assembly:
                    self.equipped_items["burger"] = self.burger_assembly.copy()
                    self.burger_assembly = []
                elif area[4] == "fryer" and self.fries.is_prepared:
                    self.equipped_items["fries"] = "cooked"
                return

    def get_prepared_items(self):
        items = {}
        if "burger" in self.equipped_items:
            items["burger"] = self.equipped_items["burger"]
        if "fries" in self.equipped_items:
            items["fries"] = True
        if self.icecream and self.icecream.is_prepared:
            items["icecream"] = self.icecream.name
        if self.drink and self.drink.is_prepared:
            items["drink"] = self.drink.name
        return items

    def update(self, delta_time):
        self.fries.update(delta_time)
        if self.icecream:
            self.icecream.update(delta_time)
        if self.drink:
            self.drink.update(delta_time)

    def draw(self):
        for item in self.inventory.values():
            item.draw()

        self.fries.draw()
        if self.icecream:
            self.icecream.draw()
        if self.drink:
            self.drink.draw()

        if self.burger_assembly:
            y_pos = 450
            for ingredient in self.burger_assembly:
                texture_path = f"images/burger_{ingredient}.png"
                if ingredient == "base":
                    texture_path = "images/burger_base.png"
                elif ingredient == "top":
                    texture_path = "images/burger_top.png"

                texture = load_texture(texture_path)
                arcade.draw_texture_rectangle(450, y_pos, 80, 80, texture)
                y_pos += 40