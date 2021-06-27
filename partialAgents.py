# partialAgent.py
# parsons/15-oct-2017
#
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class PartialAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up!"
        name = "Pacman"

        #Boolean indicators for which corners are already visited
        self.visitedTopRight = False
        self.visitedBotRight = False
        self.visitedBotLeft = False
        self.visitedTopLeft = False

        #Containers for the last action Pacman actually did
        self.lastAction = Directions.STOP


        #Variables that will store the arena dimensions bounds
        self.xUpper = 0
        self.yUpper = 0
        self.xLower = 500
        self.yLower = 500

        #list of pairs that will keep record of the food that was seen, but not eaten
        self.availableFood = []




    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like I just died!"


    def getAction(self, state):

        self.corners = api.corners(state)

        #Get corner coordinates And set dimension variables
        for corner in self.corners:
            x = corner[0]
            y = corner[1]

            if self.xLower > x:
                self.xLower = x
            if self.xUpper < x:
                self.xUpper = x
            if self.yLower > y:
                self.yLower = y
            if self.yUpper < y:
                self.yUpper = y

        #Variables always pointing current location and legal actions for next move
        location = api.whereAmI(state)
        legalActions = api.legalActions(state)

        #Not allowing Pacman to stop, as Stop is always an option
        if Directions.STOP in legalActions :
            legalActions.remove(Directions.STOP)


        #checking if Pacman is at a position of available food, so we can remove it from the available food list
        if location in self.availableFood :
            self.availableFood.remove(location)

        #checking if corners are visited while Pacman was running away from ghosts or seeking food
        if location == (self.xUpper - 1, self.yLower + 1) :
            self.visitedBotRight = True

        if location == (self.xUpper - 1, self.yUpper - 1) :
            self.visitedTopRight = True

        if location == (self.xLower + 1, self.yUpper - 1) :
            self.visitedTopLeft = True

        if location == (self.xLower + 1, self.yLower + 1) :
            self.visitedBotLeft = True

        #Variables holding the positions of all visible food and ghosts(capuseles are treated as food)
        ghostPositions = api.ghosts(state)
        foodPositions = api.food(state)

        #if there is visible food, add it to the available food list
        if len(foodPositions) != 0 :
            for food in foodPositions :
                if not food in self.availableFood :
                    self.availableFood.append(food)

        #and then after that we add the capsule to the food list, so it doesnt go into the available food
        #if there is visible capsule, we add it to the food list
        if len(api.capsules(state)) != 0 :
            foodPositions.__add__(api.capsules(state))
        #creating empty dictionary, which will hold manhattan distances(sum of absolute differences of their coordintaes) to the ghosts as a key and their coordinates as value of the entry
        ghostDistances = {}
        closestGhostCoordinates = (0,0)

        #the first priority when pacman moves is running away from ghosts, that's why the first thing we check is if there are any ghosts in sight
        if len(ghostPositions) != 0:
            # For loop so in case there is more than 1 visible ghost, we can find the closest one and focus on running away from him
            for ghost in ghostPositions:
                # temp variable for the distance to the given ghost
                key = abs(location[0] - ghost[0]) + abs(location[1] - ghost[1])
                # add entry to the dictionary
                ghostDistances.update({key: ghost})
            # Getting the smallest value in the sorted list of keys
            closestGhost = sorted(ghostDistances.keys())[0]
            # Finding the value corresponding to that key
            closestGhostCoordinates = ghostDistances[closestGhost]

            # The actual part the makes Pacman run from the ghost

            #As Pacman doesn't see around corners, I will only check the cases, where Pacman and the ghost have same coordinates along of the axis
            if location[0] == closestGhostCoordinates[0]:
                #if they have same coordinates, along the x axis and the ghost is on the south from Pacman
                if location[1] > closestGhostCoordinates[1]:
                    #if going south(towards the ghost) is possible, we remove it from the set of possible actions, so Pacman would never go straight to the ghost, even if random action is applied
                    if Directions.SOUTH in legalActions:
                        legalActions.remove(Directions.SOUTH)

                    #the very first thing we try, if possible, is to run to the opposite way from the ghost
                    if Directions.NORTH in legalActions:
                        #if possible we record what action will ne performed and return
                        self.lastAction = Directions.NORTH
                        return api.makeMove(Directions.NORTH, legalActions)
                    #if running to the opposite side is not possible, we can safely do a random action, as STOP and running towards the ghost are no longer in the list
                    else:
                        #Forcing pacman to stop added, bcause of bug, caused by pacman being stuck and having only the directions where the ghost is as possible action(which we removed early)
                        if len(legalActions) == 0 :
                            return api.makeMove(Directions.STOP, api.legalActions(state))
                        else :
                            choice = random.choice(legalActions)
                            self.lastAction = choice
                            return api.makeMove(choice, legalActions)
                #if the y coordinate of Pacman isn't bigger than the y coordinate of Pacman, i.e. ghost is above Pacman, we exactly the opposite thing
                else:
                    if Directions.NORTH in legalActions:
                        legalActions.remove(Directions.NORTH)

                    if Directions.SOUTH in legalActions:
                        self.lastAction = Directions.SOUTH
                        return api.makeMove(Directions.SOUTH, legalActions)
                    else:
                        if len(legalActions) == 0 :
                            return api.makeMove(Directions.STOP, api.legalActions(state))
                        else :
                            choice = random.choice(legalActions)
                            self.lastAction = choice
                            return api.makeMove(choice, legalActions)
            if location[1] == closestGhostCoordinates[1] :
                if location[0] > closestGhostCoordinates[0]:
                    if Directions.WEST in legalActions:
                        legalActions.remove(Directions.WEST)

                    if Directions.EAST in legalActions:
                        self.lastAction = Directions.EAST
                        return api.makeMove(Directions.EAST, legalActions)
                    else:
                        if len(legalActions) == 0 :
                            return api.makeMove(Directions.STOP, api.legalActions(state))
                        else :
                            choice = random.choice(legalActions)
                            self.lastAction = choice
                            return api.makeMove(choice, legalActions)
                else:
                    if Directions.EAST in legalActions:
                        legalActions.remove(Directions.EAST)

                    if Directions.WEST in legalActions:
                        self.lastAction = Directions.WEST
                        return api.makeMove(Directions.WEST, legalActions)
                    else:
                        if len(legalActions) == 0 :
                            return api.makeMove(Directions.STOP, api.legalActions(state))
                        else :
                            choice = random.choice(legalActions)
                            self.lastAction = choice
                            return api.makeMove(choice, legalActions)
        #for navigating Pacman to the closest food, the approach will be similar to running away from the ghost
        foodDistances = {}
        closestFoodCoordinates = (0,0)

        #as eating all the food is our second priority, after making sure there are no ghosts in sight, we if there is visible food and where is the closest one
        if len(foodPositions) != 0:
            #for finding the closest food, the exact same logic is used, as finding the closest ghost
            for food in foodPositions :
                key = abs(location[0] - food[0]) + abs(location[1] - food[1])
                foodDistances.update({key : food})
            closestFood = sorted(foodDistances.keys())[0]
            closestFoodCoordinates = foodDistances[closestFood]

            # again we have two main cases, one for each axis
            if closestFoodCoordinates[0] == location[0]:
                # if food is above Pacman, we move North, we don't have back up option if Pacman cannot move North, because if he sses food to the North, he for sure can move North, as he never stops to look back
                if closestFoodCoordinates[1] > location[1]:
                    if Directions.NORTH in legalActions:
                        self.lastAction = Directions.NORTH
                        return api.makeMove(Directions.NORTH, legalActions)
                # if food is below Pacman, we move South
                else:
                    if Directions.SOUTH in legalActions:
                        self.lastAction = Directions.SOUTH
                        return api.makeMove(Directions.SOUTH, legalActions)
            # same thing if the food is respectively right and left from Pacman
            if closestFoodCoordinates[1] == location[1]:
                if closestFoodCoordinates[0] > location[0]:
                    if Directions.EAST in legalActions:
                        self.lastAction = Directions.EAST
                        return api.makeMove(Directions.EAST, legalActions)
                else:
                    if Directions.WEST in legalActions:
                        self.lastAction = Directions.WEST
                        return api.makeMove(Directions.WEST, legalActions)

        #if there are no ghosts or food visible, we gonna seek the food he has seen, but not eaten and then its time for some corner seeking



        #Unless Pacman had ghosts in vicinity, we wouldn't allow him to reverse his last action
        #However, there is something else, there are some particular places on the map, which require reversing, so if there is only one possible action in the list, we don't remove it
        if self.lastAction == Directions.NORTH and Directions.SOUTH in legalActions and len(legalActions) != 1:
            legalActions.remove(Directions.SOUTH)
        if self.lastAction == Directions.SOUTH and Directions.NORTH in legalActions and len(legalActions) != 1:
            legalActions.remove(Directions.NORTH)
        if self.lastAction == Directions.EAST and Directions.WEST in legalActions and len(legalActions) != 1:
            legalActions.remove(Directions.WEST)
        if self.lastAction == Directions.WEST and Directions.EAST in legalActions and len(legalActions) != 1:
            legalActions.remove(Directions.EAST)


        availableFoodDistances = {}
        closestAvailableFood = (0,0)

        #if there is food, that's seen, but eaten, we seek it before, randomly seeking corners
        if len(self.availableFood) != 0 :
            #we gonna calculate the distance to the closest available food, using the same approach as for food and ghosts
            for food in self.availableFood :
                key = abs(location[0] - food[0]) + abs(location[1] - food[1])
                availableFoodDistances.update({key : food})
            closestAvailableFood = sorted(availableFoodDistances.keys())[0]
            closestAvailableFoodCoordinates = availableFoodDistances[closestAvailableFood]

            #now actually navigate to the closest food
            #if the food has lower coordinate value along the x axis, try to move WEST
            if location[0] > closestAvailableFoodCoordinates [0] :
                #we add the ectra condition for moving East, to avoid getinng stuck and moving only west and eat
                if Directions.WEST in legalActions and self.lastAction != Directions.EAST :
                    self.lastAction = Directions.WEST
                    return api.makeMove(self.lastAction, state)
                #if west is not available, check the positions along the Y axis and try to move accordingly
                else :
                    if location[1] > closestAvailableFoodCoordinates[1] :
                        if Directions.SOUTH in legalActions :
                            self.lastAction = Directions.SOUTH
                            return api.makeMove(self.lastAction, state)
                        #if the move towards the food along the Y axis is not possible, try the opposite move
                        else :
                            if Directions.NORTH in legalActions :
                                self.lastAction = Directions.NORTH
                                return api.makeMove(self.lastAction, state)
                            #if none of the are possible, we gonna move back(east)
                            if Directions.EAST in legalActions :
                                self.lastAction = Directions.EAST
                                return api.makeMove(self.lastAction, state)
                    # if the coordinates of pacman, along the Y axis are smaller then the food, we do the opposite thing
                    else:
                        if Directions.NORTH in legalActions:
                            self.lastAction = Directions.NORTH
                            return api.makeMove(self.lastAction, state)
                        else:
                            if Directions.SOUTH in legalActions:
                                self.lastAction = Directions.SOUTH
                                return api.makeMove(self.lastAction, state)
                            if Directions.EAST in legalActions:
                                self.lastAction = Directions.EAST
                                return api.makeMove(self.lastAction, state)


            #we act in similar way, if the coordinates along the X axis, are the opposite way
            else :
                if Directions.EAST in legalActions and self.lastAction != Directions.WEST:
                    self.lastAction = Directions.EAST
                    return api.makeMove(self.lastAction, state)
                else:
                    if location[1] > closestAvailableFoodCoordinates[1] :
                        if Directions.SOUTH in legalActions :
                            self.lastAction = Directions.SOUTH
                            return api.makeMove(self.lastAction, state)
                        #if the move towards the food along the Y axis is not possible, try the opposite move
                        else :
                            if Directions.NORTH in legalActions :
                                self.lastAction = Directions.NORTH
                                return api.makeMove(self.lastAction, state)
                            #if none of the are possible, we gonna move back(east)
                            if Directions.WEST in legalActions :
                                self.lastAction = Directions.WEST
                                return api.makeMove(self.lastAction, state)
                    # if the coordinates of pacman, along the Y axis are smaller then the food, we do the opposite thing
                    else:
                        if Directions.NORTH in legalActions:
                            self.lastAction = Directions.NORTH
                            return api.makeMove(self.lastAction, state)
                        else:
                            if Directions.SOUTH in legalActions:
                                self.lastAction = Directions.SOUTH
                                return api.makeMove(self.lastAction, state)
                            if Directions.WEST in legalActions:
                                self.lastAction = Directions.WEST
                                return api.makeMove(self.lastAction, state)

        # if Pacman has been seeking for corners for too long and has visited all of them, we need to reset the booleans, so he can keep going until he eats all the food
        if self.visitedBotLeft and self.visitedBotRight and self.visitedTopRight and self.visitedTopLeft:
            self.visitedBotLeft = False
            self.visitedBotRight = False
            self.visitedTopRight = False
            self.visitedTopLeft = False

        #We gonna start seeking corners anticlockwise from botRight
        #seek bottom right corner
        if not self.visitedBotRight :
            #check if we're not in the corner
            if location != (self.xUpper - 1, self.yLower + 1):
                #when seeking bottom right corner, Pacman will always first try to move East, if not possible, South, then North and then West
                if Directions.EAST in legalActions :
                    self.lastAction = Directions.EAST
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.SOUTH in legalActions:
                    self.lastAction = Directions.SOUTH
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.NORTH in legalActions:
                    self.lastAction = Directions.NORTH
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.WEST in legalActions:
                    self.lastAction = Directions.WEST
                    return api.makeMove(self.lastAction, legalActions)
            #if we're exaclty on the corner, we set the flag to true and perform random action and then on the next iteration Pacman will start seeking another corner, if there are no food and ghosts visible, of course
            else :
                self.visitedBotRight = True
                choice = random.choice(legalActions)
                self.lastAction = choice
                return api.makeMove(choice, legalActions)



        #seek top right corner. sequence of actions is similar - East, North, South, West
        if not self.visitedTopRight:
            if location != (self.xUpper - 1, self.yUpper - 1):
                if Directions.EAST in legalActions:
                    self.lastAction = Directions.EAST
                    return api.makeMove(Directions.EAST, legalActions)

                if Directions.NORTH in legalActions:
                    self.lastAction = Directions.NORTH
                    return api.makeMove(self.lastAction, legalActions)


                if Directions.SOUTH in legalActions:
                    self.lastAction = Directions.SOUTH
                    return api.makeMove(self.lastAction, legalActions)


                if Directions.WEST in legalActions:
                    self.lastAction = Directions.WEST
                    return api.makeMove(Directions.WEST, legalActions)

            else :
                self.visitedTopRight = True
                choice = random.choice(legalActions)
                self.lastAction = choice
                return api.makeMove(choice, legalActions)

        #seek top left corner, West, North, South, East
        if not self.visitedTopLeft :
            if location != (self.xLower + 1, self.yUpper - 1):

                if Directions.WEST in legalActions:
                    self.lastAction = Directions.WEST
                    return api.makeMove(self.lastAction, legalActions)


                if Directions.NORTH in legalActions:
                    self.lastAction = Directions.NORTH
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.SOUTH in legalActions:
                    self.lastAction = Directions.SOUTH
                    return api.makeMove(self.lastAction, legalActions)


                if Directions.EAST in legalActions:
                    self.lastAction = Directions.EAST
                    return api.makeMove(self.lastAction, legalActions)

        else:
            self.visitedTopLeft = True
            choice = random.choice(legalActions)
            self.lastAction = choice
            return api.makeMove(choice, legalActions)

        #seek bottom left corner
        if not self.visitedBotLeft :
            if location != (self.xLower + 1, self.yLower + 1) :
                if Directions.WEST in legalActions:
                    self.lastAction = Directions.WEST
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.SOUTH in legalActions:
                    self.lastAction = Directions.SOUTH
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.NORTH in legalActions:
                    self.lastAction = Directions.NORTH
                    return api.makeMove(self.lastAction, legalActions)

                if Directions.EAST in legalActions:
                    self.lastAction = Directions.EAST
                    return api.makeMove(self.lastAction, legalActions)

            else:
                self.visitedBotLeft = True
                choice = random.choice(legalActions)
                self.lastAction = choice
                return api.makeMove(choice, legalActions)