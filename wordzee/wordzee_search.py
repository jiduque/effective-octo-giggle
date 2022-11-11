from dataclasses import dataclass


LetterVals = dict[str, int]


@dataclass
class Word:
    word: str
    base: int
    max_loc: int
    points_at_max_loc: int

    @property
    def length(self) -> int:
        return len(self.word)

    def points_with_bonus(self, bonus: int) -> int:
        delta = self.points_at_max_loc * (bonus - 1)
        return self.base + delta


class Node:
    def __init__(self, points: int) -> None:
        self.points = points
        self.words = []

    def insert(self, word: Word) -> None:
        self.words.append(word)

    def __str__(self) -> str:
        return ', '.join(map(str, self.words))


class RowAnalyzer:
    def __init__(self, row: int, length: int) -> None:
        self.row = row
        self.length = length

        self.best = Node(0)
        self.best_full = Node(0)

    def update(self, word: Word) -> None:
        if word.length > self.length:
            return None

        self._update_normal(word)
        if word.length == self.length:
            self._update_full(word)

    def _update_full(self, word: Word) -> None:
        points = word.points_with_bonus(2)
        if points < self.best_full.points:
            return

        if points > self.best_full.points:
            self.best_full = Node(points)

        self.best_full.insert(word)

    def _update_normal(self, word: Word) -> None:
        points = word.points_with_bonus(2)
        if points < self.best.points:
            return

        if points > self.best.points:
            self.best = Node(points)

        self.best.insert(word)

    def does_it_matter(self) -> bool:
        return self.best.points != self.best_full.points


class GameAnalyzer:
    def __init__(self, letter_vals: LetterVals) -> None:
        self.letter_vals = letter_vals

        row_lengths = [3, 4, 5, 6, 7]
        self.row_analyzers = [RowAnalyzer(i, length) for i, length in enumerate(row_lengths, start=1)]

    def update(self, word: str) -> None:
        points = [self.letter_vals.get(letter, 0) for letter in word]
        base_val = sum(points)
        bound = len(word)

        for analyzer in self.row_analyzers:
            if analyzer.row in [4, 5]:
                bound = min(analyzer.length - 1, bound)
            max_index, max_value = max_up_to(points, bound)
            word_obj = Word(word, base_val, max_index, max_value)
            analyzer.update(word_obj)


def max_up_to(vals: list[int], bound: int) -> tuple[int, int]:
    max_value = max(vals[:bound])
    max_index = vals[:bound].index(max_value)
    return max_index, max_value
