
import gspread
from google.oauth2.service_account import Credentials
import os
import time
import random

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('project3-ci')

# ascii_art for title of the game
title = """
 _ _ _              _  _
| | | | ___  ___  _| || | ___
| | | || . ||  _|| . || || -_|
|_____||___||_|  |___||_||___|
"""


class WordleGame:
    def __init__(self, sheet):
        # sheet with 14885 5 letter words
        self.answers_sheet = sheet.worksheet('answer')
        # sheet with 2309 5 letter words
        self.words_sheet = sheet.worksheet('words')
        self.all_answers = self.answers_sheet.get_all_values()
        self.all_words = self.words_sheet.get_all_values()
        self.highscores_sheet = sheet.worksheet('highscores')
        self.highscores_data = self.highscores_sheet.get_all_values()
        self.player_name = None
        self.difficulty_choice = None
        self.number_of_guesses = 0
        self.guessed = False

    def run_game(self):
        """
        Starts the game. Calls the get player name and difficulty functions
        Then displays game page and handles the game logic
        Calculates the time elapsed after starting the game
        Calls the the end game function when the game ends
        """

        if self.player_name is None:
            self.player_name = self.get_player_name()
        self.difficulty_choice = self.select_difficulty()
        difficulty_guess_mapping = {'easy': 10, 'normal': 6, 'hard': 4}
        print(f"Hello, {self.player_name}!")
        input("Press Enter to start the game")
        # had to iterate due self.all_words being a list nested in a list
        all_words_list = [' '.join(sublist) for sublist in self.all_words]
        # pick a random word from the answers list
        answer = random.choice(self.all_answers)
        answer_string = answer[0]
        # start timer
        start_time = time.time()
        self.clear_terminal()
        previous_guesses = {}

        # Run the game as long as the number of guesses does not exceed the
        # chosen difficulty limit and the word is not guessed correctly
        while self.number_of_guesses+1 < difficulty_guess_mapping[
                self.difficulty_choice] and not self.guessed:
            self.clear_terminal()
            print(title)
            # used for showing the clues for previous guessess
            current_answer_display = ['_' for i in range(5)]
            print("Your previous guesses and their clues:")
            for guess, clue in previous_guesses.items():
                print(f"{guess}: {' '.join(clue)}")

            while True:
                guess = input("Input a 5-letter word and press enter:")
                try:
                    # if the guess is in the full list of allowed words
                    if guess in all_words_list:
                        self.guessed, updated_display = self.process_guess(
                            answer_string, guess, current_answer_display)
                        # equating the number of items in the dictionary to
                        # ensures that the number of gueses does not increase
                        # if the user inputs the same word over and over again.
                        self.number_of_guesses = len(previous_guesses)
                        previous_guesses[guess] = updated_display
                        break  # Break the loop if guess is valid
                    else:
                        raise ValueError("Invalid word")
                except ValueError as e:
                    print(f"\r{e}: Please try again with a valid", end="")
                    print("word that is 5 letters long.")
        elapsed_time = time.time() - start_time
        if self.guessed:
            self.add_highscore(self.player_name,
                               self.difficulty_choice, self.number_of_guesses,
                               int(elapsed_time))
            print(f"Your final time is {elapsed_time: .0f} seconds.It", end="")
            print(f" took you {self.number_of_guesses+1} guesses", end="")
            print("to find the right word!")
            self.end_game()

        else:
            print("_"*80)
            print(f"You could not guess the word in the given ", end="")
            print(f"amount of guesses, the correct answer was {answer_string}")
            self.end_game()

    def end_game(self):
        """
        Ends the game and gives options to play again or
        return to the main menu.
        """
        while True:
            end_game_input = input(
                "Enter '1' to play again or '2' to return to the main menu: ")
            if end_game_input == '1':
                self.guessed = False
                self.run_game()
            elif end_game_input == '2':
                self.guessed = False
                self.player_name = None
                print_menu(firstload=True)
                break  # Break out of the loop when a valid option is entered
            else:
                print("Please enter a valid option (1 or 2).")

    def process_guess(self, answer, guess, answer_display):
        """
        Check if the guessed word is correct or not and
        if not true give clues depending the letter locations
        """
        if guess == answer:
            print("Congratulations! You guessed the word correctly.")
            self.guessed = True
        else:
            for i, letter in enumerate(guess):
                if letter == answer[i]:
                    answer_display[i] = letter
                elif letter in answer:
                    answer_display[i] = letter+"*"
                else:
                    answer_display[i] = "_"
        return self.guessed, answer_display

    def get_player_name(self):
        """
        Gets the player name and checks its length
        """
        while True:
            name = input("Please enter your name: ").strip()
            if len(name) > 2 and name.isalnum():
                return name.title()
            else:
                print(
                    "\rYour name must be at least 3 characters long ", end="")
                print("and can only contain letters/numbers. Try again.")

    def how_to_play(self):
        """
        Display how to play information
        """
        print(title)
        print("-" * 80)
        print("How to Play Wordle:")
        print(
            "1. You will be asked to enter your name upon starting the game."
        )
        print(
            "2. Once your name is entered, desired difficulty will be asked"
            )
        print(
            "  After choosing your difficulty level, the game will begin"
            )
        print(
            "3. You'll be asked to type and try to guess a 5-letter word."
        )
        print("4. The game will provide feedback on your guess attempts.")
        print(
            "5. The feedback consists of two elements: "
        )
        print(
            "  correct letters and correct letters in the wrong position (*)")
        print(
            "6. For example, if the answer is 'APPLE' and you guess is 'ADOPT'"
        )
        print("  the feedback might look like this: A _ _ P*_ ")
        print(
            "  as you can see the 'A' is in correct position with no marking "
        )
        print(
            "  P* idicating the letter is in the answer at different position"
        )
        print(
            "7. If you correctly guess the word, you win the game!"
        )
        print("8. Have fun!")
        input("Press Enter to return to the main menu...")

    def select_difficulty(self):
        """
        Difficalty selector based on user input
        """
        print("Select difficulty:")
        print("e - Easy")
        print("n - Normal")
        print("h - Hard")
        while True:
            difficulty_choice = input("Enter choice (e/n/h): ").lower()
            if difficulty_choice in {"e", "n", "h"}:
                if difficulty_choice == "e":
                    print("You have selected easy difficulty. ")
                    print("You will be given 10 attempts to guess the word.")
                    return "easy"
                elif difficulty_choice == "n":
                    print("You have selected normal difficulty.")
                    print("You will be given 6 attempts to guess the word.")
                    return "normal"
                elif difficulty_choice == "h":
                    print("You have selected hard difficulty.")
                    print("You will be given 4 attempts to guess the word.")
                    return "hard"
                break
            else:
                print("\rPlease enter a valid option (e, n, h).", end="")
                return self.select_difficulty()

    def get_num_guesses(self):
        """
        Dependig on the difficulty of choise returns the number of guesses
        allowed before ending the game
        """
        if self.difficulty_choice == "easy":
            return 10
        elif self.difficulty_choice == "normal":
            return 6
        elif self.difficulty_choice == "hard":
            return 4

    def clear_terminal(self):
        """
        Clears terminal
        """
        # recovered from
        # https://stackoverflow.com/questions/2084508/clear-the-terminal-in-python
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_highscores(self):
        """
        Show highscores data of the best 5 players
        The data is take from google sheets
        """
        self.highscores_data = self.highscores_sheet.get_all_values()
        print(title)
        print("-" * 80)
        print("Top 10 Highscores:")

        # Map difficulty levels to numerical values for sorting
        difficulty_mapping = {'easy': 1, 'normal': 2, 'hard': 3}
        # Skip the header row and convert numeric values for sorting
        highscores_data = [[row[0], row[1], int(row[2]),
                            int(row[3])] for row in self.highscores_data[1:]]

        def sort_scores(score):
            """
            Sorting function for highscores, first the player are sorted
            accordig to the number of guesses
            then according to difficulty and finally for time
            """
            name, difficulty, guesses, time = score
            return (guesses, -difficulty_mapping[difficulty], time)

        # Sort the high_scores list
        sorted_highscores = sorted(highscores_data, key=sort_scores)
        for i, score in enumerate(sorted_highscores[:10]):
            print(f"{i + 1}. Name: {score[0]}, Difficulty:", end="")
            print(f"{score[1].title()}, Guesses: {score[2]}, Time: {score[3]}")
        print("-" * 80)
        input("Press Enter to return to the main menu...")

    def add_highscore(self, player_name, difficulty, num_guesses, time_taken):
        """
        Add a new highscore to the highscores sheet.
        """
        new_highscore = [player_name, difficulty, num_guesses, time_taken]
        self.highscores_sheet.append_row(new_highscore)


