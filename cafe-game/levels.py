import arcade


class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.customers_per_hour = 10 + level_number * 2
        self.starting_money = 500 + level_number * 200
        self.objective_score = 1000 * level_number
        self.available_ingredients = self.get_available_ingredients()
        self.time_limit = 180 - level_number * 10
        self.completed = False
        self.passed = False

    def get_available_ingredients(self):
        ingredients = {
            1: ["burger", "fries", "cola"],
            2: ["burger", "fries", "cola", "icecream"],
            3: ["burger", "fries", "cheese", "cola", "icecream"],
            4: ["burger", "fries", "cheese", "cola", "icecream"],
            5: ["burger", "fries", "cheese", "cola", "icecream"],
            6: ["burger", "fries", "cheese", "cola", "icecream"],
            7: ["burger", "fries", "cheese", "cola", "icecream"]
        }
        return ingredients.get(self.level_number, [])


class LevelManager:
    def __init__(self, game):
        self.game = game
        self.current_level = None
        self.elapsed_time = 0.0

    def load_level(self, level_number):
        self.current_level = Level(level_number)
        self.elapsed_time = 0.0
        self.game.money = self.current_level.starting_money

    def update(self, delta_time):
        if not self.current_level:
            return

        self.elapsed_time += delta_time
        if self.elapsed_time >= self.current_level.time_limit:
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
        return max(0, int(self.current_level.time_limit - self.elapsed_time))