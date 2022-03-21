import unittest

from sum_swamp import *


FP_ERROR_UP_TO_DIGITS = 5


class TestDice(unittest.TestCase):
    def test_proper_dice_list(self):
        x = [1/10 for _ in range(10)]
        y_even = [0.6, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0]
        y_odd = [0.5, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1]

        dice = Dice(x)
        
        self.assertEqual(dice.dist, x)
        self.assertEqual(dice.even, y_even)
        self.assertEqual(dice.odd, y_odd)

    def test_proper_dice_dict(self):
        x = dict([(i, 1/10) for i in range(10)])
        y_original = [1/10 for _ in range(10)]
        y_even = [0.6, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0]
        y_odd = [0.5, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1, 0.0, 0.1]

        dice = Dice(x)
        
        self.assertEqual(dice.dist, y_original)
        self.assertEqual(dice.even, y_even)
        self.assertEqual(dice.odd, y_odd)


class TestBoardIntegration(unittest.TestCase):
    board_config = BoardConfig(
        n=40,
        parities=Parities(evens={1, 15}, odds={8, 32}),
        numbered={
            2: 2,
            11: 3,
            13: 6,
            17: 1,
            22: 5,
            24: 3,
            35: 3
        },
        shortcuts=Shortcuts({6: 12, 33: 37}),
        loop=Loop(start=21, exit=28, end=30)
    )

    dice = Dice([0.08333333333333333,
                 0.1388888888888889,
                 0.125,
                 0.1111111111111111,
                 0.09722222222222221,
                 0.08333333333333333,
                 0.06944444444444445,
                 0.08333333333333333,
                 0.06944444444444445,
                 0.05555555555555555,
                 0.041666666666666664,
                 0.027777777777777776,
                 0.013888888888888888])

    board = Game(board_config, dice)
    board.compute_transition_matrix()

    def test_i_almost_inside_loop(self):
        i = 19  # The spot right before the "enter" spot in the loop
        pj = {
            19: self.dice.dist[0],
            20: self.dice.dist[1],
            21: self.dice.dist[2] + 0.5*self.dice.dist[5] + self.dice.dist[12],
            23: self.dice.dist[4],
            25: self.dice.dist[6],
            26: self.dice.dist[7],
            27: self.dice.dist[8] + self.dice.dist[3] + 0.5*self.dice.dist[5],
            28: self.dice.dist[9],
            29: self.dice.dist[10],
            30: self.dice.dist[11]
        }

        self.assert_transitions_are_correct(i, pj)

    def test_i_inside_loop(self):
        i = 25  # right after 3
        pj = {
            25: self.dice.dist[0] + self.dice.dist[10],
            26: self.dice.dist[1] + self.dice.dist[11],
            27: self.dice.dist[2] + self.dice.dist[7] + (0.5 * self.dice.dist[9]) + self.dice.dist[12],
            28: self.dice.dist[3],
            29: self.dice.dist[4],
            30: self.dice.dist[5],
            21: self.dice.dist[6] + 0.5 * self.dice.dist[9],
            23: self.dice.dist[8]
        }

        self.assert_transitions_are_correct(i, pj)

    def test_i_between_loop_exit_and_start(self):
        # spot 29
        i = 29
        pj = {
            29: self.dice.dist[0] + self.dice.dist[10],
            30: self.dice.dist[1] + self.dice.dist[11],
            21: self.dice.dist[2] + (0.5 * self.dice.dist[5]) + self.dice.dist[12],
            27: self.dice.dist[3] + (0.5 * self.dice.dist[5]) + self.dice.dist[8],
            23: self.dice.dist[4],
            25: self.dice.dist[6],
            26: self.dice.dist[7],
            28: self.dice.dist[9],
        }

        self.assert_transitions_are_correct(i, pj)

    def test_exit_point(self):
        i = 28
        # add 2 because of the two spots between enter and exit in loop
        pj = {
            28: self.dice.dist[0],
            31: self.dice.dist[1],
            32: self.dice.dist[2] + 0.5*self.dice.dist[5],
            34: self.dice.dist[4],
            36: self.dice.dist[6],
            37: self.dice.dist[7] + self.dice.dist[3],
            38: self.dice.dist[8] + 0.5*self.dice.dist[5],
            39: sum(self.dice.dist[9:])
        }

        self.assert_transitions_are_correct(i, pj)

    def test_parity_spot(self):
        # the second even on the board
        i = 15
        pj = {
            15: self.dice.dist[0] + sum([self.dice.dist[i] for i in range(1, 13, 2)]),
            16: 0.5 * self.dice.dist[2],
            18: 0.5 * self.dice.dist[2],
            19: self.dice.dist[4],
            21: self.dice.dist[6],
            23: self.dice.dist[8],
            25: self.dice.dist[10],
            27: self.dice.dist[12],
        }

        self.assert_transitions_are_correct(i, pj)

    def test_starting_point(self):
        # This gets all special spots except loop and parity
        i = 0
        pj = {
            0: self.dice.dist[0] + 0.5*self.dice.dist[2],
            1: self.dice.dist[1],
            3: self.dice.dist[3],
            4: self.dice.dist[4] + 0.5*self.dice.dist[2],
            5: self.dice.dist[5],
            7: self.dice.dist[7],
            8: self.dice.dist[8] + 0.5*self.dice.dist[11],
            9: self.dice.dist[9],
            10: self.dice.dist[10],
            12: self.dice.dist[6] + self.dice.dist[12],
            14: 0.5*self.dice.dist[11]
        }

        self.assert_transitions_are_correct(i, pj)

    def test_needs_loop_action(self):
        test_input = [
            (0, 10),
            (12, 5),
            (19, 4),
            (19, -2),
            (24, -10),
            (25, 6),
            (27, 5),
            (29, 2),
            (31, 10),
        ]
        expected = [False, False, True, False, True, True, True, True, False]

        for x, y in zip(test_input, expected):
            self.assertEqual(self.board._needs_loop_action(*x), y)

    def test_adjust_for_loop(self):
        test_input = [
            (0, 10),
            (19, 4),
            (23, -1),
            (22, 5),
            (22, -5),
            (25, 10),
            (25, 6),
            (29, 2),
            (29, -2),
            (28, 10),
            (27, -10),
        ]
        expected = [10, 23, 22, 27, 27, 25, 21, 21, 27, 39, 27]

        for x, y in zip(test_input, expected):
            self.assertEqual(self.board._adjust_for_loop(*x), y)

    def test_traversal(self):
        test_input = [
            (self.board[2], self.dice.dist[2]),
            (self.board[6], self.dice.dist[6]),
            (self.board[24], 0.5),
            (self.board[22], 0.5)
        ]

        expected = [
            [(0, 0.5 * self.dice.dist[2]), (4, 0.5 * self.dice.dist[2])],
            [(12, self.dice.dist[6])],
            [(21, 0.5 * 0.5), (27, 0.5 * 0.5)],
            [(27, 0.5 * 0.5), (27, 0.5 * 0.5)]
            ]

        for x, y in zip(test_input, expected):
            spots = self.board._traverse(*x)
            self.assertSetEqual(set(spots), set(y))

    def assert_transitions_are_correct(self, i,  pj):
        for j in range(40):
            y_true = pj.get(j, 0.0000)
            y_comp = self.board.transition_matrix[i][j]

            message = f"Spot {j}, a zero spot, was not zero"
            if j in pj:
                message = f"Spot {j}, a non-zero spot, was incorrectly computed"

            self.assertAlmostEqual(y_true, y_comp, FP_ERROR_UP_TO_DIGITS, msg=message)


if __name__ == '__main__':
    unittest.main()
