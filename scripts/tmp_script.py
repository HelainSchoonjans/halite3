#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Position

import random
import logging

# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("MyPythonBot")


def new_position(position, direction):
    return position.directional_offset(direction)


def smart_navigate(game_map, ship, destination):
    """Uses naive navigate, but takes into account the movement of allied ships."""
    direction = game_map.naive_navigate(ship, destination)
    return direction


def smart_navigate2(game_map, ship, destination):
    """
    Returns a singular safe move towards the destination.

    :param ship: The ship to move.
    :param destination: Ending position
    :return: A direction.
    """
    # No need to normalize destination, since get_unsafe_moves
    # does that
    for direction in self.get_unsafe_moves(ship.position, destination):
        target_pos = ship.position.directional_offset(direction)
        if not game_map[target_pos].is_occupied:
            game_map[target_pos].mark_unsafe(ship)
            return direction

    return Direction.Still


while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.halite_amount > 0.9 * constants.MAX_HALITE:
            direction = smart_navigate(game_map, ship, game.me.shipyard.position)
            command_queue.append(ship.move(direction))
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
            direction = smart_navigate(game_map, ship, ship.position + Position(random.choice([-2, 2]), random.choice([-2, 2])))
            command_queue.append(ship.move(direction))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= 16 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
