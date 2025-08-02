import random

class NumberGuessingGame:
    """
    A number guessing game where the player tries to guess a randomly generated number between 0-9.

    Attributes:
        target_number (int): The randomly generated number for the current game.
        attempts (int): The total number of attempts made by the player.
        wins (int): The number of games won by the player.
        average_attempts (float): The average number of attempts made per game.
        games_played (int): The total number of games played.

    Methods:
        start_new_game: Start a new game and generate a random target number.
        make_guess: Make a guess for the current target number and provide feedback.
        display_statistics: Display the current game statistics.
    """

    def __init__(self):
        """
        Initialize the NumberGuessingGame class with default values for attributes.
        """
        self.target_number = 0
        self.attempts = 0
        self.wins = 0
        self.average_attempts = 0.0
        self.games_played = 0

    def start_new_game(self) -> None:
        """
        Start a new game by generating a random target number and reset the statistics.
        """
        self.target_number = random.randint(0, 9)
        self.attempts = 0
        self.wins = 0

    def make_guess(self, guess: int) -> str:
        """
        Make a guess for the current target number and provide feedback.

        Args:
            guess (int): The player's guess for the current target number.

        Returns:
            str: Feedback message indicating whether the guess is correct, too high or too low.
        """
        if guess < 0 or guess > 9:
            return "Invalid input. Please enter a number between 0-9."

        self.attempts += 1

        if guess == self.target_number:
            self.wins += 1
            return f"Congratulations! You won in {self.attempts} attempts."
        elif guess < self.target_number:
            return "Too low. Try again!"
        else:
            return "Too high. Try again!"

    def display_statistics(self) -> None:
        """
        Display the current game statistics.
        """
        if self.games_played == 0:
            print("No games played yet.")
        else:
            print(f"Games played: {self.games_played}")
            print(f"Wins: {self.wins} ({(float(self.wins) / (self.games_playd) * 100):.2f}% wins)")
            print(f"Average attempts per game: {(float(self.attempts) / self.games_played):.2f}")

    @property
    def games_played(self) -> int:
        """
        Get the total number of games played.

        Returns:
            int: The total number of games played.
        """
        return self._games_played

    @games_played.setter
    def games_played(self, value: int) -> None:
        if value >= 0:
            self._games_played = value
        else:
            raise ValueError("Games played cannot be negative.")

# Test the class
game = NumberGuessingGame()
print(game.start_new_game())
for _ in range(5):
    game.make_guess(7)
    print(game.display_statistics())