import arcade
import os
from PIL import Image, ImageDraw, ImageFont


def generate_placeholder_image(path, size=(100, 100), color=(100, 100, 100), text=""):
    """Генерирует placeholder-изображение с текстом"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    img = Image.new('RGBA', size, (*color, 255))
    draw = ImageDraw.Draw(img)

    if text:
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    img.save(path)


def ensure_required_images():
    """Гарантирует наличие всех необходимых изображений"""
    required_images = [
        ("images/main_menu_bg.png", (1920, 1080), (30, 30, 50), "MAIN MENU"),
        ("images/level1_bg.png", (1280, 720), (50, 30, 30), "LEVEL 1"),
        ("images/player_idle.png", (150, 250), (200, 100, 50), "PLAYER"),
        ("images/grill.png", (150, 150), (80, 80, 80), "GRILL"),
        ("images/fryer.png", (150, 150), (180, 120, 60), "FRYER"),
        ("images/ice_cream_machine.png", (150, 150), (220, 200, 250), "ICE CREAM"),
        ("images/soda_tap.png", (150, 150), (100, 200, 250), "SODA TAP"),
        ("images/fries_raw.png", (100, 100), (200, 180, 100), "RAW FRIES"),
        ("images/fries_cooked.png", (100, 100), (230, 200, 100), "COOKED FRIES"),
        ("images/order_ticket.png", (300, 150), (250, 250, 200), "ORDER"),
        ("images/button_start.png", (200, 80), (100, 200, 100), "START"),
        ("images/button_exit.png", (200, 80), (200, 100, 100), "EXIT"),
        ("images/coin_icon.png", (40, 40), (255, 215, 0), "$"),
        ("images/trash_can.png", (60, 60), (120, 120, 120), "TRASH"),
        ("images/sparkle_effect.png", (80, 80), (255, 255, 200, 100), "*"),
        ("images/smoke_effect.png", (100, 100), (100, 100, 100, 150), "~")
    ]

    for img_path, size, color, text in required_images:
        if not os.path.exists(img_path):
            print(f"Generating missing image: {img_path}")
            generate_placeholder_image(img_path, size, color, text)


def load_texture(path):
    """Загружает текстуру с автоматической генерацией заглушки при отсутствии файла"""
    if not os.path.exists(path):
        print(f"Warning: Image not found - {path}")
        dir_name = os.path.dirname(path)
        base_name = os.path.basename(path)
        placeholder_path = os.path.join(dir_name, f"placeholder_{base_name}")

        if not os.path.exists(placeholder_path):
            generate_placeholder_image(placeholder_path, (100, 100), (150, 50, 50), "MISSING")

        return arcade.load_texture(placeholder_path)

    return arcade.load_texture(path)


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def get_equipment_position(equipment_name):
    positions = {
        "grill": (450, 320),
        "fryer": (550, 320),
        "ice_cream_machine": (650, 320),
        "soda_tap": (750, 320)
    }
    return positions.get(equipment_name, (0, 0))


def calculate_score(items):
    base_scores = {
        "burger": 50,
        "fries": 30,
        "icecream": 25,
        "drink": 20
    }
    total = 0
    for item, details in items.items():
        if item == "burger":
            total += base_scores["burger"] * len(details)
        else:
            total += base_scores.get(item, 0)
    return total