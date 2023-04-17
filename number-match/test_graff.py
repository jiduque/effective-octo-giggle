import unittest

import graff


class MyTestCase(unittest.TestCase):
    def test_to_ij(self):
        cases = [
            {"input": (11, 9), "expected": (1, 2)},
            {"input": (9, 9), "expected": (1, 0)},
            {"input": (0, 9), "expected": (0, 0)},
            {"input": (23, 9), "expected": (2, 5)},
            {"input": (26, 9), "expected": (2, 8)}
        ]

        for test_dict in cases:
            index, m = test_dict["input"]
            expected = test_dict["expected"]
            output = graff.to_ij(index, m)
            self.assertEqual(expected, output, f"{expected} != {output}")

    def test_to_index(self):
        cases = [
            {"input": (2, 1, 9), "expected": 19},
            {"input": (0, 1, 9), "expected": 1},
            {"input": (0, 2, 9), "expected": 2},
            {"input": (0, 8, 9), "expected": 8},
            {"input": (1, 0, 9), "expected": 9},
            {"input": (2, 8, 9), "expected": 26}
        ]

        for test_dict in cases:
            i, j, m = test_dict["input"]
            expected = test_dict["expected"]
            output = graff.to_index(i, j, m)
            self.assertEqual(expected, output, f"{expected} != {output}")

    def test_get_neighbors(self):
        cases = [
            {"input": (0, 0, 3, 9), "expected": [(0, 1), (1, 1), (1, 0)]},
            {"input": (0, 1, 3, 9), "expected": [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)]},
            {"input": (1, 1, 3, 9), "expected": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]},
            {"input": (1, 0, 3, 9), "expected": [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)]},
            {"input": (2, 8, 3, 9), "expected": [(2, 7), (1, 8), (1, 7)]}
        ]

        for test_dict in cases:
            i, j, n, m = test_dict["input"]
            expected = set(test_dict["expected"])
            output = set(graff.get_neighbors(i, j, n, m))
            msg = f"Failed for input: {i=} {j=} {n=} {m=}"
            self.assertEqual(expected, output, msg)

    def test_get_connections(self):
        cases = [
            {"input": (0, 3, 9), "expected": [1, 10, 9]},
            {"input": (1, 3, 9), "expected": [0, 2, 9, 10, 11]},
            {"input": (10, 3, 9), "expected": [0, 1, 2, 9, 11, 18, 19, 20]},
            {"input": (9, 3, 9), "expected": [0, 1, 8, 10, 18, 19]},
            {"input": (26, 3, 9), "expected": [25, 16, 17, 7, 8]}
        ]

        for test_dict in cases:
            index, n, m = test_dict["input"]
            expected = set(test_dict["expected"])
            output = set(graff.get_connections(index, n, m))
            msg = f"Failed for input: {index=} {n=} {m=}"
            self.assertEqual(expected, output, msg)

    def test_adjacency_line(self):
        cases = [
            {"input": (0, [1, 10, 9]), "expected": "0 1 10 9"},
            {"input": (1, [0, 2, 9, 10, 11]), "expected": "1 0 2 9 10 11"},
            {"input": (10, [0, 1, 2, 9, 11, 18, 19, 20]), "expected": "10 0 1 2 9 11 18 19 20"},
        ]

        for test_dict in cases:
            index, neighbors = test_dict["input"]
            expected = test_dict["expected"]
            output = graff.adjacency_line(index, neighbors)
            msg = f"Failed for input: {index=} {neighbors=}"
            self.assertEqual(expected, output, msg)


if __name__ == '__main__':
    unittest.main()