def print_menu(firstload):
    """
    Function to display the main menu options and the ascii wordle title.
    Calls the corresponding functions for each option
    """
    if firstload:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(title)
        print("-" * 80)
        print(" Welcome to our Wordle Game! Get ready to test your")
        print(" word-guessing skills and have some fun. Let's see if")
        print(" you can crack the code and climb up the highscore chart!")
        print("-" * 80)
        print("1. Start Game")
        print("2. Show High-Scores")
        print("3. How to play")
        print("-" * 80)


def main():
    """
    The main function to run the Wordle game indefinitly.
    """
    # Create an instance of the WordleGame class named game
    game = WordleGame(SHEET)
    # Set the flag of print_menu fuction to true for only initally showing menu
    firstload = True
    while True:

        # Display the menu and get the user's choice
        print_menu(firstload)
        choice = input("Type: 1 (Start Game) 2 (Highscores) or 3 (Rules): ")
        firstload = False
        # Set the flag to False after the first display this ensures that
        # the etire menu is not reprinnted after an invalid choice, etc
        if choice == "1":
            game.run_game()

        elif choice == "2":
            # Clear termial for showing the highscores, reset the menu flag
            game.clear_terminal()
            game.show_highscores()
            firstload = True

        elif choice == "3":
            # Clear termial for showing the rules, reset the menu flag
            game.clear_terminal()
            game.how_to_play()
            firstload = True

        else:
            # print error mesage if the type value is not 1,2 or 3
            print("Invalid option. Please choose a valid option.")
            continue


if __name__ == "__main__":
    main()
