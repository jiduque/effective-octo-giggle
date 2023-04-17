from itertools import product

import networkx as nx


AdjacencyList = list[str]
Coordinate = tuple[int, int]
CoordinateList = list[Coordinate]


def to_ij(node_index: int, m: int) -> tuple[int, int]:
    i, j = divmod(node_index, m)
    return i, j


def to_index(i: int, j: int, m: int) -> int:
    return (m * i) + j


def in_bound(i: int, j: int, n: int, m: int) -> bool:
    return (0 <= i < n) and (0 <= j < m)


def get_neighbors(i: int, j: int, n: int, m: int) -> CoordinateList:
    i_dir = [i - 1, i, i + 1]
    j_dir = [j - 1, j, j + 1]
    block_3_3 = product(i_dir, j_dir)
    minus_self = filter(lambda x: x != (i, j), block_3_3)
    valid_ones = filter(lambda x: in_bound(x[0], x[1], n, m), minus_self)
    return list(valid_ones)


def get_connections(node_index: int, n: int, m: int) -> list[int]:
    i, j = to_ij(node_index, m)
    neighbors = get_neighbors(i, j, n, m)

    if j == 0 and i > 0:
        neighbors.append((i - 1, m - 1))

    if i == n - 1:
        top_neighbors = [(0, j - 1), (0, j), (0, j + 1)]
        valid_ones = filter(lambda x: in_bound(x[0], x[1], n, m), top_neighbors)
        neighbors.extend(valid_ones)

    neighbors_as_nodes = map(lambda x: to_index(x[0], x[1], m), neighbors)
    return list(neighbors_as_nodes)


def adjacency_line(node: int, neighbors: list[int]) -> str:
    all_nodes = [node]
    all_nodes.extend(neighbors)
    str_ints = map(str, all_nodes)
    return ' '.join(str_ints)


def make_adjacency_list(n: int, m: int) -> AdjacencyList:
    nodes = range(m * n)
    connections = map(lambda index: get_connections(index, n, m), nodes)
    lines = map(
        lambda x: adjacency_line(x[0], x[1]),
        zip(nodes, connections))
    return list(lines)


def make_graph(n: int, m: int) -> nx.Graph:
    assert m >= 3 and n >= 3
    lines = make_adjacency_list(n, m)
    return nx.parse_adjlist(lines)
