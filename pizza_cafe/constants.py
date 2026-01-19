SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Cafe Chef Deluxe"
BACKGROUND_COLOR = (34, 139, 34)

ORDER_TAB_COLOR = (60, 60, 80)
ORDER_TAB_ACTIVE_COLOR = (100, 150, 200)
COOKING_TAB_COLOR = (80, 60, 60)
COOKING_TAB_ACTIVE_COLOR = (200, 150, 100)

TAB_HEIGHT = 60
TAB_Y = SCREEN_HEIGHT - 30
ORDER_TAB_X = 200
COOKING_TAB_X = 500
TAB_WIDTH = 300

KITCHEN_BG_COLOR = (45, 45, 55)
ORDER_BG_COLOR = (70, 90, 110)

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = (220, 110, 50)
BUTTON_HOVER_COLOR = (255, 140, 60)
TEXT_COLOR = (255, 255, 255)
TEXT_COLOR_DARK = (50, 50, 50)

PIZZA_X = 400
PIZZA_Y = 450
PIZZA_RADIUS = 180
PIZZA_CRUST_COLOR = (210, 180, 140)
PIZZA_SAUCE_COLOR = (255, 69, 0)
CHEESE_COLOR = (255, 215, 0)

BURGER_X = 400
BURGER_Y = 450
BURGER_WIDTH = 200
BURGER_HEIGHT = 50

DRINK_X = 400
DRINK_Y = 450
DRINK_RADIUS = 60

INGREDIENT_SIZE = 24
INGREDIENT_COLORS = {
    "pepperoni": (200, 0, 0),
    "mushrooms": (160, 120, 80),
    "peppers": (0, 180, 0),
    "onions": (255, 255, 240),
    "olives": (50, 50, 50),
    "tomato": (255, 99, 71),
    "sausage": (160, 80, 40),
    "basil": (0, 150, 0),
    "cheese": (255, 215, 0),
    "sauce": (255, 69, 0),
    "pineapple": (255, 255, 100),
    "ham": (255, 200, 180),
    "bacon": (200, 150, 120),
    "garlic": (240, 230, 210),
    "lettuce": (0, 200, 0),
    "pickles": (150, 200, 50),
    "beef": (139, 69, 19),
    "chicken": (255, 200, 150),
    "mayonnaise": (255, 255, 200),
    "ketchup": (255, 0, 0)
}

DRINK_COLORS = {
    "cola": (50, 25, 0),
    "sprite": (200, 255, 200),
    "orange": (255, 165, 0),
    "coffee": (101, 67, 33),
    "tea": (139, 90, 43),
    "water": (200, 230, 255),
    "juice": (255, 140, 0)
}

INGREDIENT_PRICES = {
    "dough": 1,
    "sauce": 1,
    "cheese": 2,
    "pepperoni": 3,
    "mushrooms": 2,
    "peppers": 2,
    "onions": 1,
    "olives": 2,
    "tomato": 2,
    "sausage": 4,
    "basil": 1,
    "pineapple": 3,
    "ham": 3,
    "bacon": 4,
    "garlic": 1,
    "lettuce": 1,
    "pickles": 1,
    "beef": 5,
    "chicken": 4,
    "mayonnaise": 1,
    "ketchup": 1
}

DRINK_PRICES = {
    "cola": 2,
    "sprite": 2,
    "orange": 2,
    "coffee": 3,
    "tea": 2,
    "water": 1,
    "juice": 3
}

LEVEL_TIME_LIMITS = [200, 190, 180, 170, 160, 150, 140]
LEVEL_CUSTOMER_COUNTS = [3, 4, 5, 6, 7, 8, 10]
LEVEL_MONEY_TARGETS = [50, 100, 150, 220, 300, 400, 500]
LEVEL_DIFFICULTY_MOD = [1, 1, 2, 2, 3, 3, 4]

INGREDIENT_BUTTONS_X = 950
INGREDIENT_BUTTONS_Y_START = 750
INGREDIENT_BUTTON_SPACING = 40

