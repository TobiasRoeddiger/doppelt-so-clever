import tkinter as tk
import random
import time

class Dice:
    def __init__(self, color):
        self.color = color
        self.sides = list(range(1, 7))  # Sides are numbered 1 to 6
        self.current_value = None  # To store the value after rolling

    def get_color(self):
        return self.color

    def set_color(self, new_color):
        self.color = new_color

    def get_sides(self):
        return self.sides

    def roll(self):
        self.current_value = random.choice(self.sides)
        return self.current_value

    def get_current_value(self):
        return self.current_value

    def __str__(self):
        return f"{self.get_current_value()}"
    
class DummyDice(Dice):
    def __init__(self, color, value):
        self.color = color
        self.current_value = value
    
    def roll(self):
        return

    def get_sides(self):
        return [self.value]

class Field:
    def __init__(self, color, ui_row):
        self.color = color
        self.dice = []
        self.ui_row = ui_row

    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        return dice.get_color() == self.color or dice.get_color() == 'white'
    
    def play_dice(self, dice, rolled_dice_list, taken_out_dice_list):
        if self.can_play(dice, None, None):
            self.dice.append(dice)
            return dice.get_current_value()
        else:
            return 0

    def update_ui(self):
        for i, cell in enumerate(self.ui_row):
            if i < len(self.dice):
                cell.config(text=str(self.dice[i]), bg=self.dice[i].get_color())
            else:
                cell.config(text="", bg="white")
    
    def calculate_score(self):
        return sum(dice.get_current_value() for dice in self.dice)

class SilverField(Field):
    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        return super().can_play(dice, rolled_dice_list, taken_out_dice_list)

class YellowField(Field):
    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        return super().can_play(dice, rolled_dice_list, taken_out_dice_list)

class BlueField(Field):
    def __init__(self, color, ui_row):
        super().__init__(color, ui_row)
        self.previous_sum = None
        self.score_table = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78]

    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        if len(self.dice) >= 12:
            return False

        if dice.get_color() not in ['blue', 'white']:
            return False

        white_dice_in_rolled = next((d for d in rolled_dice_list if d.get_color() == 'white'), None)
        blue_dice_in_rolled = next((d for d in rolled_dice_list if d.get_color() == 'blue'), None)
        white_dice = white_dice_in_rolled or next((d for d in taken_out_dice_list if d.get_color() == 'white'), None)
        blue_dice = blue_dice_in_rolled or next((d for d in taken_out_dice_list if d.get_color() == 'blue'), None)

        if not white_dice or not blue_dice:
            return False

        if not white_dice_in_rolled and not blue_dice_in_rolled:
            return False

        sum_value = dice.get_current_value() + (white_dice.get_current_value() if dice.get_color() != 'white' else blue_dice.get_current_value())

        if self.previous_sum is None or sum_value <= self.previous_sum:
            return True
        return False

    def play_dice(self, dice, rolled_dice_list, taken_out_dice_list):
        white_dice = next((d for d in rolled_dice_list if d.get_color() == 'white'), None) or \
                     next((d for d in taken_out_dice_list if d.get_color() == 'white'), None)
        blue_dice = next((d for d in rolled_dice_list if d.get_color() == 'blue'), None) or \
                    next((d for d in taken_out_dice_list if d.get_color() == 'blue'), None)

        if self.can_play(dice, rolled_dice_list, taken_out_dice_list):
            sum_value = dice.get_current_value() + (white_dice.get_current_value() if dice.get_color() != 'white' else blue_dice.get_current_value())
            self.dice.append(DummyDice('lightblue', sum_value))
            self.previous_sum = sum_value
            return dice.get_current_value()
        return 0

    def calculate_score(self):
        num_dice = len(self.dice)
        if num_dice == 0:
            return 0
        return self.score_table[num_dice - 1]

class GreenField(Field):
    def __init__(self, color, ui_row):
        super().__init__(color, ui_row)
        self.multipliers = [2, 2, 2, 1, 3, 3, 3, 2, 3, 1, 4, 1]

    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        return super().can_play(dice, rolled_dice_list, taken_out_dice_list)
    
    def play_dice(self, dice, rolled_dice_list, taken_out_dice_list):
        if len(self.dice) >= 12:
            return False
        
        if self.can_play(dice, None, None):
            self.dice.append(DummyDice("lightgreen", self.multipliers[len(self.dice)] * dice.get_current_value()))
            return dice.get_current_value()
        else:
            return 0
        
    def calculate_score(self):
        score = 0
        for i in range(0, min(len(self.dice), 12) - 1, 2):
            if i + 1 < len(self.dice):
                score += self.dice[i].get_current_value() - self.dice[i + 1].get_current_value()
        return score

class PinkField(Field):
    def __init__(self, color, ui_row):
        super().__init__(color, ui_row)
        self.minimum_values = [0, 0, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6]

    def can_play(self, dice, rolled_dice_list, taken_out_dice_list):
        if len(self.dice) >= 12:
            return False
        required_value = self.minimum_values[len(self.dice)]
        return super().can_play(dice, rolled_dice_list, taken_out_dice_list) and (dice.get_current_value() >= required_value)

