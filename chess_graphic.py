import pygame.image
from pygame.image import load, save
from pygame import Surface, SRCALPHA
from pygame.sprite import Sprite, Group
from pygame.transform import scale
from pygame.font import Font
from chess import Board as ChessBoard
from pygame import init
from chess import play as p

init()
SIZE = (500, 500)


class PieceSprite(Sprite):
    def __init__(self, group, columns, rows, x, y, pos, sheet='chess.png'):
        super().__init__(group)
        self.col = (255, 255, 255) if (pos[0] + pos[1]) % 2 else (127, 127, 127)
        self.frames = []
        self.cut_sheet(load(sheet), columns, rows)
        self.image = None
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(scale(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)), (50, 50), Surface((50, 50), SRCALPHA)))
        self.frames.append(Surface((50, 50), SRCALPHA))
        self.frames[-1].fill(self.col)

    def set_piece(self, piece):
        piece = {'wK': 0, 'wQ': 1, 'wB': 2, 'wN': 3, 'wR': 4, 'wP': 5, 'bK': 6, 'bQ': 7, 'bB': 8, 'bN': 9, 'bR': 10,
                 'bP': 11, '  ': 12}[piece]
        self.image = self.frames[piece]


class TextSprite(Sprite):
    def __init__(self, group, x, y, text):
        super().__init__(group)
        self.image = Surface((50, 50), SRCALPHA)
        txt = Font(None, 50).render(text, True, (0, 0, 0))
        self.image.blit(txt, (15, 10))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


class TimeSprite(Sprite):
    def __init__(self, group, x, y, text, color):
        from chess import BLACK
        super().__init__(group)
        self.image = Surface((200, 50), SRCALPHA)
        txt = Font(None, 50).render(text, True, (0, 0, 0) if color == BLACK else (255, 255, 255))
        self.image.blit(txt, (0, 10))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


class Board:
    def __init__(self, time, add_time, left=50, top=50, cell_size=50, sheet='chess.png'):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.g = Group()
        lst = list('87654321')
        for i in range(8):
            TextSprite(self.g, 0, cell_size * (i + 1), lst[i])

        lst = list('abcdefgh')
        for i in range(8):
            TextSprite(self.g, cell_size * (i + 1), cell_size * 8 + top, lst[i])

        self.board = [
            [PieceSprite(self.g, 6, 2, i * cell_size + left, j * cell_size + top, (i, j), sheet) for i in range(8)] for
            j in range(8)]
        self.chessboard = ChessBoard(time, add_time)
        self.t = None

    def render(self, image):
        from chess import WHITE, BLACK
        if self.t is not None:
            self.g.remove(self.t[0], self.t[1])

        self.t = TimeSprite(self.g, 50, 0, f'{self.chessboard.time1:.4f}', WHITE), \
            TimeSprite(self.g, 250, 0, f'{self.chessboard.time2:.4f}', BLACK)
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].set_piece('  ')
        self.g.draw(image)
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].set_piece(self.chessboard[7 - i, j])
        self.g.draw(image)


class Play:
    def __init__(self, time, add_time):
        self.t = time, add_time

    def __call__(s, printfunc, printfunc2, input_string_func, input_string_func_2):
        s.b = Board(*s.t)
        s.img = Surface(SIZE, SRCALPHA)
        s.img.fill((0, 255, 0))

        class BoardOutput:
            def __init__(self):
                from os import getpid
                self.id = getpid()
                self.f = True

            def __call__(self, board):
                if self.f:
                    s.b.chessboard = board
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
        p(board_output_func, printfunc, printfunc2, input_string_func, input_string_func_2, *s.t)


if __name__ == '__main__':
    Play(0, 0)(print, print, input, input)
