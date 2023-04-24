from time import time as t

WHITE = True
BLACK = False


class Translator:
    def __init__(self):
        self.d = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        self._d = {self.d[i]: i for i in self.d.keys()}

    def translate_coords_to_human_readable(self, row, column):
        return f'{self._d[column]}{row + 1}'

    def translate_coords_from_human_readable(self, coords):
        try:
            if coords[1] not in list('12345678'):
                raise Exception
            return int(coords[1]) - 1, self.d[coords[0]]
        except Exception:
            return -1, -1


# этот файл будет подключаться как модуль
def play(board_output_func, printfunc1, printfunc2, input_string_func1, input_string_func_2, time=10 * 60, add_t=10):
    global print
    print = printfunc1
    global input
    input = input_string_func1
    global print2
    print2 = printfunc2
    global input2
    input2 = input_string_func_2
    t = Translator()
    b = Board(time, add_t)
    while True:
        print('Чтобы выйти из игры, введите "exit"')
        if b.kings_is_under_attak() is None:
            if b.is_stalemate():
                print('Пат! Ничья!')
                print2('Пат! Ничья!')
                print('pt')
                break
        else:
            if b.is_checkmate():
                print(f'{"Белым" if b.color == WHITE else "Чёрным"} объявлен мат! '
                      f'{"Белые" if b.color == BLACK else "Чёрные"} выиграли!')
                print2(f'{"Белым" if b.color == WHITE else "Чёрным"} объявлен мат! '
                       f'{"Белые" if b.color == BLACK else "Чёрные"} выиграли!')
                print('wh' if b.color == BLACK else 'bl', end='')
                print2('wh' if b.color == BLACK else 'bl', end='')
            break
        if b.current_player_color() == WHITE:
            print('Ход белых:')
        else:
            print('Ход черных:')
        print('img:' + board_output_func(b))
        print('Чтобы ходить, введите координаты полей через пробел(вначале буква, потом цифра)')
        print('Чтобы сдаться, введите "r"')
        if b.color == WHITE:
            h = input(timeout=b.time1)
        else:
            h = input(timeout=b.time2)
        if h == 'to':
            print('Ваше время истекло. Вы проиграли.')
            print2('Время у противника истекло. Вы выиграли!')
            print('wh' if b.color == BLACK else 'bl', end='')
            print2('wh' if b.color == BLACK else 'bl', end='')

        if h == 'exit':
            break
        if h == 'r':
            print('Вы сдались.')
            print2('Противник сдался!')
            print('wh' if b.color == BLACK else 'bl', end='')
            print2('wh' if b.color == BLACK else 'bl', end='')
            break

        k = [t.translate_coords_from_human_readable(i) for i in h.split()]
        while len(k) != 2 or len(k[0]) != 2 or len(k[1]) != 2:
            print('Чтобы ходить, введите координаты полей через пробел(вначале буква, потом цифра)')
            print('Чтобы сдаться, введите "r"')
            if b.color == WHITE:
                h = input(timeout=b.time1)
            else:
                h = input(timeout=b.time2)
            if h == 'to':
                print('Ваше время истекло. Вы проиграли.')
                print2('Время у противника истекло. Вы выиграли!')
                print('wh' if b.color == BLACK else 'bl', end='')
                print2('wh' if b.color == BLACK else 'bl', end='')
            if h == 'exit':
                break
            if h == 'r':
                print('Вы сдались.')
                print2('Противник сдался')
                print('wh' if b.color == BLACK else 'bl', end='')
                print2('wh' if b.color == BLACK else 'bl', end='')
                break
            k = [t.translate_coords_from_human_readable(i) for i in h.split()]
        b.move_piece(k[0][0], k[0][1], k[1][0], k[1][1])


