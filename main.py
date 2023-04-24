from xoAI_creator import create_ai_if_not_exists
# вызов функции create_ai_if_not_exists() записан в xoAI_creator и вызовется при импорте
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from cfg import BOT_TOKEN  # токен бота написан в файле cfg.py
from random import randint
from multiprocessing import Process, Queue
from threading import Thread
from chess_graphic import Play as PlayChess
from asyncio import sleep
from db_command import add_user, dec_chess_rating, inc_chess_rating, get_chess_rating, dec_xo_rating, \
    inc_xo_rating, get_xo_rating, createdb_and_globinit_if_db_not_exists_else_globinit, user_is_exists
from xo_graphic import PlayAI, PlayXO
from weather import weather
from os.path import exists
from os import mkdir

RETRY_SEND = 50


class MyCycleCoroutine:
    def __init__(self, func, args):
        self.is_ended = False
        self.func = func
        self.args = args

    async def __call__(self):
        if not self.is_ended:
            await self.func(self, *self.args)


class Worker:
    def __init__(self):
        self.stopped = False
        self.coroutines = []
        self.ind = 0
        self.t = Thread(target=self.work)
        self.t.start()

    def work(self):
        while not self.stopped:
            async def __t():
                while True:
                    for i in self.coroutines:
                        if i.is_ended:
                            continue
                        await i()

            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(__t())
        raise Exception()  # остановить поток

    def __call__(self, cyccor):
        self.coroutines.append(cyccor)

    def stop(self):
        self.stopped = True


def _cleaner_garbage():
    hgch = []
    for i in half_games_chess.keys():
        if half_games_chess[i].is_ended:
            # half_games_chess[i].t.join()
            hgch.append(i)
    for i in hgch:
        del half_games_chess[i].g
        del half_games_chess[i]
    gch = []
    for i in range(len(games_chess)):
        if games_chess[i].is_ended:
            games_chess[i].process.kill()
            gch.append(i)
    for i in gch:
        del games_chess[i]
    gxoai = []
    for i in games_xoai.keys():
        if games_xoai[i].is_ended:
            games_xoai[i].p.kill()
            gxoai.append(i)
    for i in gxoai:
        del games_xoai[i]
    hgxo = []
    for i in half_games_xo.keys():
        if half_games_xo[i].is_ended:
            hgxo.append(i)
    for i in hgxo:
        del half_games_xo[i].g
        del half_games_xo[i]
    gxo = []
    for i in range(len(games_xo)):
        if games_xo[i].is_ended:
            games_xo[i].process.kill()
            gxo.append(i)
    for i in gxo:
        del games_xo[i]


def garbage_cleaner_thread():
    from time import sleep
    while True:
        _cleaner_garbage()
        sleep(0.1)


def cleaner_garbage():
    global garbage_cleaner
    garbage_cleaner = Thread(target=garbage_cleaner_thread)
    garbage_cleaner.start()


class XOAIGame:
    def __init__(self, userid):
        self.userid = userid
        self.input = Input()
        self.output = OutputXOAI()
        self.is_started = False
        self.is_ended = False
        self.p = Process(target=PlayAI(ai_is_first=randint(0, 1)), args=(self.input, self.output, -1))
        self.p.start()
        self.is_started = True


class HalfXOGame:
    def __init__(self, userid):
        self.userid = userid
        self.input = Input()
        self.output = OutputXO()
        self.is_started = False
        self.is_ended = False
        self.g = None

    def setgame(self, g):
        self.g = g


class XOGame:
    def __init__(self, half_game1, half_game2):
        if randint(0, 1) == 1:
            half_game1, half_game2 = half_game2, half_game1
        self.halfes_game = half_game1, half_game2
        self.process = Process(target=PlayXO(),
                               args=(half_game1.output, half_game2.output, half_game1.input, half_game2.input))
        self.process.start()
        half_game1.is_started = True
        half_game2.is_started = True

    @property
    def is_ended(self):
        if self.halfes_game[0].is_ended or self.halfes_game[1].is_ended:
            return True