ORDER_DISPLAY_X = 950
ORDER_DISPLAY_Y = 400
ORDER_DISPLAY_WIDTH = 400
ORDER_DISPLAY_HEIGHT = 450

MONEY_DISPLAY_X = 150
MONEY_DISPLAY_Y = 850
TIMER_DISPLAY_X = 400
TIMER_DISPLAY_Y = 850
LEVEL_DISPLAY_X = 650
LEVEL_DISPLAY_Y = 850

CUSTOMER_X = 950
CUSTOMER_Y = 200

OVEN_X = 150
OVEN_Y = 200
OVEN_WIDTH = 120
OVEN_HEIGHT = 80

GRILL_X = 150
GRILL_Y = 300
GRILL_WIDTH = 120
GRILL_HEIGHT = 80

DRINK_MACHINE_X = 150
DRINK_MACHINE_Y = 400
DRINK_MACHINE_WIDTH = 120
DRINK_MACHINE_HEIGHT = 80

CUT_BUTTON_X = 150
CUT_BUTTON_Y = 500
SUBMIT_BUTTON_X = 150
SUBMIT_BUTTON_Y = 550
ASSEMBLE_BUTTON_X = 150
ASSEMBLE_BUTTON_Y = 600

START_BUTTON_X = 700
START_BUTTON_Y = 450
EXIT_BUTTON_X = 700
EXIT_BUTTON_Y = 350
RESTART_BUTTON_X = 700
RESTART_BUTTON_Y = 250
CONTINUE_BUTTON_X = 700
CONTINUE_BUTTON_Y = 350

FONT_SIZE = 20
TITLE_FONT_SIZE = 48
ORDER_FONT_SIZE = 18
BIG_FONT_SIZE = 32

STATE_DOUGH = 0
STATE_SAUCE = 1
STATE_CHEESE = 2
STATE_TOPPINGS = 3
STATE_COOKING = 4
STATE_CUTTING = 5
STATE_COMPLETE = 6

BURGER_STATE_BUN = 0
BURGER_STATE_PATTY = 1
BURGER_STATE_COOKING = 2
BURGER_STATE_TOPPINGS = 3
BURGER_STATE_ASSEMBLING = 4
BURGER_STATE_COMPLETE = 5

DRINK_STATE_EMPTY = 0
DRINK_STATE_FILLING = 1
DRINK_STATE_COMPLETE = 2

COOK_TIME_MIN = 8
COOK_TIME_MAX = 15
BURN_TIME = 25

GRILL_TIME_MIN = 6
GRILL_TIME_MAX = 12
GRILL_BURN_TIME = 20

FILL_TIME_MIN = 2
FILL_TIME_MAX = 4

INGREDIENTS_PER_LEVEL = [
    ["pepperoni", "mushrooms", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "onions", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "onions", "olives", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "onions", "olives", "tomato", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "onions", "olives", "tomato", "sausage", "cheese"],
    ["pepperoni", "mushrooms", "peppers", "onions", "olives", "tomato", "sausage", "basil", "pineapple", "ham", "cheese"]
]

BURGER_INGREDIENTS_PER_LEVEL = [
    ["lettuce", "tomato"],
    ["lettuce", "tomato", "cheese"],
    ["lettuce", "tomato", "cheese", "onions"],
    ["lettuce", "tomato", "cheese", "onions", "pickles"],
    ["lettuce", "tomato", "cheese", "onions", "pickles", "bacon"],
    ["lettuce", "tomato", "cheese", "onions", "pickles", "bacon", "mayonnaise"],
    ["lettuce", "tomato", "cheese", "onions", "pickles", "bacon", "mayonnaise", "ketchup"]
]

DRINKS_PER_LEVEL = [
    ["cola", "water"],
    ["cola", "water", "sprite"],
    ["cola", "water", "sprite", "orange"],
    ["cola", "water", "sprite", "orange", "coffee"],
    ["cola", "water", "sprite", "orange", "coffee", "tea"],
    ["cola", "water", "sprite", "orange", "coffee", "tea", "juice"],
    ["cola", "water", "sprite", "orange", "coffee", "tea", "juice"]
]

ORDER_TYPES = ["pizza", "burger", "drink"]