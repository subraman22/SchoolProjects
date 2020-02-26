"""
Hunt the Wumpus game with ML implementation of weather dataset
Adapted from https://github.com/greeder59/Wumpus/blob/master/wumpus.py
CS 5100 Project 3
Fall 2019
Rohan Subramaniam
11/30/19
"""


import random
import sys
from sklearn import tree
from sklearn.svm import SVC
from keras.models import Sequential
from keras.layers import Dense
from numpy import loadtxt


def show_instructions():
    print("""
        WELCOME TO 'HUNT THE WUMPUS'
        THE WUMPUS LIVES IN A CAVE OF 20 ROOMS. EACH ROOM
        HAS 3 TUNNELS LEADING TO OTHER ROOMS. (LOOK AT A
        DODECAHEDRON TO SEE HOW THIS WORKS-IF YOU DON'T KNOW
        WHAT A DODECHADRON IS, ASK SOMEONE, or Google it.)

    HAZARDS:
        BOTTOMLESS PITS: TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
        IF YOU GO THERE, YOU FALL INTO THE PIT (& LOSE!)
        SUPER BATS: TWO OTHER ROOMS HAVE SUPER BATS. IF YOU
        GO THERE, A BAT GRABS YOU AND TAKES YOU TO SOME OTHER
        ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)
    WUMPUS:
        THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER
        FEET AND IS TOO BIG FOR A BAT TO LIFT). USUALLY
        HE IS ASLEEP. TWO THINGS THAT WAKE HIM UP: YOUR ENTERING
        HIS ROOM OR YOUR SHOOTING AN ARROW.
        IF THE WUMPUS WAKES, HE MOVES (P=.75) ONE ROOM
        OR STAYS STILL (P=.25). AFTER THAT, IF HE IS WHERE YOU
        ARE, HE TRAMPLES YOU (& YOU LOSE!).
    YOU:
        EACH TURN YOU MAY MOVE OR SHOOT AN ARROW
        MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
        ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN
        OUT. YOU AIM BY TELLING
        THE COMPUTER THE ROOM YOU WANT THE ARROW TO GO TO.
        IF THE WEATHER IN THE ROOM DOES NOT PERMIT, YOU CANNOT SHOOT
        IF THE ARROW HITS THE WUMPUS, YOU WIN.
    WARNINGS:
        WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OR A HAZARD,
        THE COMPUTER SAYS:
        WUMPUS:   'I SMELL A WUMPUS'
        BAT   :   'BATS NEAR BY'
        PIT   :   'I FEEL A DRAFT'
        """)


class Room:
    """Defines a room.
    A room has a name (or number),
    a list of other rooms that it connects to.
    and a description.
    How these rooms are built into something larger
    (cave, dungeon, skyscraper) is up to you.
    """

    def __init__(self, **kwargs):
        self.number = 0
        self.name = ''
        self.connects_to = []  # These are NOT objects
        self.description = ""
        self.weather = Weather()  # generates a random weather pattern for the room

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return str(self.number)

    def remove_connect(self, arg_connect):
        if arg_connect in self.connects_to:
            self.connects_to.remove(arg_connect)

    def add_connect(self, arg_connect):
        if arg_connect not in self.connects_to:
            self.connects_to.append(arg_connect)

    def is_valid_connect(self, arg_connect):
        return arg_connect in self.connects_to

    def get_number_of_connects(self):
        return len(self.connects_to)

    def get_connects(self):
        return self.connects_to

    def describe(self):
        if len(self.description) > 0:
            print(self.description)
        else:
            print("You are in room {}.\nPassages lead to {}".format(self.number, self.connects_to))
            self.weather.print_weather()


class Thing:
    """Defines the things that are in the cave.
    That is the Wumpus, Player, pits and bats.
    """

    def __init__(self, **kwargs):
        self.location = 0  # this is a room object

        for key, value in kwargs.items():
            setattr(self, key, value)

    def move(self, a_new_location):
        if a_new_location.number in self.location.connects_to or a_new_location == self.location:
            self.location = a_new_location
            return True
        else:
            return False

    def validate_move(self, a_new_location):
        return a_new_location.number in self.location.connects_to or a_new_location == self.location

    def get_location(self):
        return self.location.number

    def wakeup(self, a_cave):
        if random.randint(0, 3):  # P=.75 that we will move.
            self.location = a_cave[random.choice(self.location.connects_to) - 1]

    def is_hit(self, a_room):
        return self.location == a_room


