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
        res = self.curr_stage()
        # for piece in self.game.board.pieces:
        #    if piece.captured:
        #        continue
        #    if piece.king:
        #        if piece.player == self.player:
        #            res += 4
        #        else:
        #           res -= 4
        #    else:
        #        if piece.player == self.player:
        #            res += 1
        #       else:
        #           res -= 1

        self.value = res

    def curr_stage(self):
        num_of_self_pawns = 0
        num_of_enemy_pawns = 0
        num_of_self_kings = 0
        num_of_enemy_kings = 0
        num_enemy_on_edge = 0
        num_self_on_edge = 0
        num_on_top_three = 0
        num_center_king = 0
        num_center_pawn = 0
        num_double_diagonal_king = 0
        for piece in self.game.board.pieces:
            if piece.captured:
                continue
            if piece.king:
                if piece.player == self.player:
                    num_of_self_kings += 1
                else:
                    num_of_enemy_kings += 1

                if self.centrally_positioned(piece.get_row(), piece.get_column()):
                    num_center_king += 1
                if self.on_double_diagonal(piece.get_row(), piece.get_column()):
                    num_double_diagonal_king += 1
            else:
                if piece.player == self.player:
                    num_of_self_pawns += 1
                    if self.adjacent_to_the_edge(piece.get_row(), piece.get_column()):
                        num_self_on_edge += 1
                    if self.on_top_three_layers(piece.get_column()):
                        num_on_top_three += 1
                else:
                    num_of_enemy_pawns += 1
                    if self.adjacent_to_the_edge(piece.get_row(), piece.get_column()):
                        num_enemy_on_edge += 1

                if self.centrally_positioned(piece.get_row(), piece.get_column()):
                    num_center_pawn += 1

        res = num_self_on_edge + num_enemy_on_edge + num_on_top_three + num_center_king + num_center_pawn
        res += num_double_diagonal_king + self.triangle() + self.bridge() + self.dog() + self.oreo()
        if num_of_enemy_pawns > 3 and num_of_self_pawns > 3:
            if num_of_enemy_kings == 0 and num_of_self_kings == 0:
                return res
            if num_of_enemy_kings > 0 or num_of_self_kings > 0:
                return res * 2
        else:
            return res * 3

    def adjacent_to_the_edge(self, i, j):
        if i == 0 or j == 0 or i == 7 or j == 7:
            return True
        return False

    # ????
    def on_top_three_layers(self, i):
        if 4 < i <= 7:
            return True
        return False

    def centrally_positioned(self, i, j):
        if 2 <= i <= 5 and 2 <= j <= 5:
            return True
        return False

    def on_double_diagonal(self, i, j):
        if i > 0:
            if j == i - 1:
                return True
        if j > 0:
            if i == i - 1:
                return True
        return False

    # white on 1 2 6
    def triangle(self):
        return self.on_position_white(1) and self.on_position_white(2) and self.on_position_white(6)

    def on_position_white(self, i):
        piece = self.game.board.searcher.get_piece_by_position(i)
        if piece is None:
            return False
        return piece.player == 1

    def on_position_black(self, i):
        piece = self.game.board.searcher.get_piece_by_position(i)
        if piece is None:
            return False
        return piece.player == 2

    # white on 2 3 7
    def oreo(self):
        return self.on_position_white(2) and self.on_position_white(3) and self.on_position_white(7)

    # white on 1 3
    def bridge(self):
        return self.on_position_white(1) and self.on_position_white(3)

    # white on 1 black on 5
    def dog(self):
        return self.on_position_white(1) and self.on_position_black(5)

    # white king on 29
    def king_in_corner(self):
        piece = self.game.board.searcher.get_piece_by_position(29)
        if piece is None:
            return False
        return piece.player == 2 and piece.king

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
