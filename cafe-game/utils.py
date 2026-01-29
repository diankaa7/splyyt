import arcade
import os

def load_texture(path):
    """
    Load a texture from disk.
    If the file doesn't exist, return a visible placeholder texture instead of crashing.
    """
    if os.path.exists(path):
        return arcade.load_texture(path)

    # Visible placeholder so missing assets are obvious but non-fatal.
    try:
        return arcade.make_soft_square_texture(64, arcade.color.MAGENTA, 255, 255)
    except Exception:
        # Fallback for older arcade versions (best effort).
        return arcade.load_texture(":resources:images/tiles/boxCrate_double.png")


def get_texture_display_size(texture, target_width, target_height=None, fit_inside=True):
    """
    Вычисляет размер отрисовки текстуры с сохранением пропорций.
    Позволяет использовать изображения любого разрешения — они масштабируются под целевой размер.

    :param texture: текстура arcade (должна иметь .width и .height)
    :param target_width: целевая ширина (или максимальная при fit_inside)
    :param target_height: целевая высота; если None, используется target_width (квадрат)
    :param fit_inside: если True, текстурa вписывается в прямоугольник target_width x target_height
    :return: (display_width, display_height) в пикселях
    """
    if target_height is None:
        target_height = target_width
    tw = getattr(texture, "width", 64)
    th = getattr(texture, "height", 64)
    if tw <= 0 or th <= 0:
        return (target_width, target_height)
    scale_w = target_width / tw
    scale_h = target_height / th
    if fit_inside:
        scale = min(scale_w, scale_h)
    else:
        scale = max(scale_w, scale_h)
    return (max(1, int(tw * scale)), max(1, int(th * scale)))

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