def create_things(a_cave):
    Things = []
    Samples = random.sample(a_cave, 6)
    for room in Samples:
        Things.append(Thing(location=room))

    return Things


def create_cave():
    # First create a list of all the rooms.
    for number in range(20):
        Cave.append(Room(number=number + 1))

    # Then stitch them together.
    for idx, room in enumerate(Cave):

        # connect to room to the right
        if idx == 9:
            room.add_connect(Cave[0].number)
        elif idx == 19:
            room.add_connect(Cave[10].number)
        else:
            room.add_connect(Cave[idx + 1].number)

        # connect to the room to the left
        if idx == 0:
            room.add_connect(Cave[9].number)
        elif idx == 10:
            room.add_connect(Cave[19].number)
        else:
            room.add_connect(Cave[idx - 1].number)

        # connect to the room in the other ring
        if idx < 10:
            room.add_connect(Cave[idx + 10].number)  # I connect to it.
            Cave[idx + 10].add_connect(room.number)  # It connects to me.


class Weather:
    """
    Weather for each room in the cave. Randomly generated when creating the rooms
    outlook: 0 for sunny, 1 for overcast, 2 for rainy
    temperature: random int from 65-85
    humidity: random int from 65-96
    windy: 0 for false 1 for true
    """

    def __init__(self):
        self.outlook = random.randint(0, 2)
        self.temperature = random.randint(65, 85)
        self.humidity = random.randint(65, 96)
        self.windy = random.randint(0, 1)
        self.outlook_str = self.coded_outlook()

    def attribute_list(self):
        return [self.outlook, self.temperature, self.humidity, self.windy]

    def coded_outlook(self):
        if self.outlook == 0:
            return "sunny"
        elif self.outlook == 1:
            return "overcast"
        else:
            return "rainy"

    def print_weather(self):
        print("Weather in the room is {}. {} degrees with {}% humidity and {} wind".format(
            self.outlook_str, self.temperature, self.humidity, "no" if self.windy == 0 else "high"))


class Predictions:
    """
    class for the decision tree, SVM, and ANN.
    Will load the data all once and then can use this class to predict based on the weather of each room
    Saves the predictors as instance variables for use predicting each timestep

    """
    def __init__(self):
        self.X = loadtxt("weather_coded.csv", usecols=(0, 1, 2, 3), delimiter=",")
        self.y = loadtxt("weather_coded.csv", usecols=4, delimiter=",")
        self.tree = self.decision_tree()
        self.svc = self.SVM()
        self.neural_net = self.ANN()

    def predict_tree(self, x):
        return int(self.tree.predict(x))

    def predict_SVM(self, x):
        return int(self.svc.predict(x))

    def predict_ANN(self, x):
        return int(self.neural_net.predict_classes([x]))

    def vote(self, x):
        """
        totals up the predictions from all three models. returns the decision of the majority.
        2 or 3 mean True, 0 or 1 means False
        :param x: room weather for the prediction
        :return: True or False of whether the player can shoot or not
        """
        tree_vote = self.predict_tree(x)
        SVM_vote = self.predict_SVM(x)
        ANN_vote = self.predict_ANN(x)
        total_vote = tree_vote + SVM_vote + ANN_vote
        print("Decision Tree prediction: {}".format("Shoot" if tree_vote == 1 else "No Shoot"))
        print("Support Vector Machine prediction: {}".format("Shoot" if SVM_vote == 1 else "No Shoot"))
        print("Artificial Neural Network prediction: {}".format("Shoot" if ANN_vote == 1 else "No Shoot"))
        return True if total_vote > 1 else False

    def decision_tree(self):
        decision_tree = tree.DecisionTreeClassifier()
        decision_tree.fit(self.X, self.y)
        return decision_tree

    def SVM(self):
        """
        linear kernal resulted in the best accuracy over multiple runs
        :return: the SVC classifier object
        """
        svc_classifier = SVC(kernel="linear")
        svc_classifier.fit(self.X, self.y)

        return svc_classifier

    def ANN(self):
        """
        3 layer neural network for predicting shot conditions. Converges at 64% accuracy usually, but
        ranges from 35% to 78% run to run
        :return: the neural network model
        """
        model = Sequential()
        model.add(Dense(15, input_dim=4, activation="relu"))
        model.add(Dense(10, activation="relu"))
        model.add(Dense(1, activation="sigmoid"))
        model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
        model.fit(self.X, self.y, batch_size=10, epochs=500, verbose=0)
        _, accuracy = model.evaluate(self.X, self.y, verbose=0)
        print('Accuracy: %.2f' % (accuracy * 100))
        return model

