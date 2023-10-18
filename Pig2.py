import sys
import argparse
import random
import time
from queue import Queue


class Players(object):


    def __init__(self, players):
        self.__players = players
        self.__current_player = players.get()

    def get_current_player(self):
        # Return the current player
        return self.__current_player

    def get_next_player(self):
        # Add current player back to the end of the queue
        self.__players.put(self.__current_player)
        # Get the next player from the queue and return it
        self.__current_player = self.__players.get()
        return self.__current_player

    def get_players(self):
        # Add current player back to the queue before returning the players
        self.__players.put(self.__current_player)
        return self.__players


class Player(object):

    def __init__(self, name):
        self.__name = name.strip()
        self.__score = 0
        self.__rolls = 0

    def get_name(self):
        # Return the player's name
        return self.__name

    def get_score(self):
        # Return the player's score
        return self.__score

    def get_rolls(self):
        # Return the player's rolls
        return self.__rolls

    def commit_score(self, score, rolls):
        # Update the player's score and roll count
        self.__score += score
        self.__rolls += rolls

class ComputerPlayer(Player):
    def request_action(self):
        # Determine the computer player's desired action
        action = "r" if self._current_score < min(25, (100 - (self._total_score + self._current_score))) else "h"
        # Return the action
        return action

class PlayerFactory:

    def get_player(self, player_name, player_type):

        # Return correct player class
        if player_type == "human":
             return Player(player_name)
        if player_type == "computer":
             return ComputerPlayer(player_name)


class Die(object):

    def __init__(self):
        # Set the seed to 0
        random.seed(0)

    def roll(self):
        # Return a random integer between 1 and 6
        return random.randint(1, 6)


class Game(object):
    def __init__(self, players):
        # Instantiate a Players object with the players queue
        self.__players = Players(players)
        # Instantiate the Die to be used for the current game
        self.__die = Die()

    def start(self):
        # Call the private __turn method to start the game
        self.__turn()

    def _accounce_winner(self):
        winner = sorted(((player.get_name(), player.get_last_roll(), player.get_total_score())
                         for player in self._players.get_players()),
                        key=lambda player: (player[1]),
                        reverse=True)[0]

        print("\n\nCongratulations {}, you rolled a {} and your total score is {}. You won the game!"
              .format(winner[0], winner[1], winner[2]))

    def __game_over(self):
        # Get the players and create the leaderboard tuple
        leaderboard = ((player.get_name(), player.get_score(), player.get_rolls())
                       for player in list(self.__players.get_players().queue))

        print("\nLEADERBOARD\n")
        # Print leaderboard header border
        print("+-{:<32}-+-{:>10}-+-{:>10}-+".format("-"*32, "-"*10, "-"*10))
        # Print the leaderboard header
        print("| {:<32} | {:>10} | {:>10} |".format(
            'Player', 'Score', '# of Rolls'))
        # Sort by highest scores first and print the details
        for player in sorted(leaderboard,
                             key=lambda player: (player[1]),
                             reverse=True):
            # Print the cell separators
            print("|-{:<32}-+-{:>10}-+-{:>10}-|".format("-"*32, "-"*10, "-"*10))
            # Print the player's details
            print("| {:<32} | {:>10} | {:>10} |".format(
                player[0], player[1], player[2]))

        # Print leaderboard footer border
        print("+-{:<32}-+-{:>10}-+-{:>10}-+".format("-"*32, "-"*10, "-"*10))

    def _play(self, player):
        # Request the current player's desired action
        action = player.request_action()

        # Player chose to roll
        if action == "r":
            # Roll the die and add to roll total for the turn
            roll = self._die.roll()
            player.update_total_rolls()
            player.update_last_roll(roll)
            if roll == 1:
                player.reset_turn_stats()
                player.commit_score()
                print(
                    "Ouch {}, you rolled a {} and lost all points you accumulated during this turn. Your score for this turn is {}. Your total score is {}.".format(
                        player.get_name(), roll, player.get_current_score(), player.get_total_score()))
                self._active_turn = False
            else:
                player.update_turn_score(roll)
                if (player.get_current_score() + player.get_total_score()) >= 100:
                    player.commit_score()
                    player.reset_turn_stats()
                    self._end_game, self._active_turn = True, False
                else:
                    print(
                        "Nice {}! You rolled a {}. Your current score for this turn is {}. Your total score is {}".format(
                            player.get_name(),
                            roll,
                            player.get_current_score(),
                            player.get_current_score() + player.get_total_score()
                        )
                    )
        elif action == "h":
            player.commit_score()
            print("{}, you held. Your score for this turn is {}. Your total score is {}.".format(
                player.get_name(), player.get_current_score(), player.get_total_score()))
            player.reset_turn_stats()
            self._active_turn = False
        else:
            print("You entered an invalid action.")


    def __turn(self, next_player=False):
        # Get the player for the current turn
        player = self.__players.get_current_player(
        ) if not next_player else self.__players.get_next_player()
        # Keep track of the current score and rolls
        current_score = 0
        rolls = 0
        # Keep track of the turn and game status
        active_turn = True
        game_over = False
        # Let the players know who's turn it is
        print("\n{}, it's your turn. Your current score is {}".format(
            player.get_name(), player.get_score()))

        while active_turn and not game_over:
            # Request the current player's desired action
            action = input(
                "Enter 'r' to roll the die, or 'h' to hold. What you you like to do? ")

            # Player chose to roll
            if action == "r":
                # Roll the die and add to roll total for the turn
                roll = self.__die.roll()
                rolls += 1

                if roll == 1:
                    current_score = 0
                    player.commit_score(current_score, rolls)
                    print("Ouch, {} you rolled a {} and lost all points you accumulated during this turn. Your score for this turn is {}. Your total score is {}.".format(
                        player.get_name(), roll, current_score, player.get_score()))
                    active_turn = False

                else:
                    current_score += roll
                    if (current_score + player.get_score()) >= 100:
                        player.commit_score(current_score, rolls)
                        print("\n\nCongratulations {}, you rolled a {} and your total score is {}. You won the game!"
                              .format(player.get_name(), roll, player.get_score()))
                        game_over, active_turn = True, False
                    else:
                        print("Nice {}! You rolled a {}. Your current score for this turn is {}. Your total score is {}".format(
                            player.get_name(),
                            roll,
                            current_score,
                            current_score + player.get_score()
                        )
                        )

            elif action == "h":
                player.commit_score(current_score, rolls)
                print("{}, you held. Your score for this turn is {}. Your total score is {}.".format(
                    player.get_name(), current_score, player.get_score()))
                active_turn = False
            # The player entered an invalid action
            else:
                print("You entered an invalid action.")

        if not game_over:
            self.__turn(True)
        else:
            self.__game_over()

