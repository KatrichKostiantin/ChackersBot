import concurrent
import datetime
import logging
from copy import deepcopy
from queue import Queue


class Node:
    def __init__(self, game, move, player, player_moved, heuristic):
        self.heuristic = heuristic
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
        num_dif_pawns = 0
        num_dif_kings = 0
        num_dif_on_edge_pawn = 0
        num_dif_on_edge_king = 0
        num_dif_defend_pieces = 0
        num_dif_on_top_three = 0
        num_dif_center_king = 0
        num_dif_center_pawn = 0

        for piece in self.game.board.pieces:
            if piece.captured:
                continue
            column = piece.get_row()
            row = piece.get_column() * 2 + 1 if row % 2 == 0 else piece.get_column() * 2
            if piece.king:
                if piece.player == self.player:
                    num_dif_kings += 1
                    if self.centrally_positioned(row, column):
                        num_dif_center_king += 1
                    if self.adjacent_to_the_edge(row, column):
                        num_dif_on_edge_king += 1
                    if self.on_lower_two_layers(column, piece.player):
                        num_dif_defend_pieces += 1
                else:
                    num_dif_kings -= 1
                    if self.centrally_positioned(row, column):
                        num_dif_center_king -= 1
                    if self.adjacent_to_the_edge(row, column):
                        num_dif_on_edge_king -= 1
                    if self.on_lower_two_layers(column, piece.player):
                        num_dif_defend_pieces -= 1
            else:
                if piece.player == self.player:
                    num_dif_pawns += 1
                    if self.adjacent_to_the_edge(row, column):
                        num_dif_on_edge_pawn += 1
                    if self.on_top_three_layers(column, piece.player):
                        num_dif_on_top_three += 1
                    if self.centrally_positioned(row, piece.get_column()):
                        num_dif_center_pawn += 1
                    if self.on_lower_two_layers(column, piece.player):
                        num_dif_defend_pieces += 1
                else:
                    num_dif_pawns -= 1
                    if self.adjacent_to_the_edge(row, column):
                        num_dif_on_edge_pawn -= 1
                    if self.on_top_three_layers(column, piece.player):
                        num_dif_on_top_three -= 1
                    if self.centrally_positioned(row, column):
                        num_dif_center_pawn -= 1
                    if self.on_lower_two_layers(column, piece.player):
                        num_dif_defend_pieces -= 1

        if self.player == 1:
            dif_triangle = self.triangle(1) - self.triangle(2)
            dif_bridge = self.bridge(1) - self.bridge(2)
            dif_dog = self.dog(1) - self.dog(2)
            dif_oreo = self.oreo(1) - self.oreo(2)
            dif_kings_corner = self.king_in_corner(1) - self.king_in_corner(2)
        else:
            dif_triangle = self.triangle(2) - self.triangle(1)
            dif_bridge = self.bridge(2) - self.bridge(1)
            dif_dog = self.dog(2) - self.dog(1)
            dif_oreo = self.oreo(2) - self.oreo(1)
            dif_kings_corner = self.king_in_corner(2) - self.king_in_corner(1)

        res = self.heuristic.count_heuristic(
            num_dif_pawns, num_dif_kings,
            num_dif_on_edge_pawn, num_dif_on_edge_king,
            num_dif_defend_pieces, num_dif_on_top_three,
            num_dif_center_king, num_dif_center_pawn,
            dif_triangle, dif_bridge, dif_dog, dif_oreo, dif_kings_corner
        )
        return res

    def adjacent_to_the_edge(self, i, j):
        if i == 0 or j == 0 or i == 7 or j == 7:
            return True
        return False

    def on_lower_two_layers(self, i, player):
        if player == 1:
            if 0 <= i <= 1:
                return True
            return False
        else:
            if 6 <= i <= 7:
                return True
            return False

    def on_top_three_layers(self, i, player):
        if player == 1:
            if 4 < i <= 7:
                return True
            return False
        else:
            if 0 <= i <= 2:
                return True
            return False

    def centrally_positioned(self, i, j):
        if 2 <= i <= 5 and 2 <= j <= 5:
            return True
        return False

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

    # white on 1 2 6 / black on 27 31 32
    def triangle(self, player):
        if player == 1:
            return self.on_position_white(1) and self.on_position_white(2) and self.on_position_white(6)
        return self.on_position_black(27) and self.on_position_black(31) and self.on_position_black(32)

    # white on 2 3 7 / black on 26 30 31
    def oreo(self, player):
        if player == 1:
            return self.on_position_white(2) and self.on_position_white(3) and self.on_position_white(7)
        return self.on_position_black(26) and self.on_position_black(30) and self.on_position_black(31)

    # white on 1 3 / black on 30, 32
    def bridge(self, player):
        if player == 1:
            return self.on_position_white(1) and self.on_position_white(3)
        return self.on_position_black(30) and self.on_position_black(32)

    # white on 1 black on 5/ black on 32 white on 28
    def dog(self, player):
        if player == 1:
            return self.on_position_white(1) and self.on_position_black(5)
        return self.on_position_white(28) and self.on_position_black(32)

    # white king on 29/ black king on 4
    def king_in_corner(self, player):
        if player == 1:
            piece = self.game.board.searcher.get_piece_by_position(29)
            if piece is None:
                return False
            return piece.player == 1 and piece.king
        else:
            piece = self.game.board.searcher.get_piece_by_position(4)
            if piece is None:
                return False
            return piece.player == 2 and piece.king

    def add_children(self, children):
        self.children.append(children)