class HalfChessGame:
    def __init__(self, userid, rating, minrating, maxrating, time_of_game, time_of_motion, output):
        self.userid = userid
        self.rating = rating
        self.rating_other = (minrating, maxrating)
        self.t_motion = time_of_motion
        self.t_game = time_of_game
        self.input = Input()
        self.output = output
        self.is_ended = False
        self.is_started = False
        self.g = None
        self.t = None

    def setgame(self, g):
        self.g = g


class ChessGame:
    def __init__(self, half_game1, half_game2):
        if randint(0, 1) == 1:
            half_game1, half_game2 = half_game2, half_game1
        userid1, userid2 = half_game1.userid, half_game2.userid
        self.white, self.black = userid1, userid2
        self.halfes_game = half_game1, half_game2
        self.process = Process(target=PlayChess(half_game1.t_game, half_game1.t_motion),
                               args=(half_game1.output, half_game2.output, half_game1.input, half_game2.input))
        self.process.start()
        half_game1.is_started = True
        half_game2.is_started = True

    @property
    def is_ended(self):
        if self.halfes_game[0].is_ended or self.halfes_game[1].is_ended:
            return True


class Input:
    def __init__(self):
        self.q = Queue()

    def __call__(self, timeout, *args, **kwargs):
        try:
            return self.q.get(timeout=timeout)
            # if timeout != float('inf'):
            #     return self.q.get(timeout=timeout)
            # else:
            #     return self.q.get()
        except Exception:
            return 'to'

    def __iadd__(self, other):
        while True:
            try:
                self.q.put(other)
            except:
                pass
            else:
                break
        return self


class Output:
    def __init__(self):
        self.q = Queue()

    def __call__(self, *args, sep=' ', end='\n'):
        while True:
            try:
                self.q.put(sep.join([str(i) for i in args]) + end)
            except:
                pass
            else:
                break

    def output(self, outtext, outphoto, halfgame):
        async def func(s, outtext, outphoto, halfgame):
            if not halfgame.is_started:
                return None
            try:
                text = self.q.get(block=False)
            except Exception:
                await sleep(0.1)
                return None
            if text == 'pt':
                halfgame.is_ended = True
                s.is_ended = True
                return None
            elif text == 'wh' and halfgame.g.white == halfgame.userid:
                inc_chess_rating(halfgame.userid)
                halfgame.is_ended = True
                s.is_ended = True
                return None
            elif text == 'wh':
                dec_chess_rating(halfgame.userid)
                halfgame.is_ended = True
                s.is_ended = True
                return None
            elif text == 'bl' and halfgame.g.black == halfgame.userid:
                inc_chess_rating(halfgame.userid)
                halfgame.is_ended = True
                s.is_ended = True
                return None
            elif text == 'bl':
                dec_chess_rating(halfgame.userid)
                halfgame.is_ended = True
                s.is_ended = True
                return None
            else:
                if text.startswith('img:'):
                    text = text.removeprefix('img:').removesuffix('\n')
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outphoto(photo=open(text, 'rb'), caption='Шахматы')
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break
                else:
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outtext(text)
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break

        worker(MyCycleCoroutine(func, (outtext, outphoto, halfgame)))


class OutputXOAI:
    def __init__(self):
        self.q = Queue()

    def __call__(self, *args, sep=' ', end='\n'):
        while True:
            try:
                self.q.put(sep.join([str(i) for i in args]) + end)
            except:
                pass
            else:
                break

    def output(self, outtext, outphoto, game):
        async def func(s, outtext, outphoto, game):
            if not game.is_started:
                return None
            try:
                text = self.q.get(block=False)
            except Exception:
                await sleep(0.1)
                return None
            if text == '-':
                game.is_ended = True
                dec_xo_rating(game.userid)
                s.is_ended = True
                return None
            if text == '+':
                game.is_ended = True
                inc_xo_rating(game.userid)
                s.is_ended = True
                return None
            if text == '=':
                game.is_ended = True
                s.is_ended = True
                return None
            else:
                if text.startswith('img:'):
                    text = text.removeprefix('img:').removesuffix('\n')
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outphoto(photo=open(text, 'rb'))
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break
                else:
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outtext(text)
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break

        worker(MyCycleCoroutine(func, (outtext, outphoto, game)))


