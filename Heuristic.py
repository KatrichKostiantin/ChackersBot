class Heuristic:
    def __init__(self, cof_self_pawns, cof_self_kings, cof_enemy_pawns,
                 cof_enemy_kings, cof_on_edge, cof_on_top_three):
        self.cof_self_pawns = cof_self_pawns
        self.cof_self_kings = cof_self_kings
        self.cof_enemy_pawns = cof_enemy_pawns
        self.cof_enemy_kings = cof_enemy_kings
        self.cof_on_edge = cof_on_edge
        self.cof_on_top_three = cof_on_top_three

    def count_heuristic(self, num_of_self_pawns, num_of_self_kings, num_of_enemy_pawns,
                        num_of_enemy_kings, num_on_edge, num_on_top_three
                        ):
        res = 0
        res += self.cof_self_pawns * num_of_self_pawns
        res += self.cof_self_kings * num_of_self_kings
        res += self.cof_enemy_pawns * num_of_enemy_pawns
        res += self.cof_enemy_kings * num_of_enemy_kings
        res += self.cof_on_edge * num_on_edge
        res += self.cof_on_top_three * num_on_top_three
        return res
