from xo import XOBoard
from pickle import loads
from xo import Translator

from xoAI_creator import VarTreeNode
import __main__

__main__.__dict__['VarTreeNode'] = VarTreeNode  # требуется, чтобы a и b успешно загрузились из файла
a, b = loads(open('_', 'rb').read())


class XOAI:
    @staticmethod
    def find_node(motions, tree):
        t = tree
        for i in t.childs:
            if i.motion == motions[-1]:
                return i

    @staticmethod
    def choice_motion(tree):
        return tree.childs[0].motion


def play1(board_output_func, input_func, output_func, ai_userid=-1):
    sh = XOBoard.X
    n = a
    g = XOBoard()
    t = Translator()
    motions = []
    from db_command import inc_xo_rating, dec_xo_rating
    while not g.is_ended:
        motions.append(XOAI.choice_motion(n))
        g.motion(*motions[-1])
        n = XOAI.find_node(motions, n)
        output_func('img:' + board_output_func(g))
        if g.is_ended:
            break
        output_func('Введите координаты клетки, в которой Вы хотите поставить свой знак')
        i = input_func(timeout=g.time)
        if i == 'to':
            output_func('Ваше время вышло. Вы проиграли.')
            inc_xo_rating(ai_userid)
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
                inc_xo_rating(ai_userid)
                output_func('-', end='')
                return
        motions.append(t.translate_coords_from_human_readable(i))
        g.motion(*motions[-1])
        n = XOAI.find_node(motions, n)
    if g.is_win and g.shape == sh:
        output_func('Вы проиграли.')
        output_func('-', end='')
        inc_xo_rating(ai_userid)
    elif g.is_win:
        output_func('Вы выиграли!')
        output_func('+', end='')
        dec_xo_rating(ai_userid)
    else:
        output_func('Ничья!')
        output_func('=', end='')


def play2(board_output_func, input_func, output_func, ai_userid=-1):
    sh = XOBoard.O
    n = b
    g = XOBoard()
    motions = []
    t = Translator()
    from db_command import inc_xo_rating, dec_xo_rating
    while not g.is_ended:
        output_func('img:' + board_output_func(g))
        output_func('Введите координаты клетки, в которой Вы хотите поставить свой знак')
        i = input_func(timeout=g.time)
        if i == 'to':
            output_func('Ваше время вышло. Вы проиграли.')
            inc_xo_rating(ai_userid)
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
                inc_xo_rating(ai_userid)
                output_func('-', end='')
                return
        motions.append(t.translate_coords_from_human_readable(i))
        g.motion(*motions[-1])
        n = XOAI.find_node(motions, n)
        if g.is_ended:
            break
        motions.append(XOAI.choice_motion(n))
        g.motion(*motions[-1])
        n = XOAI.find_node(motions, n)
    if g.is_win and g.shape == sh:
        output_func('Вы проиграли.')
        output_func('-', end='')
        inc_xo_rating(ai_userid)
    elif g.is_win:
        output_func('Вы выиграли!')
        output_func('+', end='')
        dec_xo_rating(ai_userid)
    else:
        output_func('Ничья!')
        output_func('=', end='')


if __name__ == '__main__':
    def print_board(b):
        print(b)
        return ''


    def _input(timeout=30):
        return input()


    play1(print_board, _input, print)
    play2(print_board, _input, print)
