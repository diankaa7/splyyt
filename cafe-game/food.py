import os
import arcade
from utils import load_texture, get_texture_display_size

# Русские названия ингредиентов для отображения
INGREDIENT_NAMES_RU = {
    "burger_base": "Низ булки",
    "burger_patty": "Котлета",
    "burger_cheese": "Сыр",
    "burger_top": "Верх булки",
    "fries": "Картошка",
    "icecream_default": "Мороженое ваниль",
    "icecream_chocolate": "Мороженое шоколад",
    "drink_cola": "Кола",
    "drink_water": "Вода",
}


class FoodItem:
    # Целевой размер отрисовки ингредиента (любое разрешение картинки масштабируется под него)
    DEFAULT_DISPLAY_SIZE = 64

    def __init__(self, name, texture_path, position, scale=0.6, display_size=None):
        self.name = name
        self.texture = load_texture(texture_path)
        self.center_x = position[0]
        self.center_y = position[1]
        target = display_size if display_size is not None else self.DEFAULT_DISPLAY_SIZE
        self.width, self.height = get_texture_display_size(self.texture, target, target)
        # Для обратной совместимости: scale дополнительно уменьшает/увеличивает
        if scale != 1.0:
            self.width = max(1, int(self.width * scale))
            self.height = max(1, int(self.height * scale))
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
                arcade.play_sound(arcade.load_sound("sounds/cooking.wav"))

    def draw(self):
        # Draw background rectangle for visibility (more prominent)
        bg_rect = arcade.types.XYWH(self.center_x, self.center_y, self.width + 20, self.height + 20)
        arcade.draw_rect_filled(bg_rect, arcade.color.LIGHT_BLUE)
        arcade.draw_rect_outline(bg_rect, arcade.color.DARK_BLUE, 3)
        
        # Draw the item texture
        rect = arcade.types.XYWH(self.center_x, self.center_y, self.width, self.height)
        arcade.draw_texture_rect(self.texture, rect)
        
        # Draw label below the item (more visible)
        label = INGREDIENT_NAMES_RU.get(self.name, self.name.replace("_", " ").title())
        arcade.draw_text(
            label,
            self.center_x, self.center_y - self.height / 2 - 20,
            arcade.color.DARK_BLUE, 14, anchor_x="center", anchor_y="top", bold=True
        )
        
        if not self.is_prepared and self.preparation_time > 0:
            progress = self.preparation_progress / self.preparation_time
            width = self.width * progress
            bar_x = self.center_x - self.width / 2 + width / 2
            bar_y = self.center_y - self.height / 2 - 30
            filled_rect = arcade.types.XYWH(bar_x, bar_y, width, 8)
            outline_rect = arcade.types.XYWH(self.center_x, bar_y, self.width, 8)
            arcade.draw_rect_filled(filled_rect, arcade.color.GREEN)
            arcade.draw_rect_outline(outline_rect, arcade.color.BLACK)


