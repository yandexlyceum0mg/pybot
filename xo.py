class Translator:
    def __init__(self):
        self.d = {'a': 0, 'b': 1, 'c': 2}
        self._d = {self.d[i]: i for i in self.d.keys()}

    def translate_coords_to_human_readable(self, row, column):
        return f'{self._d[column]}{row + 1}'

    def translate_coords_from_human_readable(self, coords):
        try:
            if coords[1] not in list('123'):
                raise Exception
            return int(coords[1]) - 1, self.d[coords[0]]
        except Exception:
            return -1, -1


class XOBoard:
    X = True
    O = False

    def __init__(self, time=60):
        self.field = [[None, None, None] for _ in range(3)]
        self.ended = False
        self.shape = self.X
        self.time = time

    def __copy__(self):
        c = XOBoard()
        c.field = [[i for i in j] for j in self.field]
        c.ended = self.ended
        c.shape = self.shape
        return c

    @staticmethod
    def is_correct_coords(x, y):
        return 0 <= x <= 2 and 0 <= y <= 2

    @property
    def is_ended(self):
        if self.ended or self.ended is None:
            return True
        for i in range(3):
            if self.field[i][0] == self.field[i][1] == self.field[i][2] != None:
                self.ended = True
                return True
            if self.field[0][i] == self.field[1][i] == self.field[2][i] != None:
                self.ended = True
                return True
        if self.field[0][0] == self.field[1][1] == self.field[2][2] != None:
            self.ended = True
            return True
        if self.field[0][2] == self.field[1][1] == self.field[2][0] != None:
            self.ended = True
            return True
        if all([all(['' if i is None else ' ' for i in j]) for j in self.field]):
            self.ended = None
            return None
        return False

    @staticmethod
    def opponent(shape):
        return not shape

    def change_shape(self):
        self.shape = self.opponent(self.shape)

    def motion(self, x, y):
        if self.is_ended or self.ended is None:
            return
        self.field[x][y] = self.shape
        if self.is_ended or self.ended is None:
            return
        self.change_shape()

    @property
    def is_win(self):
        if self.ended is True:
            return True
        else:
            return False

    def __getitem__(self, crds):
        return '.' if self.field[crds[0]][crds[1]] is None else 'X' if self.field[crds[0]][crds[1]] == self.X else 'O'

    def __str__(self):
        return '\n'.join(
            [''.join(['.' if i is None else 'X' if i == self.X else 'O' for i in j]) for j in self.field])


def play(board_output_func, input_func, output_func, input_func2, output_func2):
    g = XOBoard()
    t = Translator()
    while not g.is_ended:
        output_func('img:' + board_output_func(g))
        output_func('Введите координаты клетки, в которой Вы хотите поставить свой знак')
        i = input_func(timeout=g.time)
        if i == 'to':
            output_func('Ваше время вышло. Вы проиграли.')
            output_func2('+', end='')
            output_func('-', end='')
            return
        while not XOBoard.is_correct_coords(*t.translate_coords_from_human_readable(i)) or g[
            t.translate_coords_from_human_readable(i)] != '.':
            if not XOBoard.is_correct_coords(*t.translate_coords_from_human_readable(i)):
                output_func('Введите корректные координаты!')
            else:
                output_func('Эта клетка уже занята. Введите координаты ещё раз!')
            i = input_func(timeout=g.time)
            if i == 'to':
                output_func('Ваше время вышло. Вы проиграли.')
                output_func2('+', end='')
                output_func('-', end='')
                return
        g.motion(*t.translate_coords_from_human_readable(i))
        if g.is_ended:
            break
        output_func2('img:' + board_output_func(g))
        output_func2('Введите координаты клетки, в которой Вы хотите поставить свой знак')
        i = input_func2(timeout=g.time)
        if i == 'to':
            output_func('Ваше время вышло. Вы проиграли.')
            output_func2('Время противника вышло. Вы выиграли!')
            output_func('+', end='')
            output_func2('-', end='')
            return
        while not XOBoard.is_correct_coords(*t.translate_coords_from_human_readable(i)) or g[
            t.translate_coords_from_human_readable(i)] != '.':
            if not XOBoard.is_correct_coords(*t.translate_coords_from_human_readable(i)):
                output_func2('Введите корректные координаты!')
            else:
                output_func2('Эта клетка уже занята. Введите координаты ещё раз!')
            i = input_func2(timeout=g.time)
            if i == 'to':
                output_func2('Ваше время вышло. Вы проиграли.')
                output_func('Время противника вышло. Вы выиграли!')
                output_func('+', end='')
                output_func2('-', end='')
                return
        g.motion(*t.translate_coords_from_human_readable(i))
    sh = XOBoard.O
    if g.is_win and g.shape == sh:
        output_func('Вы проиграли.')
        output_func('-', end='')
        output_func2('Вы выиграли!')
        output_func2('+', end='')
    elif g.is_win:
        output_func('Вы выиграли!')
        output_func('+', end='')
        output_func2('Вы проиграли.')
        output_func2('-', end='')
    else:
        output_func('Ничья!')
        output_func2('Ничья')
        output_func('=', end='')
        output_func2('=', end='')


if __name__ == '__main__':
    a = XOBoard()
    a.motion(1, 1)
    a.motion(0, 1)
    a.motion(2, 2)
    a.motion(1, 0)
    a.motion(0, 0)
    print(a.is_ended)
    print(a)
