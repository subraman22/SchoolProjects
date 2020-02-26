Hunt the Wumpus game with ML implementation of weather dataset
Adapted from https://github.com/greeder59/Wumpus/blob/master/wumpus.py
CS 5100 Project 3
Fall 2019
Rohan Subramaniam
11/30/19


In this game implementation, the Player is the agent going through the Wumpus cave.
The performance measure would be the end state of the game. If the Wumpus dies, the player wins, and if the player dies to a pit or Wumpus, they lose.
The environment consists of a 20 room cave set up in two rings of 10. Rooms 1-10 are connected to a left and right neighbor in a ring, as are 11-20.
Also, 1 connects to 11, 2 to 12, 3 to 13 etc.
The actuators include the agent's possibility to move to or shoot at any adjacent room. Actions are validated to make sure the room is valid
The sensors include the stench of the Wumpus, the draft from pits, and the presence of bats.

I made the following modifications:
- Import the weather dataset as training data for a decision tree, SVM, and ANN
- Assign a random weather (within the range of training data) to each room
- If the player decides to shoot, use the three ML models to predict whether they can shoot or not
    - If at least two of the models return 1, the player can shoot. Otherwise they can't
- Added a few print statements to display the weather and the number of arrows remaining to have a more descriptive description

Since the training set only has 14 instances of data, the models generated were not incredibly accurate, which makes the ensemble decision more important.
The SVM averaged around 70-80% accuracy with a linear model and the ANN converges at 64% accuracy, but operates in the range of 35-78%.