class FoodManager:
    # Позиции ингредиентов в окне кухни (подальше друг от друга). Используются для отрисовки и для проверки кликов.
    COOKING_VIEW_POSITIONS = [
        ("burger_base", (120, 520)),
        ("burger_patty", (240, 520)),
        ("burger_cheese", (360, 520)),
        ("burger_top", (480, 520)),
        ("fries", (120, 400)),
        ("icecream_default", (240, 400)),
        ("icecream_chocolate", (360, 400)),
        ("drink_cola", (480, 400)),
        ("drink_water", (600, 400)),
    ]
    # Радиус клика по ингредиенту (пиксели)
    INGREDIENT_CLICK_RADIUS = 50

    # Оборудование в окне кухни: (center_x, center_y, width, height, id) — интервал 160px, чтобы кнопки не накладывались
    EQUIPMENT_AREAS = [
        (400, 280, 140, 140, "grill"),
        (560, 280, 140, 140, "fryer"),
        (720, 280, 140, 140, "ice_cream_machine"),
        (880, 280, 140, 140, "soda_tap"),
    ]
    # Панель «Готово к подаче»: центр X, верх Y, ширина, высота строки, размер кнопки [X]
    PREPARED_PANEL_CX = 1200
    PREPARED_PANEL_TOP = 520
    PREPARED_PANEL_WIDTH = 220
    PREPARED_ROW_HEIGHT = 48
    PREPARED_REMOVE_BUTTON_HALF = 14

    def __init__(self, game):
        self.game = game
        self.inventory = {}
        self.selected_ingredient = None
        self.burger_assembly = []
        self.fries = FoodItem("fries", "images/fries_raw.png", (540, 400))
        self.icecream = None
        self.drink = None
        self.equipped_items = {}
        self.setup_inventory()

    def setup_inventory(self):
        # Position ingredients in bottom-left area, organized in rows
        # Row 1 (top): burger ingredients; Row 2: fries, ice cream, drinks
        ingredients = [
            ("burger_base", "images/burger_base.png", (70, 140)),
            ("burger_patty", "images/burger_patty.png", (140, 140)),
            ("burger_cheese", "images/burger_cheese.png", (210, 140)),
            ("burger_top", "images/burger_top.png", (280, 140)),
            ("fries", "images/fries_raw.png", (70, 80)),
            ("icecream_default", "images/icecream_default.png", (140, 80)),
            ("icecream_chocolate", "images/icecream_default.png", (210, 80)),
            ("drink_cola", "images/cup_cola.png", (280, 80)),
            ("drink_water", "images/cup_cola.png", (350, 80)),
        ]

        for name, path, position in ingredients:
            item = FoodItem(name, path, position, 0.6)  # Increased scale for better visibility
            item.center_x = position[0]
            item.center_y = position[1]
            self.inventory[name] = item

    def reset_inventory(self):
        self.burger_assembly = []
        self.fries = FoodItem("fries", "images/fries_raw.png", (540, 400))
        self.icecream = None
        self.drink = None
        self.equipped_items = {}
        # Ensure we are back in the main gameplay frame
        self.game.show_cooking_frame = False

    def select_ingredient(self, category):
        if category == "burger":
            self.selected_ingredient = "burger_base"
        elif category == "fries":
            self.start_cooking_fries()
        elif category == "icecream":
            self.selected_ingredient = "icecream_default"
        elif category == "drink":
            self.selected_ingredient = "drink_cola"

    def start_cooking_fries(self):
        self.fries = FoodItem("fries", "images/fries_raw.png", (540, 400))
        self.fries.start_preparing(3.0)
        # Switch to dedicated cooking frame while fries are preparing
        self.game.show_cooking_frame = True

    def add_burger_ingredient(self, ingredient):
        if ingredient == "burger_base" and not self.burger_assembly:
            self.burger_assembly.append("base")
        elif self.burger_assembly and ingredient.startswith("burger_"):
            if ingredient == "burger_patty":
                self.burger_assembly.append("patty")
            elif ingredient == "burger_cheese":
                self.burger_assembly.append("cheese")
            elif ingredient == "burger_top" and len(self.burger_assembly) > 1:
                self.burger_assembly.append("top")

    def prepare_icecream(self, flavor="default"):
        self.icecream = FoodItem(flavor, "images/icecream_default.png", (700, 400))
        self.icecream.is_prepared = True

    def prepare_drink(self, drink_type="cola"):
        self.drink = FoodItem(drink_type, "images/cup_cola.png", (860, 400))
        self.drink.is_prepared = True

    def check_prepared_panel_click(self, x, y):
        """Обработка клика по панели «Готово к подаче» (удаление пункта). Возвращает True если клик обработан."""
        lst = self.get_prepared_list()
        if not lst:
            return False
        cx, top, width, row_h, rh = (
            self.PREPARED_PANEL_CX, self.PREPARED_PANEL_TOP, self.PREPARED_PANEL_WIDTH,
            self.PREPARED_ROW_HEIGHT, self.PREPARED_REMOVE_BUTTON_HALF
        )
        remove_center_x = cx + width // 2 - rh - 8
        for i, (key, _) in enumerate(lst):
            row_y = top - 70 - i * row_h
            if (remove_center_x - rh <= x <= remove_center_x + rh and
                    row_y - rh <= y <= row_y + rh):
                self.remove_from_prepared(key)
                return True
        return False

    def _draw_complete_burger(self, center_x, center_y, size=70, assembly=None):
        """Рисует собранный бургер: если есть images/burger_complete.png — одна картинка, иначе слои друг на друге."""
        complete_path = "images/burger_complete.png"
        if os.path.exists(complete_path):
            tex = load_texture(complete_path)
            rect = arcade.types.XYWH(center_x, center_y, size, size)
            arcade.draw_texture_rect(tex, rect)
            return
        layers = assembly if assembly is not None else ["base", "patty", "cheese", "top"]
        y_off = size * 0.12
        for i, layer in enumerate(layers):
            path = "images/burger_base.png" if layer == "base" else "images/burger_top.png" if layer == "top" else f"images/burger_{layer}.png"
            tex = load_texture(path)
            y = center_y - i * y_off
            rect = arcade.types.XYWH(center_x, y, size, size)
            arcade.draw_texture_rect(tex, rect)

    def check_equipment_click(self, x, y):
        if self.check_prepared_panel_click(x, y):
            return
        # Проверка клика по ингредиентам — используем позиции из окна кухни
        r = self.INGREDIENT_CLICK_RADIUS
        for name, (cx, cy) in self.COOKING_VIEW_POSITIONS:
            if name not in self.inventory:
                continue
            if abs(x - cx) <= r and abs(y - cy) <= r:
                item = self.inventory[name]
                if "burger" in item.name:
                    self.add_burger_ingredient(item.name)
                elif "fries" in item.name:
                    self.start_cooking_fries()
                elif "icecream" in item.name:
                    flavor = "chocolate" if "chocolate" in item.name else "default"
                    self.prepare_icecream(flavor)
                elif "drink" in item.name:
                    drink_type = "water" if "water" in item.name else "cola"
                    self.prepare_drink(drink_type)
                return

        # Проверка клика по оборудованию
        for area in self.EQUIPMENT_AREAS:
            ax, ay, aw, ah, aid = area
            if (ax - aw / 2 <= x <= ax + aw / 2 and
                    ay - ah / 2 <= y <= ay + ah / 2):
                if aid == "grill" and self.burger_assembly:
                    self.equipped_items["burger"] = self.burger_assembly.copy()
                    self.burger_assembly = []
                elif aid == "fryer":
                    if self.fries.is_prepared:
                        self.equipped_items["fries"] = "cooked"
                        self.fries = FoodItem("fries", "images/fries_raw.png", (540, 400))
                    elif self.fries.preparation_time == 0:
                        self.start_cooking_fries()
                elif aid == "ice_cream_machine":
                    self.prepare_icecream("default")
                elif aid == "soda_tap":
                    self.prepare_drink("cola")
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

    def get_prepared_list(self):
        """Список (key, label) для отображения в панели «Готово к подаче»."""
        result = []
        if "burger" in self.equipped_items:
            result.append(("burger", "Бургер"))
        if "fries" in self.equipped_items:
            result.append(("fries", "Картошка"))
        if self.icecream and self.icecream.is_prepared:
            ice_label = "Мороженое шоколад" if self.icecream.name == "chocolate" else "Мороженое ваниль"
            result.append(("icecream", ice_label))
        if self.drink and self.drink.is_prepared:
            drink_label = "Вода" if self.drink.name == "water" else "Кола"
            result.append(("drink", drink_label))
        return result

    def remove_from_prepared(self, key):
        """Убрать блюдо из списка приготовленного."""
        if key == "burger" and "burger" in self.equipped_items:
            del self.equipped_items["burger"]
        elif key == "fries" and "fries" in self.equipped_items:
            del self.equipped_items["fries"]
        elif key == "icecream" and self.icecream:
            self.icecream = None
        elif key == "drink" and self.drink:
            self.drink = None

    def _is_burger_complete(self):
        """Бургер собран полностью (есть база, минимум один слой и верх)."""
        a = self.burger_assembly
        return len(a) >= 2 and a[0] == "base" and a[-1] == "top"

    def update(self, delta_time):
        self.fries.update(delta_time)
        # Don't auto-exit cooking frame - let user stay in kitchen
        if self.icecream:
            self.icecream.update(delta_time)
        if self.drink:
            self.drink.update(delta_time)

    def draw(self):
        # Draw inventory panel background (bottom-left area, wider)
        inventory_bg = arcade.types.XYWH(200, 110, 360, 90)
        arcade.draw_rect_filled(inventory_bg, (200, 200, 200, 240))
        arcade.draw_rect_outline(inventory_bg, arcade.color.BLACK, 3)
        
        # Draw title
        arcade.draw_text(
            "ИНГРЕДИЕНТЫ (нажмите для использования)",
            200, 180,
            arcade.color.BLACK, 15, anchor_x="center", bold=True
        )
        
        # Draw inventory items
        for item in self.inventory.values():
            item.draw()

        # Draw equipment labels with backgrounds for visibility (below equipment)
        equipment_labels = [
            (400, 200, "ГРИЛЬ\n(Бургер)"),
            (560, 200, "ФРИТЮР\n(Картошка)"),
            (720, 200, "МОРОЖЕНОЕ"),
            (880, 200, "НАПИТКИ")
        ]
        for x, y, label in equipment_labels:
            # Draw background for text
            text_bg = arcade.types.XYWH(x, y, 110, 35)
            arcade.draw_rect_filled(text_bg, (0, 0, 0, 200))
            arcade.draw_rect_outline(text_bg, arcade.color.YELLOW, 2)
            
            # Draw text
            lines = label.split('\n')
            for i, line in enumerate(lines):
                arcade.draw_text(
                    line,
                    x, y + 10 - i * 15,
                    arcade.color.YELLOW, 13, anchor_x="center",
                    bold=True
                )

        self.fries.draw()
        if self.icecream:
            self.icecream.draw()
        if self.drink:
            self.drink.draw()

        if self.burger_assembly:
            # Draw burger assembly area (center-left, above equipment, выше)
            assembly_bg = arcade.types.XYWH(400, 580, 120, 120)
            arcade.draw_rect_filled(assembly_bg, (255, 255, 200, 200))
            arcade.draw_rect_outline(assembly_bg, arcade.color.BROWN, 2)
            
            arcade.draw_text(
                "БУРГЕР:",
                400, 630,
                arcade.color.BLACK, 14, anchor_x="center", bold=True
            )
            if self._is_burger_complete():
                self._draw_complete_burger(400, 550, 70)
            else:
                y_pos = 600
                for ingredient in self.burger_assembly:
                    texture_path = f"images/burger_{ingredient}.png"
                    if ingredient == "base":
                        texture_path = "images/burger_base.png"
                    elif ingredient == "top":
                        texture_path = "images/burger_top.png"
                    texture = load_texture(texture_path)
                    rect = arcade.types.XYWH(400, y_pos, 60, 60)
                    arcade.draw_texture_rect(texture, rect)
                    y_pos -= 30

    def draw_cooking_view(self):
        """Draw cooking view with all ingredients and equipment visible."""
        # Draw inventory panel background (left side, larger for cooking view)
        inventory_bg = arcade.types.XYWH(380, 460, 520, 160)
        arcade.draw_rect_filled(inventory_bg, (200, 200, 200, 250))
        arcade.draw_rect_outline(inventory_bg, arcade.color.BLACK, 3)
        
        # Draw title
        arcade.draw_text(
            "ИНГРЕДИЕНТЫ",
            380, 540,
            arcade.color.BLACK, 20, anchor_x="center", bold=True
        )
        arcade.draw_text(
            "(нажмите для использования)",
            380, 515,
            arcade.color.DARK_GRAY, 14, anchor_x="center"
        )
        
        # Draw inventory items (repositioned for cooking view)
        for name, pos in self.COOKING_VIEW_POSITIONS:
            if name in self.inventory:
                item = self.inventory[name]
                # Temporarily save original position
                orig_x, orig_y = item.center_x, item.center_y
                # Set cooking view position
                item.center_x, item.center_y = pos
                item.draw()
                # Restore original position
                item.center_x, item.center_y = orig_x, orig_y

        # Draw current cooking items (near equipment) — позиции совпадают с EQUIPMENT_AREAS
        fryer_x, ice_x, drink_x = 560, 720, 880
        zone_y, zone_h = 280, 80

        # Fries (fryer)
        fries_bg = arcade.types.XYWH(fryer_x, zone_y - 20, 140, 100)
        arcade.draw_rect_filled(fries_bg, (100, 100, 100, 220))
        arcade.draw_rect_outline(fries_bg, arcade.color.ORANGE, 2)
        orig_fries_x, orig_fries_y = self.fries.center_x, self.fries.center_y
        self.fries.center_x, self.fries.center_y = fryer_x, zone_y
        self.fries.draw()
        self.fries.center_x, self.fries.center_y = orig_fries_x, orig_fries_y
        if self.fries.preparation_time > 0:
            progress = min(1.0, self.fries.preparation_progress / self.fries.preparation_time)
            arcade.draw_text(f"Картошка: {int(progress * 100)}%", fryer_x, zone_y - 60, arcade.color.YELLOW, 16, anchor_x="center", bold=True)
        elif self.fries.is_prepared:
            arcade.draw_text("Картошка: готово!", fryer_x, zone_y - 60, arcade.color.GREEN, 16, anchor_x="center", bold=True)
        else:
            arcade.draw_text("Нажмите фритюр для старта", fryer_x, zone_y - 60, arcade.color.WHITE, 14, anchor_x="center")

        # Ice cream
        icecream_bg = arcade.types.XYWH(ice_x, zone_y - 20, 140, 100)
        arcade.draw_rect_filled(icecream_bg, (200, 200, 255, 200))
        arcade.draw_rect_outline(icecream_bg, arcade.color.BLUE, 2)
        if self.icecream:
            orig_ice_x, orig_ice_y = self.icecream.center_x, self.icecream.center_y
            self.icecream.center_x, self.icecream.center_y = ice_x, zone_y
            self.icecream.draw()
            self.icecream.center_x, self.icecream.center_y = orig_ice_x, orig_ice_y
            arcade.draw_text("Готово", ice_x, zone_y - 60, arcade.color.GREEN, 14, anchor_x="center", bold=True)
        else:
            arcade.draw_text("Нажмите мороженое", ice_x, zone_y - 30, arcade.color.BLUE, 14, anchor_x="center")
            arcade.draw_text("для приготовления", ice_x, zone_y - 48, arcade.color.BLUE, 12, anchor_x="center")

        # Drink
        drink_bg = arcade.types.XYWH(drink_x, zone_y - 20, 140, 100)
        arcade.draw_rect_filled(drink_bg, (200, 255, 200, 200))
        arcade.draw_rect_outline(drink_bg, arcade.color.GREEN, 2)
        if self.drink:
            orig_drink_x, orig_drink_y = self.drink.center_x, self.drink.center_y
            self.drink.center_x, self.drink.center_y = drink_x, zone_y
            self.drink.draw()
            self.drink.center_x, self.drink.center_y = orig_drink_x, orig_drink_y
            arcade.draw_text("Готово", drink_x, zone_y - 60, arcade.color.GREEN, 14, anchor_x="center", bold=True)
        else:
            arcade.draw_text("Нажмите напиток", drink_x, zone_y - 30, arcade.color.GREEN, 14, anchor_x="center")
            arcade.draw_text("для приготовления", drink_x, zone_y - 48, arcade.color.GREEN, 12, anchor_x="center")

        # Draw burger assembly area (над грилем, выше). Собранный бургер — одна картинка burger_complete.png
        grill_x = 400
        if self.burger_assembly:
            assembly_bg = arcade.types.XYWH(grill_x, 580, 150, 150)
            arcade.draw_rect_filled(assembly_bg, (255, 255, 200, 220))
            arcade.draw_rect_outline(assembly_bg, arcade.color.BROWN, 3)
            arcade.draw_text("СБОРКА БУРГЕРА:", grill_x, 640, arcade.color.BLACK, 16, anchor_x="center", bold=True)
            if self._is_burger_complete():
                self._draw_complete_burger(grill_x, 560, 80)
            else:
                y_pos = 610
                for ingredient in self.burger_assembly:
                    texture_path = f"images/burger_{ingredient}.png"
                    if ingredient == "base":
                        texture_path = "images/burger_base.png"
                    elif ingredient == "top":
                        texture_path = "images/burger_top.png"
                    texture = load_texture(texture_path)
                    rect = arcade.types.XYWH(grill_x, y_pos, 70, 70)
                    arcade.draw_texture_rect(texture, rect)
                    y_pos -= 35

        # Панель «Готово к подаче» — полный список и кнопки убрать
        cx, top, width, row_h = self.PREPARED_PANEL_CX, self.PREPARED_PANEL_TOP, self.PREPARED_PANEL_WIDTH, self.PREPARED_ROW_HEIGHT
        lst = self.get_prepared_list()
        panel_h = max(80, len(lst) * row_h + 50)
        panel_rect = arcade.types.XYWH(cx, top - panel_h // 2, width, panel_h)
        arcade.draw_rect_filled(panel_rect, (60, 80, 60, 240))
        arcade.draw_rect_outline(panel_rect, arcade.color.GREEN, 2)
        arcade.draw_text("ГОТОВО К ПОДАЧЕ", cx, top - 28, arcade.color.WHITE, 18, anchor_x="center", bold=True)
        arcade.draw_text("(нажмите [X] чтобы убрать)", cx, top - 50, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        remove_cx = cx + width // 2 - self.PREPARED_REMOVE_BUTTON_HALF - 8
        rh = self.PREPARED_REMOVE_BUTTON_HALF
        for i, (key, label) in enumerate(lst):
            row_y = top - 70 - i * row_h
            arcade.draw_text(label, cx - width // 2 + 40, row_y, arcade.color.WHITE, 16, anchor_x="left", anchor_y="center")
            if key == "burger":
                self._draw_complete_burger(cx - width // 2 + 25, row_y, 36, assembly=self.equipped_items.get("burger"))
            elif key == "fries":
                tex = load_texture("images/fries_raw.png")
                arcade.draw_texture_rect(tex, arcade.types.XYWH(cx - width // 2 + 25, row_y, 36, 36))
            elif key == "icecream" and self.icecream:
                orig_x, orig_y = self.icecream.center_x, self.icecream.center_y
                self.icecream.center_x, self.icecream.center_y = cx - width // 2 + 25, row_y
                r2 = arcade.types.XYWH(self.icecream.center_x, self.icecream.center_y, 32, 32)
                arcade.draw_texture_rect(self.icecream.texture, r2)
                self.icecream.center_x, self.icecream.center_y = orig_x, orig_y
            elif key == "drink" and self.drink:
                orig_x, orig_y = self.drink.center_x, self.drink.center_y
                self.drink.center_x, self.drink.center_y = cx - width // 2 + 25, row_y
                r2 = arcade.types.XYWH(self.drink.center_x, self.drink.center_y, 32, 32)
                arcade.draw_texture_rect(self.drink.texture, r2)
                self.drink.center_x, self.drink.center_y = orig_x, orig_y
            remove_rect = arcade.types.XYWH(remove_cx, row_y, rh * 2, rh * 2)
            arcade.draw_rect_filled(remove_rect, arcade.color.DARK_RED)
            arcade.draw_rect_outline(remove_rect, arcade.color.WHITE, 2)
            arcade.draw_text("X", remove_cx, row_y, arcade.color.WHITE, 14, anchor_x="center", anchor_y="center", bold=True)