import datetime
import logging
from copy import deepcopy
from queue import Queue


class Node:
    def __init__(self, game, move, player, player_moved):
        self.game = game
        self.move = move
        self.player = player
        self.player_moved = player_moved
        self.value = None
        self.children = []

    def count_value(self):
        res = 0
        for piece in self.game.board.pieces:
            if piece.captured:
                continue
            if piece.king:
                if piece.player == self.player:
                    res += 4
                else:
                    res -= 4
            else:
                if piece.player == self.player:
                    res += 1
                else:
                    res -= 1
        self.value = res

    def add_children(self, children):
        self.children.append(children)


class Minimax:
    def __init__(self):
        self.player_num = None

    def find_best_move(self, available_time, game):
        logging.debug("Try find_best_move")
        self.player_num = game.whose_turn()
        start_time = datetime.datetime.now()
        logging.debug(f"start_time = {start_time}, available_time = {available_time}")
        root_node = self.create_tree(game, start_time + datetime.timedelta(milliseconds=(available_time - 2.0) * 1000))
        best_move = self.choice_best_move(root_node)
        logging.debug(f"Return best move({best_move})")
        return best_move

    def create_tree(self, game, available_time_to):
        logging.debug(f"Try create_tree, available_time_to = {available_time_to}")
        root = Node(game, None, self.player_num, 2 if self.player_num is 1 else 1)
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
            player_moved = copy_game.whose_turn()
            copy_game.move(move)
            new_node = Node(copy_game, move, self.player_num, player_moved)
            node.add_children(new_node)
            node_init_queue.put(new_node)

    def choice_best_move(self, root_node):
        self.iterative_deep_alpha_beta(root_node, -100, 100)

        for node in root_node.children:
            if node.value is root_node.value:
                return node.move

    def iterative_deep_alpha_beta(self, node, alpha, beta):
        if len(node.children) is 0:
            node.count_value()
            return node.value
        if node.player_moved is not self.player_num:
            node.value = -100
            for child in node.children:
                node.value = max(node.value, self.iterative_deep_alpha_beta(child, alpha, beta))
                alpha = max(alpha, node.value)
                if alpha > beta:
                    break
        else:
            node.value = 100
            for child in node.children:
                node.value = min(node.value, self.iterative_deep_alpha_beta(child, alpha, beta))
                beta = min(alpha, node.value)
                if beta < alpha:
                    break
        return node.value
