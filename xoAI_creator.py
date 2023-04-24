from __future__ import annotations  # для dataclasses, которые потребляют меньше памяти, чем обычные классы
from xo import XOBoard
from dataclasses import dataclass
from pickle import dumps
from os.path import exists


class VariantsTreeNode:
    __slots__ = ['child_nodes', 'min_deep_defeat', 'part_of_wins', 'part_of_defeats', 'min_deep_win', 'b', 'shape',
                 'leaves_count', '_motion']  # уменьшаем потребление памяти, оно итак > 100МБ

    def __init__(self, shape):
        self.child_nodes = []
        self.min_deep_defeat = -1
        self.part_of_wins = -1
        self.part_of_defeats = -1
        self.min_deep_win = -1
        self.b = XOBoard()
        self.shape = shape
        self.leaves_count = 0
        self._motion = None

    @property
    def is_leave(self):
        return self.leaves_count == 0

    def motion(self, x, y):
        self._motion = (x, y)
        self.b.motion(x, y)

    def make(self):
        if self.b.is_ended:
            if self.b.is_win:
                self.min_deep_win = 0 if self.b.shape == self.shape else float('inf')
                self.min_deep_defeat = float('inf') if self.b.shape == self.shape else 0
                self.part_of_wins = 1 if self.b.shape == self.shape else 0
                self.part_of_defeats = 0 if self.b.shape == self.shape else 1
                self.leaves_count = 0
                return
            self.min_deep_win = float('inf')
            self.min_deep_defeat = float('inf')
            self.part_of_wins = 0
            self.part_of_defeats = 0
            self.leaves_count = 0
            return
        for i in range(3):
            for j in range(3):
                if self.b[i, j] == '.':
                    self.child_nodes.append(VariantsTreeNode(self.shape))
                    self.child_nodes[-1].b = self.b.__copy__()
                    self.child_nodes[-1].motion(i, j)
                    self.child_nodes[-1].make()
        self.leaves_count = sum([i.is_leave + i.leaves_count for i in self.child_nodes])
        self.min_deep_win = 1 + min([i.min_deep_win for i in self.child_nodes])
        self.min_deep_defeat = 1 + min([i.min_deep_defeat for i in self.child_nodes])
        self.part_of_wins = sum(
            [i.part_of_wins * (i.leaves_count + i.is_leave) for i in self.child_nodes]) / self.leaves_count
        self.part_of_defeats = sum(
            [i.part_of_defeats * (i.leaves_count + i.is_leave) for i in self.child_nodes]) / self.leaves_count


class XOAI:
    @staticmethod
    def find_node(motions, tree):
        t = tree
        for i in t.child_nodes:
            if i._motion == motions[-1]:
                t = i
                if motions[0] != motions[-1]:
                    del motions[0]
                break
        return t

    @staticmethod
    def is_guaranty_defeat(tree):
        if tree.is_leave:
            return False
        return max([j.min_deep_defeat for j in tree.child_nodes]) == 1

    @classmethod
    def is_deep_guaranty_defeat(cls,
                                tree):  # если есть гарантированное поражение при одном из вариантов хода противника(так не надо ходить)
        for i in tree.child_nodes:
            if cls.is_guaranty_defeat(i):
                return True
        return False

    @classmethod
    def choice_motion(cls, tree):
        trees = tree.child_nodes
        for i in trees:
            if i.min_deep_win == 0:  # если можно выиграть в этот ход
                return i._motion  # выберем этот ход
            if i.min_deep_defeat == 1:  # если можно проиграть в следующий ход
                if max([j.min_deep_defeat for j in trees]) != 1:  # но если можно не проиграть в следующий ход
                    continue  # этот выбор хода неверен
                else:
                    break
            if i.min_deep_win == float(
                    'inf') and i.min_deep_defeat == 1:  # если выиграть невозможно при выборе этого хода
                if min([j.min_deep_win for j in filter(lambda x: x.min_deep_defeat != 1, trees)]) == float(
                        'inf'):  # и вообще нельзя выиграть без вероятности проиграть на следующий ход
                    if i.part_of_defeats == min([j.part_of_defeats for j in filter(lambda x: x.min_deep_defeat != 1,
                                                                                   trees)]):  # если больше шанса на ничью
                        return i._motion  # выберем этот ход
                else:  # но если выиграть возможно без шанса проиграть на следующий ход
                    continue  # этот выбор хода неверен
            if i.part_of_wins == max([j.part_of_wins for j in
                                      filter(lambda x: x.min_deep_defeat != 1 and not cls.is_deep_guaranty_defeat(x),
                                             trees)]):  # если шанс выиграть максимален(не учитывая ходы с возможностью проиграть на следущий ход)
                if i.part_of_defeats == max([j.part_of_defeats for j in filter(lambda x: x.min_deep_defeat != 1,
                                                                               trees)]):  # если шанс проиграть минимален(не учитывая ходы с возможностью проиграть на следущий ход)
                    if i.min_deep_defeat == min([j.min_deep_defeat for j in filter(lambda x: x.min_deep_defeat != 1,
                                                                                   trees)]):  # если возможно выиграть раньше(не учитывая ходы с возможностью проиграть на следущий ход)
                        if i.min_deep_win == max([j.min_deep_win for j in filter(lambda x: x.min_deep_defeat != 1,
                                                                                 trees)]):  # если возможно проиграть позже(не учитывая ходы с возможностью проиграть на следущий ход)
                            return i._motion  # выберем этот ход
                        return i._motion  # выберем этот ход
                    return i._motion  # выберем этот ход
                return i._motion  # выберем этот ход

        return trees[0]._motion


@dataclass
class VarTreeNode:
    childs: list[VarTreeNode] | None = None
    motion: tuple[int, int] | None = None


def clear_tree_1(t):
    if t.is_leave:
        return VarTreeNode(None, t._motion)
    m = XOAI.choice_motion(t)
    for i in t.child_nodes:
        if i._motion == m:
            return VarTreeNode([clear_tree_2(i)], t._motion)


def clear_tree_2(t):
    if t.is_leave:
        return VarTreeNode(None, t._motion)
    return VarTreeNode([clear_tree_1(i) for i in t.child_nodes], t._motion)


def create_ai():
    a = VariantsTreeNode(XOBoard.X)
    b = VariantsTreeNode(XOBoard.O)
    b.make()
    a.make()
    a = clear_tree_1(a)
    b = clear_tree_2(b)
    _ = a, b
    open('_', 'wb').write(dumps(_))


def create_ai_if_not_exists():
    if not exists('_'):
        create_ai()


create_ai_if_not_exists()