class OutputXO:
    def __init__(self):
        self.q = Queue()

    def __call__(self, *args, sep=' ', end='\n'):
        while True:
            try:
                self.q.put(sep.join([str(i) for i in args]) + end)
            except:
                pass
            else:
                break

    def output(self, outtext, outphoto, halfgame):
        async def func(s, outtext, outphoto, halfgame):
            if not halfgame.is_started:
                return None
            try:
                text = self.q.get(block=False)
            except Exception:
                await sleep(0.1)
                return None
            if text == '-':
                halfgame.is_ended = True
                dec_xo_rating(halfgame.userid)
                s.is_ended = True
                return None
            if text == '+':
                halfgame.is_ended = True
                inc_xo_rating(halfgame.userid)
                s.is_ended = True
                return None
            if text == '=':
                halfgame.is_ended = True
                s.is_ended = True
                return None
            else:
                if text.startswith('img:'):
                    text = text.removeprefix('img:').removesuffix('\n')
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outphoto(photo=open(text, 'rb'))
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break
                else:
                    c = 0
                    while True:
                        try:
                            c += 1
                            await outtext(text)
                        except:
                            if c == RETRY_SEND:
                                raise
                            pass
                        else:
                            break

        worker(MyCycleCoroutine(func, (outtext, outphoto, halfgame)))


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(f"Привет {user.mention_html()}! Я pybot!\n"
                                    f"Чтобы узнать мои команды, напишите мне /help")


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я pybot.\n"
                                    "Чтобы узнать погоду, напишите мне /weather <Город>\n"
                                    "Чтобы сыграть в крестики-нолики со мной, напишите мне /xoai\n"
                                    "Чтобы сыграть в крестики-нолики с другим игроком, напишите мне /xo\n"
                                    "Чтобы сыграть в шахматы с другим игроком напишите мне /chess <минимальный"
                                    " рейтинг противника> <максимальный рейтинг противника> <время игры в минутах>"
                                    "<добавочное время на ход в секундах> (можно также написать /chess без аргументов)"
                                    "\nЧтобы узнать свой рейтинг, напишите мне /rating")


