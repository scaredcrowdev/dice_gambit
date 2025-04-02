import sys
import json
import os

def get_int_input(prompt, min_val=None, max_val=None):
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Please enter a number at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Please enter a number no greater than {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def load_players(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_players(file_path, players):
    with open(file_path, "w") as file:
        json.dump(players, file, indent=4)

def print_c(message, color):
    colors = {
        "red": '\033[31m',
        "cyan": '\033[36m',
        "magenta": '\033[35m',
        "green": '\033[32m',
        }
    reset = '\033[0m'

    print(f"{colors[color]}{message}{reset}")


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else "players.json"
    players = load_players(file_path)

    print_c("Welcome to Dice Gambit!🎲", "magenta")

    if not players:
        num_players = get_int_input("Enter number of players: ", 1)
        for _ in range(num_players):
            name = input("Enter player name: ").strip()
            points = input(f"Enter {name}'s points: ")
            players[name] = {"points": int(points), "bets": {}, "results": {}}

    # Input bets for each player
    for name in players:
        print(f"\n{name}'s turn to place bets:")

        # Get bets for each game
        bet_d6 = get_int_input("Enter bet for D6: ", 0)
        choice_d6 = get_int_input("Choose a number (1-6) for D6: ", 1, 6)

        bet_d8 = get_int_input("Enter bet for D8: ", 0)
        choice_d8 = get_int_input("Choose a number (1-8) for D8: ", 1, 8)

        bet_d10 = get_int_input("Enter bet for D10 (per number): ", 0)
        num_choices = get_int_input("How many numbers will you bet on? (1-3): ", 1, 3)
        choices_d10 = [get_int_input(f"Enter choice {i+1} (1-10): ", 1, 10) for i in range(num_choices)]

        # Store bets
        players[name]["bets"] = {
            "D6": (bet_d6, choice_d6),
            "D8": (bet_d8, choice_d8),
            "D10": (bet_d10, choices_d10)
        }

    # Get the lowest-scoring player's points to enforce bet limits
    min_points = min(int(player["points"]) for player in players.values())

    # Ensure total bets do not exceed the lowest player's points
    for name in players:
        total_bet = sum(bet for bet, _ in players[name]["bets"].values())
        if total_bet > min_points:
            print(f"{name} exceeded the bet limit ({min_points} points). Adjusting bets...")
            scale_factor = min_points / total_bet
            for game in ["D6", "D8", "D10"]:
                bet, choices = players[name]["bets"][game]
                players[name]["bets"][game] = (int(bet * scale_factor), choices)

    # Input actual dice rolls
    roll_d6 = get_int_input("\nEnter the actual roll for D6 (1-6): ", 1, 6)
    roll_d8 = get_int_input("Enter the actual roll for D8 (1-8): ", 1, 8)
    wild_d10 = get_int_input("Enter the first roll for D10 (wild number, 1-10): ", 1, 10)
    roll_d10 = get_int_input("Enter the second roll for D10 (1-10): ", 1, 10)

    # Calculate results for each player
    for name in players:
        bets = players[name]["bets"]
        points_won = 0
        correct_games = 0

        # D6 game
        bet, choice = bets["D6"]
        if choice == roll_d6:
            points_won += bet * 3
            correct_games += 1
        else:
            points_won -= bet

        # D8 game
        bet, choice = bets["D8"]
        if choice == roll_d8:
            points_won += bet * 4
            correct_games += 1
        else:
            points_won -= bet

        # D10 game
        bet, choices = bets["D10"]
        multiplier = {1: 10, 2: 5, 3: 3}[len(choices)]
        matches = sum(1 for choice in choices if choice == roll_d10)

        if wild_d10 == roll_d10 and wild_d10 in choices:
            multiplier *= 3

        if matches > 0:
            points_won += bet * matches * multiplier
            correct_games += 1
        else:
            points_won -= bet * len(choices)

        # Apply bonus multipliers
        if correct_games == 3:
            points_won *= 3
        elif correct_games == 2:
            points_won *= 2

        # Update player points
        text_color = ""
        if points_won <= 0:
            text_color="red"
        else:
            text_color="green"

        players[name]["points"] += points_won
        print_c(f"\n{name}'s score is {points_won} and now has {players[name]['points']} points.", text_color)

    # Save updated results
    save_players(file_path, players)

    print_c("\nFinal Results 🃏:", magenta)
    for name, data in players.items():
        print_c(f"{name}: {data['points']} points", "cyan")

if __name__ == "__main__":
    main()