class Game:
    def __init__(self, root):
        self.fields = []
        self.total_points = 0
        self.rounds = 6
        self.current_round = 0
        self.rolled_dice_list = []
        self.taken_out_dice_list = []

        self.root = root
        self.root.title("Dice Game")

        self.create_ui()

    def create_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.fields_frame = tk.Frame(self.frame)
        self.fields_frame.pack()

        colors = ['silver', 'yellow', 'blue', 'green', 'pink']

        for color in colors:
            row_frame = tk.Frame(self.fields_frame)
            row_frame.pack(fill="x")
            label = tk.Label(row_frame, text=f"{color.capitalize()}:", font=("Helvetica", 12), width=10, anchor="w")
            label.pack(side="left")
            ui_row = []
            for i in range(12):
                cell = tk.Label(row_frame, text="", font=("Helvetica", 12), width=4, relief="solid", borderwidth=1, bg="white")
                cell.pack(side="left")
                ui_row.append(cell)
            if color == 'silver':
                self.fields.append(SilverField(color, ui_row))
            elif color == 'yellow':
                self.fields.append(YellowField(color, ui_row))
            elif color == 'blue':
                self.fields.append(BlueField(color, ui_row))
            elif color == 'green':
                self.fields.append(GreenField(color, ui_row))
            elif color == 'pink':
                self.fields.append(PinkField(color, ui_row))

        self.rolled_label = tk.Label(self.frame, text="Rolled Dice: ", font=("Helvetica", 12))
        self.rolled_label.pack(pady=5)
        self.rolled_dice_frame = tk.Frame(self.frame)
        self.rolled_dice_frame.pack()

        self.in_label = tk.Label(self.frame, text="Still In Play: ", font=("Helvetica", 12))
        self.in_label.pack(pady=5)
        self.in_dice_frame = tk.Frame(self.frame)
        self.in_dice_frame.pack()

        self.out_label = tk.Label(self.frame, text="Taken Out: ", font=("Helvetica", 12))
        self.out_label.pack(pady=5)
        self.out_dice_frame = tk.Frame(self.frame)
        self.out_dice_frame.pack()

        self.play_button = tk.Button(self.frame, text="Play Round", command=self.play_round, font=("Helvetica", 14))
        self.play_button.pack(pady=10)
        
        self.status_label = tk.Label(self.frame, text="Status: Waiting to start", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.score_label = tk.Label(self.frame, text="Score: 0", font=("Helvetica", 12))
        self.score_label.pack(pady=5)

    def update_display(self):
        for field in self.fields:
            field.update_ui()

        for widget in self.rolled_dice_frame.winfo_children():
            widget.destroy()
        for dice in self.rolled_dice_list:
            dice_label = tk.Label(self.rolled_dice_frame, text=str(dice.get_current_value()), font=("Helvetica", 12), width=4, relief="solid", borderwidth=1, bg=dice.get_color())
            dice_label.pack(side="left")

        for widget in self.in_dice_frame.winfo_children():
            widget.destroy()
        for dice in self.rolled_dice_list:
            dice_label = tk.Label(self.in_dice_frame, text=str(dice.get_current_value()), font=("Helvetica", 12), width=4, relief="solid", borderwidth=1, bg=dice.get_color())
            dice_label.pack(side="left")

        for widget in self.out_dice_frame.winfo_children():
            widget.destroy()
        for dice in self.taken_out_dice_list:
            dice_label = tk.Label(self.out_dice_frame, text=str(dice.get_current_value()), font=("Helvetica", 12), width=4, relief="solid", borderwidth=1, bg=dice.get_color())
            dice_label.pack(side="left")

        self.update_score()

    def play_round(self):
        if self.current_round >= self.rounds:
            return
        
        self.play_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Playing round")
        
        self.rolled_dice_list = [Dice(color) for color in ['silver', 'yellow', 'blue', 'green', 'pink', 'white']]
        self.taken_out_dice_list = []
        self.play_step(0)

    def play_step(self, step):
        if step >= 3:
            self.current_round += 1
            self.update_display()
            self.play_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Round completed")
            return

        for dice in self.rolled_dice_list:
            dice.roll()
        self.rolled_dice_list.sort(key=lambda d: d.get_current_value())

        self.update_display()
        self.status_label.config(text=f"Status: Step {step + 1} - Rolling dice")
        self.root.after(3000, self.place_dice, step)

    def place_dice(self, step):
        placed_dice = False
        for dice in self.rolled_dice_list:
            for field in self.fields:
                if field.can_play(dice, self.rolled_dice_list, self.taken_out_dice_list):
                    points = field.play_dice(dice, self.rolled_dice_list, self.taken_out_dice_list)
                    self.total_points += points
                    self.taken_out_dice_list.append(dice)
                    self.rolled_dice_list.remove(dice)
                    placed_dice = True
                    break
            if placed_dice:
                break

        highest_value_dice = self.rolled_dice_list[0].get_current_value() if self.rolled_dice_list else None
        self.rolled_dice_list[:] = [dice for dice in self.rolled_dice_list if dice.get_current_value() >= highest_value_dice]

        self.update_display()
        self.status_label.config(text=f"Status: Step {step + 1} - Placing dice")
        self.root.after(3000, self.play_step, step + 1)
    
    def update_score(self):
        self.total_points = sum(field.calculate_score() for field in self.fields)
        self.score_label.config(text=f"Score: {self.total_points}")

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()