async def handle(update, context):
    def diff_is_normal(a, b):
        return a / b > 0.75 and b / a > 0.75

    def _time(a):
        try:
            return float(a) * 60
        except:
            return 600

    def _add_time(a):
        try:
            return float(a)
        except:
            return 10

    def ratmin(a):
        try:
            return float(a)
        except:
            return float('-inf')

    def ratmax(a):
        try:
            return float(a)
        except:
            return float('inf')

    usr = update.message.chat
    msg = update.message.text

    if usr.id not in pipes.keys():
        __ = type('', tuple(), {})()  # создатся объект с __dict__
        __.__dict__ = {'reply_text': update.message.reply_text, 'reply_photo': update.message.reply_photo}
        pipes[usr.id] = __

    if usr.id in half_games_chess.keys():
        if not half_games_chess[usr.id].is_ended:
            half_games_chess[usr.id].input += msg
            return None
    if usr.id in games_xoai.keys():
        if not games_xoai[usr.id].is_ended:
            games_xoai[usr.id].input += msg
            return None

    if usr.id in half_games_xo.keys():
        if not half_games_xo[usr.id].is_ended:
            half_games_xo[usr.id].input += msg
            return None

    if msg.startswith('/rating'):
        await update.message.reply_text(f'Ваш рейтинг в шахматах: {get_chess_rating(usr.id)}\n'
                                        f'Ваш рейтинг в крестиках-ноликах: {get_xo_rating(usr.id)}')

    if msg.startswith('/xoai'):
        games_xoai[usr.id] = XOAIGame(usr.id)

        games_xoai[usr.id].output.output(pipes[usr.id].reply_text, pipes[usr.id].reply_photo, games_xoai[usr.id])
        return None

    elif msg.startswith('/xo'):
        half_games_xo[usr.id] = HalfXOGame(usr.id)
        flag = True
        for i in half_games_xo.keys():
            if not half_games_xo[i].is_ended and not half_games_xo[i].is_started:
                _i = half_games_xo[i]
                _usr = half_games_xo[usr.id]
                if _i.userid != _usr.userid:
                    game = XOGame(_i, _usr)
                    games_xo.append(game)
                    _i.setgame(game)
                    _usr.setgame(game)
                    flag = False
                    _usr.output.output(pipes[usr.id].reply_text, pipes[usr.id].reply_photo, _usr)
                    break

        if flag:
            _usr.output.output(pipes[usr.id].reply_text, pipes[usr.id].reply_photo, _usr)
        return None

    if msg.startswith('/chess'):
        msg = msg.removeprefix('/chess')
        args = msg.split()
        args = list(filter(bool, args))
        try:
            args[0] = ratmin(args[0])
            args[1] = ratmax(args[1])
            args[2] = _time(args[2])
            if args[2] == 0:
                args[2] = _time('inf')
                args[3] = 0
            else:
                args[3] = _add_time(args[3])
            if not args[0] < get_chess_rating(usr.id) < args[1]:
                await update.message.reply_text(
                    'Введите корректные пределы рейтинга! Минимальный должен быть не выше, чем Ваш, а максимальный - не ниже, чем Ваш.')
                return None
        except:
            args = 0 - float('inf'), float('inf'), 10 * 60, 10
        half_games_chess[usr.id] = HalfChessGame(usr.id, get_chess_rating(usr.id), *args, Output())
        flag = True
        for i in half_games_chess.keys():
            _i = half_games_chess[i]
            _usr = half_games_chess[usr.id]
            if diff_is_normal(_i.t_game, _usr.t_game) and diff_is_normal(_i.t_motion, _usr.t_motion) and \
                    _usr.rating_other[0] <= _i.rating <= _usr.rating_other[
                1] and not _i.is_ended and not _i.is_started and _i.userid != _usr.userid:
                game = ChessGame(_i, _usr)
                games_chess.append(game)
                _i.setgame(game)
                _usr.setgame(game)
                flag = False
                _usr.output.output(pipes[usr.id].reply_text, pipes[usr.id].reply_photo, _usr)
                break
        if flag:
            _usr.output.output(pipes[usr.id].reply_text, pipes[usr.id].reply_photo, _usr)
        return None

    if msg.startswith('/weather'):
        try:
            await weather(msg.removeprefix('/weather '), update.message.reply_text, update.message.reply_photo,
                          RETRY_SEND)
        except IndexError:
            await update.message.reply_text('К сожалению, в Яндексе такого города нет')
        except KeyError:
            await update.message.reply_text('К сожалению, в Яндексе такого города нет')


def main():
    logging.basicConfig(filename='main.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    logger = logging.getLogger(__name__)
    create_ai_if_not_exists()
    if not exists('tmp'):
        mkdir('tmp')
    createdb_and_globinit_if_db_not_exists_else_globinit()
    if not user_is_exists(-1):
        add_user(-1)
    application = Application.builder()
    # application.connection_pool_size(1024*1024)
    # application.read_timeout(5)
    # application.write_timeout(2)
    # application.pool_timeout(10000)
    app = application.token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT, handle)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(text_handler)

    app.run_polling()


if __name__ == '__main__':
    worker = Worker()

    pipes = {}

    half_games_chess = {}

    games_chess = []

    games_xoai = {}

    half_games_xo = {}

    games_xo = []
    cleaner_garbage()
    main()
