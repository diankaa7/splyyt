import arcade
from game import FastFoodGame

def main():
    window = FastFoodGame(1280, 720, "MAK")
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()