# ============ BEGIN HERE ===========


Cave = []
create_cave()
predictor = Predictions()


# Make player, wumpus, bats, pits and put into cave.

Wumpus, Player, Pit1, Pit2, Bats1, Bats2 = create_things(Cave)

Arrows = 5

# Now play the game

print("""\n   Welcome to the cave, Great White Hunter.
    You are hunting the Wumpus.
    On any turn you can move or shoot.
    Commands are entered in the form of ACTION LOCATION
    IE: 'SHOOT 12' or 'MOVE 8'
    type 'HELP' for instructions.
    'QUIT' to end the game.
    """)

while True:
    Player.location.describe()
    print("You have {} arrows remaining".format(Arrows))
    # Check each <Player.location.connects_to> for hazards.
    for room in Player.location.connects_to:
        if Wumpus.location.number == room:
            print("I smell a Wumpus!")
        if Pit1.location.number == room or Pit2.location.number == room:
            print("I feel a draft!")
        if Bats1.location.number == room or Bats2.location.number == room:
            print("Bats nearby!")

    raw_command = input("\n> ")
    command_list = raw_command.split(' ')
    command = command_list[0].upper()
    if len(command_list) > 1:
        try:
            move = Cave[int(command_list[1]) - 1]
        except:
            print("\n **What??")
            continue
    else:
        move = Player.location

    if command == 'HELP' or command == 'H':
        show_instructions()
        continue

    elif command == 'QUIT' or command == 'Q':
        print("\nOK, Bye.")
        sys.exit()

    elif command == 'MOVE' or command == 'M':
        if Player.move(move):
            if Player.location == Wumpus.location:
                print("... OOPS! BUMPED A WUMPUS!")
                Wumpus.wakeup(Cave)
        else:
            print("\n **You can't get there from here")
            continue

    elif command == 'SHOOT' or command == 'S':
        # first check if the player can even shoot
        can_shoot = predictor.vote([Player.location.weather.attribute_list()])
        if not can_shoot:
            print("\nWeather in this room does not permit shooting, you must move")
            continue
        if Player.validate_move(move):
            print("\n-Twang-")
            if Wumpus.location == move:
                print("\n Good Shooting!! You hit the Wumpus. \n Wumpi will have their revenge.\n")
                sys.exit()
        else:
            print("\n** Stop trying to shoot through walls.")

        Wumpus.wakeup(Cave)
        Arrows -= 1
        if Arrows == 0:
            print("\n You are out of arrows\n Better luck next time\n")
            sys.exit()

    else:
        print("\n **What?")
        continue

    # By now the player has moved. See what happened.
    # Handle problems with pits, bats and wumpus.

    if Player.location == Bats1.location or Player.location == Bats2.location:
        print("Oh no! Bats snatched you and carried you to a different room\n")
        Player.location = random.choice(Cave)

    if Player.location == Wumpus.location:
        print("Stomp! The Wumpus got you! Game over\n")
        sys.exit()

    elif Player.location == Pit1.location or Player.location == Pit2.location:
        print("You fell into a pit and died. Game over\n")
        sys.exit()

    else:  # Keep playing
        continue