class Minimax:
    def __init__(self):
        self.player_num = None

    def find_best_move(self, available_time, game, heuristic):
        self.player_num = game.whose_turn()
        start_time = datetime.datetime.now()
        logging.debug(f"Try find_best_move start_time = {start_time}, available_time = {available_time}")
        root_node = self.create_tree(game, start_time + datetime.timedelta(milliseconds=(available_time * 0.8) * 1000),
                                     heuristic)
        best_move = self.choice_best_move(root_node)
        logging.debug(f"Return best move({best_move})")
        return best_move

    def create_tree(self, game, available_time_to, heuristic):
        logging.debug(f"Try create_tree, available_time_to = {available_time_to}")
        root = Node(game, None, self.player_num, 2 if self.player_num == 1 else 1, heuristic)
        node_init_queue = Queue(maxsize=99999999)
        node_init_queue.put(root)
        self.recursive_child_creation(node_init_queue, available_time_to)
        return root

    def recursive_child_creation(self, node_init_queue, available_time_to):
        while datetime.datetime.now() < available_time_to and node_init_queue.qsize() > 0:
            node = node_init_queue.get()
            self.creating_node_children(node, node_init_queue, available_time_to)
        logging.debug(f"End recursive_child_creation on {datetime.datetime.now()}")

    def creating_node_children(self, node, node_init_queue, available_time_to):
        #logging.debug(f"All moves {node.game.get_possible_moves()}")
        for move in node.game.get_possible_moves():
            if datetime.datetime.now() > available_time_to:
                return
            copy_game = deepcopy(node.game)
            player_moved = copy_game.whose_turn()
            copy_game.move(move)
            new_node = Node(copy_game, move, self.player_num, player_moved, node.heuristic)
            node.add_children(new_node)
            if copy_game.is_over():
                continue
            node_init_queue.put(new_node)

    def choice_best_move(self, root_node):
        self.iterative_deep_alpha_beta(root_node, -1000, 1000)

        for node in root_node.children:
            if node.value is root_node.value:
                return node.move

    def iterative_deep_alpha_beta(self, node, alpha, beta):
        if len(node.children) == 0:
            node.count_value()
            return node.value
        if node.player_moved is not self.player_num:
            node.value = -1000
            for child in node.children:
                node.value = max(node.value, self.iterative_deep_alpha_beta(child, alpha, beta))
                alpha = max(alpha, node.value)
                if alpha > beta:
                    break
        else:
            node.value = 1000
            for child in node.children:
                node.value = min(node.value, self.iterative_deep_alpha_beta(child, alpha, beta))
                beta = min(alpha, node.value)
                if beta < alpha:
                    break
        return node.value
