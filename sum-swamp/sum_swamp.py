import random
from typing import Dict, List, Optional, Set, Union, Tuple
from enum import Enum
from dataclasses import dataclass
from collections import Counter

import numpy as np
import numpy.typing as npt


class Parity(Enum):
    EVEN = 0
    ODD = 1


@dataclass
class Space:
    spot_number: int
    number: Optional[int] = None
    parity: Optional[Parity] = None
    shortcut: Optional[int] = None


@dataclass
class Loop:
    start: int
    end: int
    exit: int

    def __post_init__(self) -> None:
        assert self.start < self.end        
        assert self.start < self.exit
        assert self.exit <= self.end


@dataclass
class Parities:
    evens: Set[int]
    odds: Set[int]

    def __post_init__(self) -> None:
        assert self.evens.isdisjoint(self.odds)


class Shortcuts(dict):
    def __init__(self, shortcuts: Dict[int, int]) -> None:
        super(Shortcuts, self).__init__(shortcuts)
        assert all(map(lambda x: x[0] != x[1], self.items()))


@dataclass
class BoardConfig:
    n: int
    parities: Optional[Parities] = None
    numbered: Optional[Dict[int, int]] = None
    shortcuts: Optional[Shortcuts] = None
    loop: Optional[Loop] = None


class Dice:
    def __init__(self, dist: Union[Dict[int, float], List[float]], p: float = 0.5) -> None:
        assert isinstance(dist, (list, dict))
        assert p >= 0.0

        k = len(dist)
        self.p = p
        self.dist = dist
        
        if isinstance(dist, dict):
            k = max(dist) + 1
            self.dist = list(map(lambda y: dist[y], range(k)))

        self.even = [0.0 for _ in range(k)]
        self.odd = [0.0 for _ in range(k)]
        
        for i, x in enumerate(self.dist):
            if i == 0:
                self.even[i] += x
                self.odd[i] += x
                continue
            
            if i % 2 == 0:
                self.odd[0] += x
                self.even[i] += x
            
            else:
                self.even[0] += x
                self.odd[i] += x


class Game:
    def __init__(self, config: BoardConfig, dice: Dice) -> None:
        self.n = config.n
        self._board = [Space(i) for i in range(self.n)]
        self.transition_matrix = [[0 for _ in range(self.n)] for _ in range(self.n)]
        self.dice = dice

        if config.parities:
            self._setup_parities(config.parities)
        
        if config.numbered:
            self._setup_numbered_spots(config.numbered)

        if config.shortcuts:
            self._setup_shortcuts(config.shortcuts)

        if config.loop:
            self._setup_loop(config.loop)

    def __getitem__(self, i: int) -> Space:
        return self._board[i]
        
    def compute_transition_matrix(self) -> None:
        self.transition_matrix = [[0.0000 for _ in range(self.n)] for _ in range(self.n)]
        
        for i in range(self.n):
            space = self[i] 
            
            if space.number is not None or space.shortcut is not None:
                continue

            tmp_dist = self.dice.dist
            if space.parity is not None:
                tmp_dist = self.dice.even if space.parity == Parity.EVEN else self.dice.odd

            for roll in range(len(tmp_dist)):
                self._add_probability(i, roll, tmp_dist[roll])

    def _add_probability(self, i: int, roll: int, prob_of_roll: float) -> None:
        j = self._adjust_for_loop(i, roll) if self._needs_loop_action(i, roll) else i + roll

        j = min(j, self.n - 1)

        probs_to_add = [(j, prob_of_roll)]

        if self._needs_traversal(j):
            probs_to_add = self._traverse(self[j], prob_of_roll)

        for k, p in probs_to_add:
            self.transition_matrix[i][k] += p

    def _needs_loop_action(self, i: int, move_up: int) -> bool:
        return any([
            self.loop_start <= i <= self.loop_end,
            i < self.loop_start < i + move_up,
        ])

    def _adjust_for_loop(self, i: int, move_up: int) -> int:
        j = i + move_up

        loop_size = (self.loop_end - self.loop_start + 1)

        if i == self.loop_exit and move_up > 0:
            j = self.loop_end + move_up

        elif (self.loop_start <= i <= self.loop_end) or (i < self.loop_start and j > self.loop_end):
            x = move_up - (self.loop_start - i)
            j = self.loop_start + (x % loop_size)

        return min(j, self.n - 1)

    def _needs_traversal(self, spot: int) -> bool:
        return any([self[spot].shortcut, self[spot].number])

    def _traverse(self, space: Space, prob: float) -> List[Tuple[int, float]]:
        output = []

        spots_to_traverse = [(space, prob)]
        while spots_to_traverse:
            spot, p = spots_to_traverse.pop()

            if spot.shortcut is not None:
                if self._needs_traversal(spot.shortcut):
                    next_spot = (self[spot.shortcut], p)
                    spots_to_traverse.append(next_spot)
                else:
                    output.append((spot.shortcut, p))

            elif spot.number:
                for m, pp in [(-spot.number, (1 - self.dice.p) * p), (spot.number, self.dice.p * p)]:
                    j = spot.spot_number + m
                    if self._needs_loop_action(spot.spot_number, m):
                        j = self._adjust_for_loop(spot.spot_number, m)

                    if self._needs_traversal(j):
                        next_spot = (self[j], pp)
                        spots_to_traverse.append(next_spot)
                    else:
                        output.append((j, pp))
        return output

    def _setup_parities(self, parities: Parities) -> None:
        for i in parities.evens:
            self[i].parity = Parity.EVEN

        for i in parities.odds:
            self[i].parity = Parity.ODD

    def _setup_numbered_spots(self, numbered: Dict[int, int]) -> None:
        for key, val in numbered.items():
            self[key].number = val

    def _setup_shortcuts(self, shortcuts: Dict[int, int]) -> None:
        for key, val in shortcuts.items():
            self[key].shortcut = val

    def _setup_loop(self, loop: Loop) -> None:
        self.loop_start = loop.start
        self.loop_exit = loop.exit
        self.loop_end = loop.end


def expected_tau(transition_matrix: npt.ArrayLike, max_iters: int = 10000) -> float:
    n = transition_matrix.shape[0]
    
    one = np.ones(n)
    one[n-1] = 0

    mask = np.zeros(n)
    mask[n-1] = 1

    k1 = np.zeros(n)
    k2 = one + transition_matrix.dot(k1)

    i = 0

    while (np.linalg.norm(k2 - k1) > 1e-6) and i < max_iters:
        k1 = k2
        k2 = one + transition_matrix.dot(k1)
        np.putmask(k2, mask, 0)
        i += 1

    return k2[0]


def simulate_game_length(transition_matrix: npt.ArrayLike) -> int:
    n = transition_matrix.shape[0]
    current_position, output = 0, 0
    possible_choices = list(range(n))
    
    while current_position < n - 1:
        probs = transition_matrix[current_position]
        current_position = random.choices(possible_choices, weights=probs)[0]
        output += 1
    
    return output


def simulate_tau_distribution(transition_matrix: npt.ArrayLike, n_games: int = 1000000) -> Dict[int, float]:
    output = Counter(
        map(
            lambda _: simulate_game_length(transition_matrix), 
            range(n_games)
        )
    )

    for key, val in output.items():
        output[key] = val / n_games

    return output