class Board:
    def __init__(self, time, add_time):
        self.color = WHITE
        self.field = []
        for row in range(8):
            self.field.append([None] * 8)
        """field[1][4] == E2"""
        self.prepare()
        self.sh = False
        self.mat = False
        self.pawn = [-1, -1, -1, -1]
        self.won = None
        self.dictboard = {}
        self.time1 = time
        self.time2 = time
        self.add_t = add_time
        self.t = t()

    @property
    def is_ended(self):
        if self.is_stalemate() or self.is_checkmate():
            return True
        self.change_color(False)
        if self.is_stalemate() or self.is_checkmate():
            self.change_color(False)
            return True
        return False

    def make_dictboard(self):
        self.dictboard = {}
        for row in range(8):
            for col in range(8):
                self.dictboard[f'{row}:{col}'] = self.field[row][col]

    def prepare(self):
        for i in range(8):
            self.field[1][i] = Pawn(1, i, WHITE)
            self.field[6][i] = Pawn(6, i, BLACK)
        for i in [0, 7]:
            cc = BLACK if i else WHITE
            self.field[i][0] = Rook(i, 0, cc)
            self.field[i][1] = Knight(i, 1, cc)
            self.field[i][2] = Bishop(i, 2, cc)
            self.field[i][3] = Queen(i, 3, cc)
            self.field[i][4] = King(i, 4, cc)
            self.field[i][5] = Bishop(i, 5, cc)
            self.field[i][6] = Knight(i, 6, cc)
            self.field[i][7] = Rook(i, 7, cc)

    def change_color(self, add_time=True):
        self.color = self.opponent(self.color)
        global print, print2, input, input2
        print, print2, input, input2 = print2, print, input2, input
        if add_time:
            if self.color == BLACK:
                self.time1 += self.add_t
                self.time1 -= t() - self.t
                self.t = t()
            else:
                self.time2 += self.add_t
                self.time2 -= t() - self.t
                self.t = t()

    @staticmethod
    def opponent(color):
        return not color

    def is_under_attack(self, row, col, color):
        '''Возвращает True, если field[row][col](т.е. поле row col)
         бьётся хотя бы одной фигурой цвета color'''
        if not self.correct_coords(row, col):
            return None
        self.make_dictboard()
        for i in range(8):
            for j in range(8):
                piece = self.field[i][j]
                if piece is None:
                    pass
                if isinstance(piece, Pawn):
                    if piece.get_color() == color:
                        if piece.can_eat(row, col):
                            return True
                elif isinstance(piece, Rook) or isinstance(piece, Knight) or isinstance(piece, Bishop) \
                        or isinstance(piece, Queen) or isinstance(piece, King):
                    if piece.get_color() == color:
                        if piece.can_move(row, col):
                            flag = True
                            for k in piece.move(row, col):
                                if self.dictboard[k] is None:
                                    pass
                                else:
                                    flag = False
                            if flag:
                                return True

        return False

    @staticmethod
    def correct_coords(row, col):
        """Функция проверяет, что координаты (row, col) лежат
        внутри доски"""
        return 0 <= row < 8 and 0 <= col < 8

    def current_player_color(self):
        return self.color

    def __getitem__(self, item):
        """Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела."""
        row, col = item
        piece = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def kings_is_under_attak(self):
        """Возвращает цвет короля под атакой, если один из королей атакован,
         если ни один не под атакой, возвращает None"""
        whiteking = None
        blackking = None
        for row in range(8):
            for col in range(8):
                if isinstance(self.field[row][col], King):
                    piece = self.field[row][col]
                    if piece.color == WHITE:
                        whiteking = [row, col]
                    if piece.color == BLACK:
                        blackking = [row, col]
        under_attak = None
        if self.is_under_attack(whiteking[0], whiteking[1], BLACK):
            under_attak = WHITE
        if self.is_under_attack(blackking[0], blackking[1], WHITE):
            under_attak = BLACK
        return under_attak

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        pawn = self.field[row][col]
        color = pawn.get_color()
        self.field[row][col] = None
        b = color == BLACK and row == 1
        w = color == WHITE and row == 6
        s = b or w
        if char == 'R' and s:
            self.field[row1][col1] = Rook(row, col, color)
            print('Ваша пешка превратилась в ладью')
            return True
        if char == 'N' and s:
            self.field[row1][col1] = Knight(row, col, color)
            print('Ваша пешка превратилась в коня')
            return True
        if char == 'B' and s:
            self.field[row1][col1] = Bishop(row, col, color)
            print('Ваша пешка превратилась в слона')
            return True
        if char == 'Q' and s:
            self.field[row1][col1] = Queen(row, col, color)
            print('Ваша пешка превратилась в ферзя')
            return True
        self.field[row][col] = pawn
        return False

    def rooking(self, row, col, row1, col1):
        if row != row1 or (row != 0 and row != 7):
            return False
        if col != 4 or (col1 != 6 and col1 != 2):
            return False
        color = WHITE if row else BLACK
        if col1 == 6:
            if self.field[row][5] is None and self.field[row][6] is None:
                if self.is_under_attack(row, 5, color) or self.is_under_attack(row, 6, color) \
                        or self.is_under_attack(row, 4, color):
                    print('рокировка через битое поле и рокировка под шах запрещены!')
                    return False
                if self.field[row][4] is None or self.field[row][7] is None:
                    print('Нельзя рокироваться, если ладья не на месте!')
                    return False
                if not isinstance(self.field[row][4], King) or not isinstance(self.field[row][7], Rook):
                    print('Рокироваться могут только король с ладьёй!')
                    return False
                if not self.field[row][4].isstatic() or not self.field[row][7].isstatic():
                    print('Нельзя рокироваться, если король ходил или ладья ходила!')
                    return False
                king = self.field[row][4]
                rook = self.field[row][7]
                self.field[row][4] = None
                king.set_position(row, 6)
                self.field[row][6] = king
                self.field[row][7] = None
                rook.set_position(row, 5)
                self.field[row][5] = rook
                return True
            else:
                return False
        if col1 == 2:
            if self.field[row][1] is None and self.field[row][2] is None and self.field[row][3] is None:
                if self.is_under_attack(row, 2, color) or self.is_under_attack(row, 3, color) \
                        or self.is_under_attack(row, 4, color):
                    print('рокировка через битое поле и рокировка под шах запрещены!')
                    return False
                if self.field[row][4] is None or self.field[row][0] is None:
                    print('Нельзя рокироваться, если ладья не на месте!')
                    return False
                if not isinstance(self.field[row][4], King) or not isinstance(self.field[row][0], Rook):
                    print('Рокироваться могут только король с ладьёй!')
                    return False
                if not self.field[row][4].isstatic() or not self.field[row][0].isstatic():
                    print('Нельзя рокироваться, если король ходил или ладья ходила!')
                    return False
                king = self.field[row][4]
                rook = self.field[row][0]
                self.field[row][4] = None
                king.set_position(row, 2)
                self.field[row][2] = king
                self.field[row][0] = None
                rook.set_position(row, 3)
                self.field[row][3] = rook
                return True
            else:
                return False
        return False

    def move_piece(self, row, col, row1, col1):
        """Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его и вернет True.
        Если нет --- вернет False"""

        if not self.correct_coords(row, col) or not self.correct_coords(row1, col1):
            print('Координаты некорректны. Такой ход невозможен!')
            return False
        if row == row1 and col == col1:
            print('Нельзя пойти в ту клетку, где стояла фигура изначально!')
            return False
        piece = self.field[row][col]
        if piece is None:
            print('На указанной клетке нет фигуры. Нечем ходить. Такой ход невозможен!')
            return False
        if piece.get_color() != self.color:
            print('На указанной клетке не Ваша фигура. Такой ход невозможен!')
            return False
        if self.field[row1][col1] is not None:
            if self.field[row1][col1].get_color() == self.color:
                print('Нельзя взять (снять с доски) свою фигуру!')

        piece = self.field[row][col]
        if isinstance(piece, King):
            if self.rooking(row, col, row1, col1):
                print('Ход завершён успешно!')
                self.change_color()
                self.pawn = [-1, -1, -1, -1]
                return True
        if isinstance(piece, Pawn):
            if piece.can_eat(row1, col1):
                p = self.pawn
                if piece.can_eat(p[0], p[1]):
                    piece.set_position(row1, col1)
                    self.field[row][col] = None
                    self.field[row1][col1] = piece
                    attacked = self.field[p[2]][p[3]]
                    self.field[p[2]][p[3]] = None
                    piece.set_position(row1, col1)
                    if self.kings_is_under_attak() is None:
                        self.sh = False
                        self.pawn = [-1, -1, -1, -1]
                        print('Ход завершён успешно!')
                        self.change_color()
                        return True
                    else:
                        if self.kings_is_under_attak() == self.color:
                            self.field[row1][col1] = None
                            self.field[row][col] = piece
                            piece.set_position(row, col)
                            self.field[p[2]][p[3]] = attacked
                            if self.sh:
                                print('Нельзя оставлять короля под шахом. Такой ход невозможен!')
                            else:
                                print('Нельзя подставлять короля под шах. Такой ход невозможен!')
                            return False
                if self.field[row1][col1] is None:
                    print('Пешки не могут двигаться так, как могут брать фигуры! Неверный ход!')
                    return False
                else:
                    self.field[row][col] = None
                    eated = self.field[row1][col1]
                    self.field[row1][col1] = piece
                    piece.set_position(row1, col1)
                    if self.kings_is_under_attak() is None:
                        self.sh = False
                    else:
                        if self.kings_is_under_attak() == self.color:
                            self.field[row1][col1] = eated
                            self.field[row][col] = piece
                            piece.set_position(row, col)
                            if self.sh:
                                print('Нельзя оставлять короля под шахом. Такой ход невозможен!')
                            else:
                                print('Нельзя подставлять короля под шах. Такой ход невозможен!')
                            return False

                    if row1 == 7 or row1 == 0:
                        self.field[row1][col1] = None
                        self.field[row][col] = piece
                        print('Превращение пешки! Введите символ("Q"-ферзь, "B"-слон, "N"-конь, "R"-ладья)')
                        if self.color == WHITE:
                            char = input(timeout=self.time1)
                        else:
                            char = input(timeout=self.time2)
                        if char == 'to':
                            print('Ваше время истекло. Вы проиграли.')
                            print2('Время у противника истекло. Вы выиграли!')
                            print('wh' if self.color == BLACK else 'bl', end='')
                            print2('wh' if self.color == BLACK else 'bl', end='')
                        while char not in ['Q', 'B', 'N', 'R']:
                            print('Вы ввели неправильный символ. Попробуйте ещё раз.')
                            print('Превращение пешки! Введите символ("Q"-ферзь, "B"-слон, "N"-конь, "R"-ладья)')
                            if self.color == WHITE:
                                char = input(timeout=self.time1)
                            else:
                                char = input(timeout=self.time2)
                            if char == 'to':
                                print('Ваше время истекло. Вы проиграли.')
                                print2('Время у противника истекло. Вы выиграли!')
                                print('wh' if self.color == BLACK else 'bl', end='')
                                print2('wh' if self.color == BLACK else 'bl', end='')
                        if self.move_and_promote_pawn(row, col, row1, col1, char):
                            if self.kings_is_under_attak() is not None:
                                if self.kings_is_under_attak() != self.color:
                                    self.change_color(False)
                                    print('Вашему королю объявлен шах')
                                    self.change_color(False)
                                    self.sh = True
                            print('Ход завершён успешно!')
                            self.pawn = [-1, -1, -1, -1]
                            self.change_color()
                            return True
                        else:
                            return False
                    print('Ход завершён успешно!')
                    self.change_color()
                    self.pawn = [-1, -1, -1, -1]
                    return True
            if piece.can_move(row1, col1):
                __pawn = [-1, -1, -1, -1]
                if self.field[row1][col1] is None:
                    if piece.move(row1, col1):
                        self.make_dictboard()
                        if self.dictboard[piece.move(row1, col1)[0]] is not None:
                            print('Пешка не может прыгать через фигуры, даже с начальной позиции')
                            return False
                        __pawn = [int(i) for i in piece.move(row1, col1)[0].split(':')] + [row1, col1]

                    self.field[row][col] = None
                    self.field[row1][col1] = piece
                    piece.set_position(row1, col1)
                    if self.kings_is_under_attak() is None:
                        self.sh = False
                    else:
                        if self.kings_is_under_attak() == piece.color:
                            self.field[row1][col1] = None
                            self.field[row][col] = piece
                            piece.set_position(row, col)
                            if self.sh:
                                print('Нельзя оставлять короля под шахом. Такой ход невозможен!')
                            else:
                                print('Нельзя подставлять короля под шах. Такой ход невозможен!')
                            return False

                    if row1 == 7 or row1 == 0:
                        self.field[row1][col1] = None
                        self.field[row][col] = piece
                        print('Превращение пешки! Введите символ("Q"-ферзь, '
                              '"B"-слон, "N"-конь, "R"-ладья)')
                        if self.color == WHITE:
                            char = input(timeout=self.time1)
                        else:
                            char = input(timeout=self.time2)
                        if char == 'to':
                            print('Ваше время истекло. Вы проиграли.')
                            print2('Время у противника истекло. Вы выиграли!')
                            print('wh' if self.color == BLACK else 'bl', end='')
                            print2('wh' if self.color == BLACK else 'bl', end='')
                        while char not in ['Q', 'B', 'N', 'R']:
                            print('Вы ввели неправильный символ. Попробуйте ещё раз.')
                            print('Превращение пешки! Введите символ("Q"-ферзь, '
                                  '"B"-слон, "N"-конь, "R"-ладья)')
                            if self.color == WHITE:
                                char = input(timeout=self.time1)
                            else:
                                char = input(timeout=self.time2)
                            if char == 'to':
                                print('Ваше время истекло. Вы проиграли.')
                                print2('Время у противника истекло. Вы выиграли!')
                                print('wh' if self.color == BLACK else 'bl', end='')
                                print2('wh' if self.color == BLACK else 'bl', end='')
                        if self.move_and_promote_pawn(row, col, row1, col1, char):
                            if not (self.kings_is_under_attak() is None):
                                if self.kings_is_under_attak() != self.color:
                                    self.change_color(False)
                                    print('Вашему королю объявлен шах')
                                    self.change_color(False)
                                    self.sh = True
                            print('Ход завершён успешно!')
                            self.pawn = __pawn
                            self.change_color()
                            return True
                        else:
                            return False
                    print('Ход завершён успешно!')
                    self.change_color()
                    self.pawn = __pawn
                    return True
                else:
                    print('Пешки берут фигуры не так как движутся! Неверный ход!')
                    return False

        if not piece.can_move(row1, col1):
            print('Указанная Вами фигура так ходить не может. Такой ход невозможен!')
            return False
        self.make_dictboard()
        for i in piece.move(row1, col1):
            if self.dictboard[i] is None:
                pass
            else:
                print('Указанная Вами фигура - не конь. Она не может прыгать через фигуры.'
                      ' Такой ход невозможен!')
                return False
        if self.field[row1][col1] is not None:
            if self.field[row1][col1].get_color() == piece.get_color():
                print('Вы не можете взять (снять с доски) фигуру своего цвета. Такой ход невозможен! ')
                return False
        if isinstance(piece, King):
            if self.is_under_attack(row1, col1, self.opponent(piece.get_color())):
                print('Вы не можете ходить королём под шах. Такой ход невозможен!')
                return False
        attacked = self.field[row1][col1]
        self.field[row][col] = None
        self.field[row1][col1] = piece
        piece.set_position(row1, col1)
        if self.kings_is_under_attak() is None:
            self.sh = False
        else:
            if self.kings_is_under_attak() == self.color:
                self.field[row1][col1] = attacked
                self.field[row][col] = piece
                piece.set_position(row, col)
                if self.sh:
                    print('Нельзя оставлять короля под шахом. Такой ход невозможен!')
                else:
                    print('Нельзя подставлять короля под шах. Такой ход невозможен!')
                return False
        print('Ход завершён успешно!')
        self.change_color()
        self.make_dictboard()
        if self.kings_is_under_attak() is not None:
            if self.kings_is_under_attak() == self.color:
                print('Вашему королю объявлен шах')
                self.sh = True
        self.pawn = [-1, -1, -1, -1]
        return True

    def is_stalemate(self):
        '''Пат?'''
        if self.kings_is_under_attak() is not None:
            return False
        self.make_dictboard()
        color = self.color
        for i in range(8):
            for j in range(8):
                piece = self.field[i][j]
                if piece is None:
                    continue
                if piece.get_color() != color:
                    continue

                for i1 in range(8):
                    for j1 in range(8):
                        fl = False
                        if isinstance(piece, Pawn):
                            if piece.can_eat(i1, j1):
                                fl = True
                        if piece.can_move(i1, j1) or fl:
                            flag = True
                            if self.field[i1][j1] is not None:
                                if self.field[i1][j1].get_color() == color:
                                    continue
                                if isinstance(piece, Pawn):
                                    continue
                            for k in piece.move(i1, j1):
                                if self.dictboard[k] is not None:
                                    flag = False
                                    break
                            if flag:
                                piece2 = self.field[i1][j1]
                                self.field[i1][j1] = piece
                                self.field[i][j] = None
                                piece.set_position(i1, j1)
                                if self.kings_is_under_attak() is not None:
                                    self.field[i1][j1] = piece2
                                    self.field[i][j] = piece
                                    piece.set_position(i, j)
                                else:
                                    self.field[i1][j1] = piece2
                                    self.field[i][j] = piece
                                    piece.set_position(i, j)
                                    return False
        return True

    def is_checkmate(self):
        '''Мат?'''
        if self.kings_is_under_attak() is None:
            return False
        self.make_dictboard()
        color = self.color
        for i in range(8):
            for j in range(8):
                piece = self.field[i][j]
                if piece is None:
                    continue
                if piece.get_color() != color:
                    continue

                for i1 in range(8):
                    for j1 in range(8):
                        fl = False
                        if isinstance(piece, Pawn):
                            if piece.can_eat(i1, j1):
                                fl = True
                        if piece.can_move(i1, j1) or fl:
                            flag = True
                            if self.field[i1][j1] is not None:
                                if self.field[i1][j1].get_color() == color:
                                    continue
                                if isinstance(piece, Pawn):
                                    continue
                            for k in piece.move(i1, j1):
                                if self.dictboard[k] is not None:
                                    flag = False
                                    break
                            if flag:
                                piece2 = self.field[i1][j1]
                                self.field[i1][j1] = piece
                                self.field[i][j] = None
                                piece.set_position(i1, j1)
                                if self.kings_is_under_attak() is not None:
                                    self.field[i1][j1] = piece2
                                    self.field[i][j] = piece
                                    piece.set_position(i, j)
                                else:
                                    self.field[i1][j1] = piece2
                                    self.field[i][j] = piece
                                    piece.set_position(i, j)
                                    return False
        return True


