import arcade
from utils import get_texture_display_size


class Chef:
    def __init__(self, center_x: float, center_y: float, texture=None):
        self.center_x = center_x
        self.center_y = center_y
        self.texture = texture

        self.body_width = 120
        self.body_height = 150
        self.head_radius = 28

    def draw(self):
        x = self.center_x
        y = self.center_y

        if self.texture is not None:
            dw, dh = get_texture_display_size(
                self.texture, self.body_width, self.body_height, fit_inside=True
            )
            rect = arcade.types.XYWH(x, y, dw, dh)
            arcade.draw_texture_rect(self.texture, rect)
            return

        skin = arcade.color.BISQUE
        outline = arcade.color.BLACK

        arcade.draw_ellipse_filled(x, y - self.body_height / 2 - 10, self.body_width * 0.9, 12, (0, 0, 0, 80))

        leg_h = 30
        leg_w = 11
        leg_y = y - self.body_height / 2 - leg_h / 2 + 6
        leg_left = arcade.types.XYWH(x - 12, leg_y, leg_w, leg_h)
        leg_right = arcade.types.XYWH(x + 12, leg_y, leg_w, leg_h)
        arcade.draw_rect_filled(leg_left, arcade.color.DARK_GRAY)
        arcade.draw_rect_filled(leg_right, arcade.color.DARK_GRAY)

        body_rect = arcade.types.XYWH(x, y, self.body_width, self.body_height)
        arcade.draw_rect_filled(body_rect, arcade.color.LIGHT_GRAY)
        arcade.draw_rect_outline(body_rect, outline)

        apron_w = self.body_width * 0.75
        apron_h = self.body_height * 0.7
        apron_rect = arcade.types.XYWH(x, y - 5, apron_w, apron_h)
        arcade.draw_rect_filled(apron_rect, arcade.color.WHITE_SMOKE)
        arcade.draw_rect_outline(apron_rect, outline)
        arcade.draw_line(x - apron_w / 2, y + apron_h / 2 - 8, x + apron_w / 2, y + apron_h / 2 - 8, outline, 2)

        arm_y = y + self.body_height / 4
        arcade.draw_line(x - self.body_width / 2, arm_y, x - self.body_width / 2 - 16, arm_y - 10, outline, 3)
        hand_x = x + self.body_width / 2 + 12
        hand_y = arm_y - 6
        arcade.draw_line(x + self.body_width / 2, arm_y, hand_x, hand_y, outline, 3)
        pan_rect = arcade.types.XYWH(hand_x + 10, hand_y + 2, 26, 10)
        handle_rect = arcade.types.XYWH(hand_x + 22, hand_y + 2, 10, 4)
        arcade.draw_rect_filled(pan_rect, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_rect_outline(pan_rect, outline)
        arcade.draw_rect_filled(handle_rect, arcade.color.DARK_SLATE_GRAY)

        head_y = y + self.body_height / 2 + self.head_radius - 6
        arcade.draw_circle_filled(x, head_y, self.head_radius, skin)
        arcade.draw_circle_outline(x, head_y, self.head_radius, outline, 2)

        hat_w = self.head_radius * 2.2
        hat_h = self.head_radius * 1.6
        hat_y = head_y + self.head_radius * 0.9
        hat_rect = arcade.types.XYWH(x, hat_y, hat_w, hat_h)
        arcade.draw_rect_filled(hat_rect, arcade.color.WHITE)
        arcade.draw_rect_outline(hat_rect, outline)
        arcade.draw_ellipse_filled(x, hat_y + hat_h / 2 - 2, hat_w, hat_h / 1.7, arcade.color.WHITE)
        arcade.draw_ellipse_outline(x, hat_y + hat_h / 2 - 2, hat_w, hat_h / 1.7, outline, 2)

        eye_dx = 6
        eye_y = head_y + 4
        arcade.draw_circle_filled(x - eye_dx, eye_y, 2.2, outline)
        arcade.draw_circle_filled(x + eye_dx, eye_y, 2.2, outline)
        arcade.draw_arc_outline(x, head_y - 5, 16, 10, outline, 200, 340, 2)