class TimedGame(Game):

    def start(self):
        # Call the protected _turn method to start the game
        self._end_time = time.time() + 60
        self._turn()

    def _accounce_winner(self):
        if self._end_time < time.time():
            winner = sorted(((player.get_name(), player.get_last_roll(), player.get_total_score())
                             for player in self._players.get_players()),
                            key=lambda player: (player[1]),
                            reverse=True)[0]

            print("\n\nCongratulations {}, you had the highest score of {} before time ran out. You won the game!"
                  .format(winner[0], winner[2]))
        else:
            super()._accounce_winner()

    def _play(self, player, time_left):
        print("There are {} seconds left in this game.".format(time_left))
        super()._play(player)

    def _turn(self, next_player=False):
        # Get the player for the current turn
        player = self._players.get_current_player(
        ) if not next_player else self._players.get_next_player()

        # Reset the _active_turn attribute to True
        self._active_turn = True

        # Let the players know who's turn it is
        print("\n{}, it's your turn. Your current score is {}".format(
            player.get_name(), player.get_total_score()))

        while self._active_turn and not self._end_game and time.time() < self._end_time:
            self._play(player, round(self._end_time - time.time(), 0))

        if time.time() >= self._end_time:
            self._end_game = True
            self._active_turn = False
        if not self._end_game:
            self._turn(True)
        else:
            self._accounce_winner()
            self._game_over()

class TimedGameProxy(Game):
    def __init__(self, players):
        self._players = players
        self._game = None

    def start(self, timed):
        if timed:
            self._game = TimedGame(self._players)
        else:
            self._game = Game(self._players)

        self._game.start()

def main():

    # Setup arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--player1',
                        help='Player 1 type, computer or human.',
                        type=str
                        )
    parser.add_argument('--player2',
                        help='Player 2 type, computer or human.',
                        type=str
                        )
    parser.add_argument('--timed',
                        action='store_true',
                        help='Whichever player has the most points after one minute wins the game.'
                        )
    args = parser.parse_args()

    # Check for required arguments and correct values
    if not args.player1 and not args.player2:
        print(
            "The --player1 and --player2 arguments are required. Valid types are computer or human. Please try again.")
        sys.exit()

    if not args.player1.lower() == "computer" and not args.player1.lower() == "human":
        print("You entered an invalid player type for player1. Valid types are computer or human. Please try again.")
        sys.exit()

    if not args.player2.lower() == "computer" and not args.player2.lower() == "human":
        print("You entered an invalid player type for player2. Valid types are computer or human. Please try again.")
        sys.exit()

    # Create a queue for the players
    players = Queue()

    # Ask for player names if they are human
    player1_name = "Computer [Player 1]" if args.player1.lower() == "computer" \
        else input("What is Player 1's name? ")

    player2_name = "Computer [Player 2]" if args.player2.lower() == "computer" \
        else input("What is Player 2's name? ")

    # Use PlayerFactory to get correct player classes and add to players queue
    players.put(PlayerFactory().get_player(player1_name, args.player1.lower()))
    players.put(PlayerFactory().get_player(player2_name, args.player2.lower()))

    # Use GameFactory to get correct game class and start the game
    TimedGameProxy(players).start(args.timed)

    # Exit the program after the game is over
    sys.exit()


if __name__ == '__main__':
    main()