class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.static = True  # двигалась ли фигура

    def get_color(self):
        return self.color

    def set_position(self, row1, col1):
        self.row = row1
        self.col = col1
        self.static = False

    def isstatic(self):
        return self.static

    @staticmethod
    def move(row, col):
        return []


class Knight(Piece):
    @staticmethod
    def char():
        return 'N'

    def can_move(self, row1, col1):
        if self.col + 2 == col1 and self.row + 1 == row1:
            return True
        if self.col - 2 == col1 and self.row + 1 == row1:
            return True
        if self.col + 2 == col1 and self.row - 1 == row1:
            return True
        if self.col - 2 == col1 and self.row - 1 == row1:
            return True
        if self.col + 1 == col1 and self.row + 2 == row1:
            return True
        if self.col - 1 == col1 and self.row + 2 == row1:
            return True
        if self.col + 1 == col1 and self.row - 2 == row1:
            return True
        if self.col - 1 == col1 and self.row - 2 == row1:
            return True
        else:
            return False


class Rook(Piece):
    @staticmethod
    def char():
        return 'R'

    def can_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False

        if self.row != row and self.col != col:
            return False

        return True

    def move(self, row, col):
        if self.row == row:
            if self.col > col:
                temp = list(range(col + 1, self.col))
            else:
                temp = list(range(self.col + 1, col))
            return [f'{row}:{i}' for i in temp]
        else:
            if self.row > row:
                temp = list(range(row + 1, self.row))
            else:
                temp = list(range(self.row + 1, row))
            return [f'{i}:{col}' for i in temp]


