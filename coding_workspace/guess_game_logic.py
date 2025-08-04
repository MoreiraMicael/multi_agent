import random

class NumberGuessingGame:
    """
    A simple number guessing game where the player tries to guess a random number between 0-9.

    Attributes:
        target_number (int): The randomly generated number for the current game.
        attempts (int): The number of attempts made by the player to guess the target number.
        games_played (int): The total number of games played.
        wins (int): The total number of wins.
        average_attempts (float): The average number of attempts per game.

    Methods:
        start_new_game(): Initializes a new game by generating a random target number and resetting statistics.
        make_guess(guess: int) -> str: Allows the player to make a guess. Returns feedback based on correctness.
        display_statistics() -> None: Displays the current game statistics.
    """

    def __init__(self):
        """
        Initializes an instance of NumberGuessingGame with default values for game statistics.
        """
        self.target_number = random.randint(0, 9)
        self.attempts = 0
        self.games_played = 0
        self.wins = 0
        self.average_attempts = 0.0

    def start_new_game(self) -> None:
        """
        Initializes a new game by generating a random target number and resetting statistics.

        Returns:
            None: Indicates that the game has started.
        """
        self.target_number = random.randint(0, 9)
        self.attempts = 0
        self.games_played += 1

    def make_guess(self, guess: int) -> str:
        """
        Allows the player to make a guess.

        Args:
            guess (int): The user's guess for the target number.

        Returns:
            str: Feedback indicating if the guess is too high, too low, or correct. If the game is won,
                 it will display the final message.
        """
        self.attempts += 1
        if guess == self.target_number:
            self.wins += 1
            return f"Congratulations! You got it in {self.attempts} attempts."
        elif guess > self.target_number:
            return "Too high! Try again."
        else:
            return "Too low! Guess higher."

    def display_statistics(self) -> None:
        """
        Displays the current game statistics.

        Returns:
            None: Prints the statistics to the console.
        """
        if self.games_played == 0:
            print("Statistics will be displayed after playing at least one game.")
        else:
            average_attempts = self.average_attempts
            games_played = self.games_played
            wins = self.wins

            print(f"Games played: {games_played}")
            print(f"Wins: {wins}")
            if average_attempts != 0.0:
                print(f"Average attempts per game: {average_attempts:.2f}")

    def display_average_attempts(self) -> float:
        """
        Calculates and returns the average number of attempts per game.

        Returns:
            float: The average number of attempts per game.
        """
        if self.games_played == 0:
            return 0.0
        return self.attempts / self.games_played

    # Example usage:
game = NumberGuessingGame()
game.start_new_game()

while True:
    user_guess = int(input("Enter your guess (0-9): "))
    feedback = game.make_guess(user_guess)

    if "Congratulations" in feedback:
        print(f"{feedback} Would you like to play again? (yes/no)")
        response = input().lower()
        if response != "yes":
            break

game.display_statistics()

# Calculate and display the average number of attempts per game.
average_attempts = game.display_average_attempts()
print(f"Avg. attempts: {average_attempts:.2f}")