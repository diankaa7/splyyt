import arcade

from constants import *


class Ingredient:
    def __init__(self, name, price, color, texture=None):
        self.name = name
        self.price = price
        self.color = color
        self.texture = texture
        self.count = 0
        self.available = True

    def draw(self, x, y):
        if not self.available:
            arcade.draw_rectangle_filled(x, y, 150, 40, (100, 100, 100, 200))
            color = (150, 150, 150)
        else:
            color = self.color

        if self.texture:
            arcade.draw_texture_rectangle(
                x - 60, y, 30, 30, self.texture)
        else:
            arcade.draw_circle_filled(x - 60, y, 15, color)

        name_text = self.name.capitalize()
        if not self.available:
            name_text = f"{name_text} (LOCKED)"

        arcade.draw_text(
            name_text, x - 30, y, TEXT_COLOR_DARK, 16,
            anchor_x="left", anchor_y="center")
        arcade.draw_text(
            f"${self.price}", x + 50, y, TEXT_COLOR_DARK, 16,
            anchor_x="center", anchor_y="center")

    def draw_on_pizza(self, x, y):
        if self.texture:
            arcade.draw_texture_rectangle(
                x, y, INGREDIENT_SIZE, INGREDIENT_SIZE, self.texture)
        else:
            arcade.draw_circle_filled(x, y, INGREDIENT_SIZE // 2, self.color)


class IngredientButton:
    def __init__(self, ingredient, x, y, width=150, height=40):
        self.ingredient = ingredient
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_hovered = False
        self.is_active = True

    def draw(self):
        if not self.is_active:
            arcade.draw_rectangle_filled(
                self.x, self.y, self.width, self.height, (100, 100, 100, 200))
            color = (150, 150, 150)
        elif self.is_hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, color)

        if self.ingredient.texture:
            arcade.draw_texture_rectangle(
                self.x - 50, self.y, 30, 30, self.ingredient.texture)
        else:
            arcade.draw_circle_filled(
                self.x - 50, self.y, 15, self.ingredient.color)

        name_text = self.ingredient.name.capitalize()
        if not self.is_active:
            name_text = f"{name_text} (LOCKED)"

        arcade.draw_text(
            name_text, self.x - 30, self.y, TEXT_COLOR, 16,
            anchor_x="left", anchor_y="center")
        arcade.draw_text(
            f"${self.ingredient.price}", self.x + 40, self.y, TEXT_COLOR, 16,
            anchor_x="center", anchor_y="center")

    def check_hover(self, mouse_x, mouse_y):
        if not self.is_active:
            self.is_hovered = False
            return False

        self.is_hovered = (
                abs(mouse_x - self.x) < self.width / 2 and
                abs(mouse_y - self.y) < self.height / 2
        )
        return self.is_hovered

    def is_clicked(self, mouse_x, mouse_y):
        if not self.is_active:
            return False

        return (
                abs(mouse_x - self.x) < self.width / 2 and
                abs(mouse_y - self.y) < self.height / 2
        )