class Bishop(Piece):
    @staticmethod
    def char():
        return 'B'

    def can_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        elif abs(row - self.row) == abs(col - self.col):
            return True
        else:
            return False

    def move(self, row, col):
        if row - self.row > 0:
            if col - self.col > 0:
                temp = [f'{self.row + i}:{self.col + i}' for i in range(1, abs(row - self.row))]
            else:
                temp = [f'{self.row + i}:{self.col - i}' for i in range(1, abs(row - self.row))]
        else:
            if col - self.col > 0:
                temp = [f'{self.row - i}:{self.col + i}' for i in range(1, abs(row - self.row))]
            else:
                temp = [f'{self.row - i}:{self.col - i}' for i in range(1, abs(row - self.row))]
        return temp


class Queen(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.r = Rook(row, col, color)
        self.b = Bishop(row, col, color)

    @staticmethod
    def char():
        return 'Q'

    def can_move(self, row, col):
        if self.b.can_move(row, col) or self.r.can_move(row, col):
            return True
        else:
            return False

    def set_position(self, row1, col1):
        self.row = row1
        self.col = col1
        self.b.set_position(row1, col1)
        self.r.set_position(row1, col1)
        self.static = False

    def move(self, row, col):
        if self.r.can_move(row, col):
            return self.r.move(row, col)
        if self.b.can_move(row, col):
            return self.b.move(row, col)


class Pawn(Piece):
    @staticmethod
    def char():
        return 'P'

    def can_eat(self, row, col):
        if self.color == WHITE:
            if self.col == col + 1 and self.row == row - 1:
                return True
            if self.col == col - 1 and self.row == row - 1:
                return True
        else:
            if self.col == col + 1 and self.row == row + 1:
                return True
            if self.col == col - 1 and self.row == row + 1:
                return True
        return False

    def can_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False

        if self.col != col:
            return False
        direction = 1 if self.color == WHITE else -1
        start_row = 1 if self.color == WHITE else 6

        # ход на 1 клетку
        if self.row + direction == row:
            return True

        # ход на 2 клетки из начального положения
        if self.row == start_row and self.row + 2 * direction == row:
            return True

        return False

    def move(self, row, col):
        if self.row == 1 and self.row + 2 == row:
            return [f'2:{col}']
        elif self.row == 6 and self.row - 2 == row:
            return [f'5:{col}']
        else:
            return []


class King(Piece):
    @staticmethod
    def char():
        return 'K'

    def can_move(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        r = self.row
        c = self.col
        if r == row and c == col:
            return False
        if c + 1 == col or c - 1 == col or c == col:
            if r - 1 == row or r + 1 == row or r == row:
                return True
        return False


if __name__ == '__main__':
    def print_board(board):
        print('     +----+----+----+----+----+----+----+----+')
        for row in range(7, -1, -1):
            print(' ', row + 1, end='  ')
            for col in range(8):
                print('|', board[row, col], end=' ')
            print('|')
            print('     +----+----+----+----+----+----+----+----+')
        print(end='        ')
        for col in list('abcdefgh'):
            print(col, end='    ')
        print()
        print()
        return ''


    class Input:
        def __init__(self):
            self.lst = 'e2 e4\nf1 c4\nd1 f3\nf3 f7'.split('\n')
            self.counter = -1

        def __call__(self, *args, **kwargs):
            self.counter += 1
            try:
                return self.lst[self.counter]
            except IndexError:
                return ''


    class Input2:
        def __init__(self):
            self.lst = 'e7 e5\nf8 c5\na7 a6'.split('\n')
            self.counter = -1

        def __call__(self, *args, **kwargs):
            self.counter += 1
            try:
                return self.lst[self.counter]
            except IndexError:
                return ''


    play(print_board, print, print, Input(), Input2())
