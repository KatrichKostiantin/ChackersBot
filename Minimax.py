import datetime
import logging
import random
from copy import deepcopy
from queue import Queue

from monkey_patched.game import Game


class Node:
    def __init__(self, game, move):
        self.game = game
        self.move = move
        self.value = None
        self.children = []

    def count_value(self):
        return 0

    def add_children(self, children):
        self.children.append(children)


class Minimax:
    def find_best_move(self, available_time, game):
        logging.debug("Try find_best_move")
        player_num = game.whose_turn()
        start_time = datetime.datetime.now()
        logging.debug(f"start_time = {start_time}, available_time = {available_time}")
        root_node = self.create_tree(game, start_time + datetime.timedelta(milliseconds=(available_time - 0.7) * 1000))
        best_move = random.choice(root_node.children).move
        logging.debug(f"Return best move({best_move})")
        return best_move

    def create_tree(self, game, available_time_to):
        logging.debug(f"Try create_tree, available_time_to = {available_time_to}")
        root = Node(game, None)
        node_init_queue = Queue(maxsize=99999999)
        node_init_queue.put(root)
        self.recursive_child_creation(node_init_queue, available_time_to)
        return root

    def recursive_child_creation(self, node_init_queue, available_time_to):
        while datetime.datetime.now() < available_time_to:
            node = node_init_queue.get()
            self.creating_node_children(node, node_init_queue, available_time_to)
        logging.debug(f"End recursive_child_creation on {datetime.datetime.now()}")

    def creating_node_children(self, node, node_init_queue, available_time_to):
        for move in node.game.get_possible_moves():
            if datetime.datetime.now() > available_time_to:
                return
            copy_game = deepcopy(node.game)
            copy_game.move(move)
            new_node = Node(copy_game, move)
            node.add_children(new_node)
            node_init_queue.put(new_node)
