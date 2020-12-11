class Heuristic:
    def __init__(self, cof_dif_pawns, cof_dif_kings,
                 cof_dif_on_edge_pawn, cof_dif_on_edge_king,
                 cof_dif_defend_pieces, cof_dif_on_top_three,
                 cof_dif_center_king, cof_dif_center_pawn,
                 cof_dif_triangle, cof_dif_bridge, cof_dif_dog, cof_dif_oreo, cof_dif_kings_corner
                 ):
        self.cof_dif_pawns = cof_dif_pawns
        self.cof_dif_kings = cof_dif_kings
        self.cof_dif_on_edge_pawn = cof_dif_on_edge_pawn
        self.cof_dif_on_edge_king = cof_dif_on_edge_king
        self.cof_dif_defend_pieces = cof_dif_defend_pieces
        self.cof_dif_on_top_three = cof_dif_on_top_three
        self.cof_dif_center_king = cof_dif_center_king
        self.cof_dif_center_pawn = cof_dif_center_pawn
        self.cof_dif_triangle = cof_dif_triangle
        self.cof_dif_bridge = cof_dif_bridge
        self.cof_dif_dog = cof_dif_dog
        self.cof_dif_oreo = cof_dif_oreo
        self.cof_dif_kings_corner = cof_dif_kings_corner

    def count_heuristic(self, num_dif_pawns, num_dif_kings,
                        num_dif_on_edge_pawn, num_dif_on_edge_king,
                        num_dif_defend_pieces, num_dif_on_top_three,
                        num_dif_center_king, num_dif_center_pawn,
                        dif_triangle, dif_bridge, dif_dog, dif_oreo, dif_kings_corner
                        ):
        res = 0
        res += self.cof_dif_pawns * num_dif_pawns
        res += self.cof_dif_kings * num_dif_kings
        res += self.cof_dif_on_edge_pawn * num_dif_on_edge_pawn
        res += self.cof_dif_on_edge_king * num_dif_on_edge_king
        res += self.cof_dif_defend_pieces * num_dif_defend_pieces
        res += self.cof_dif_center_king * num_dif_center_king
        res += self.cof_dif_on_top_three * num_dif_on_top_three
        res += self.cof_dif_center_pawn * num_dif_center_pawn
        res += self.cof_dif_triangle * dif_triangle
        res += self.cof_dif_bridge * dif_bridge
        res += self.cof_dif_dog * dif_dog
        res += self.cof_dif_oreo * dif_oreo
        res += self.cof_dif_kings_corner * dif_kings_corner
        return res
