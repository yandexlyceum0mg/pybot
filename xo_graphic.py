from pygame.image import save
from pygame import Surface, SRCALPHA
from pygame.sprite import Sprite, Group
from pygame.font import Font
from pygame import init
from pygame.draw import line, circle
from xo import XOBoard, play
from xoAI import play1, play2

init()
SIZE = (250, 250)


class TextSprite(Sprite):
    def __init__(self, group, x, y, text):
        super().__init__(group)
        self.image = Surface((50, 50), SRCALPHA)
        txt = Font(None, 50).render(text, True, (0, 0, 0))
        self.image.blit(txt, (15, 10))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


class ShapeSprite(Sprite):
    def __init__(self, group, x, y, pos):
        super().__init__(group)
        self.col = (255, 255, 255) if (pos[0] + pos[1]) % 2 else (127, 127, 127)
        self.frames = []
        self.frames.append(Surface((50, 50), SRCALPHA))
        self.frames[-1].fill(self.col)
        self.l_ = line(self.frames[-1], (0, 0, 0), (0, 0), (50, 50), 5)
        self.l__ = line(self.frames[-1], (0, 0, 0), (0, 50), (50, 0), 5)
        self.frames.append(Surface((50, 50), SRCALPHA))
        self.frames[-1].fill(self.col)
        self.c_ = circle(self.frames[-1], (0, 0, 0), (25, 25), 22.5, 5)
        self.frames.append(Surface((50, 50), SRCALPHA))
        self.frames[-1].fill(self.col)

        self.image = self.frames[-1]
        self.rect = self.image.get_rect().move(x, y)

    def set_shape(self, shape):
        self.image = self.frames[{'X': 0, 'O': 1, '.': 2}[shape]]
        self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)


class Board:
    def __init__(self, time=30, left=50, top=50, cell_size=50):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.g = Group()
        lst = list('321')
        for i in range(3):
            TextSprite(self.g, 0, cell_size * (i + 1), lst[i])

        lst = list('abc')
        for i in range(3):
            TextSprite(self.g, cell_size * (i + 1), cell_size * 3 + top, lst[i])

        self.board = [
            [ShapeSprite(self.g, i * cell_size + left, j * cell_size + top, (i, j)) for i in range(3)] for
            j in range(3)]
        self.xoboard = XOBoard(time)
        # self.t = None

    def render(self, image):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].set_shape(self.xoboard[2 - i, j])
        self.g.draw(image)


class PlayAI:
    def __init__(self, time=30, ai_is_first=True):
        self.t = time
        self.ai_is_first = ai_is_first

    def __call__(s, input_func, output_func, ai_userid):
        s.b = Board(s.t)
        s.img = Surface(SIZE, SRCALPHA)
        s.img.fill((0, 255, 0))

        class BoardOutput:
            def __init__(self):
                from os import getpid
                self.id = getpid()
                self.f = True

            def __call__(self, board):
                if self.f:
                    s.b.xoboard = board
                s.img.fill((0, 255, 0))
                s.b.render(s.img)
                while True:
                    try:
                        save(s.img, f'tmp/img.{self.id}.png')
                    except:
                        pass
                    else:
                        break
                return f'tmp/img.{self.id}.png'

        board_output_func = BoardOutput()
        if s.ai_is_first:
            play1(board_output_func, input_func, output_func, ai_userid)
        else:
            play2(board_output_func, input_func, output_func, ai_userid)


class PlayXO:
    def __init__(self, time=30):
        self.t = time

    def __call__(s, output_func, output_func2, input_func, input_func2):
        s.b = Board(s.t)
        s.img = Surface(SIZE, SRCALPHA)
        s.img.fill((0, 255, 0))

        class BoardOutput:
            def __init__(self):
                from os import getpid
                self.id = getpid()
                self.f = True

            def __call__(self, board):
                if self.f:
                    s.b.xoboard = board
                s.img.fill((0, 255, 0))
                s.b.render(s.img)
                while True:
                    try:
                        save(s.img, f'tmp/img.{self.id}.png')
                    except:
                        pass
                    else:
                        break
                return f'tmp/img.{self.id}.png'

        board_output_func = BoardOutput()
        play(board_output_func, input_func, output_func, input_func2, output_func2)
