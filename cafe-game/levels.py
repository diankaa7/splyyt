import arcade


class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.customers_per_hour = 10 + level_number * 2
        self.starting_money = 500 + level_number * 200
        self.objective_score = 1000 * level_number
        self.available_ingredients = self.get_available_ingredients()
        self.time_limit = 180 - level_number * 10  # seconds
        self.completed = False
        self.passed = False

    def get_available_ingredients(self):
        ingredients = {
            1: ["burger", "fries", "cola"],
            2: ["burger", "fries", "cola", "sprite"],
            3: ["burger", "fries", "cola", "sprite", "water", "icecream"],
            4: ["burger", "fries", "cheese", "lettuce", "tomato", "sauce", "cola", "sprite", "water", "icecream"],
            5: ["burger", "fries", "cheese", "lettuce", "tomato", "sauce", "cola", "sprite", "water", "vanilla",
                "chocolate"],
            6: ["burger", "fries", "cheese", "lettuce", "tomato", "sauce", "cola", "sprite", "water", "vanilla",
                "chocolate", "strawberry"],
            7: ["burger", "fries", "cheese", "lettuce", "tomato", "sauce", "cola", "sprite", "water", "vanilla",
                "chocolate", "strawberry"]
        }
        return ingredients.get(self.level_number, [])


class LevelManager:
    def __init__(self, game):
        self.game = game
        self.current_level = None
        self.level_start_time = 0
        self.level_duration = 0

    def load_level(self, level_number):
        self.current_level = Level(level_number)
        self.level_start_time = arcade.get_fps()
        self.level_duration = self.current_level.time_limit * 60
        self.game.money = self.current_level.starting_money

    def update(self, delta_time):
        if not self.current_level:
            return

        elapsed_frames = arcade.get_fps() - self.level_start_time
        if elapsed_frames > self.level_duration:
            self.check_level_completion()

    def check_level_completion(self):
        if self.game.score >= self.current_level.objective_score:
            self.current_level.passed = True
            self.current_level.completed = True
        else:
            self.current_level.passed = False
            self.current_level.completed = True

    def is_level_complete(self):
        return self.current_level and self.current_level.completed

    def get_time_remaining(self):
        if not self.current_level:
            return 0

        elapsed_frames = arcade.get_fps() - self.level_start_time
        remaining_frames = self.level_duration - elapsed_frames
        return max(0, remaining_frames // 60)