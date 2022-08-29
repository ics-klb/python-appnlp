"""
BotNlp.xtensor - model for training with tensorflow modules.
Обучение бота на основе нейросетевой модели CRNN.
"""

import sys
import os
import signal
import platform

from . import worker as botworker

def common_train():
    ''' Обучение модели xnlp. '''

    from .nlu.adapters import testgendim
    xbase_dataset = ''
    testgendim()

def common_service():
    ''' Тестовый запуск сервиса с прослушиванием сокета. '''

    try:
        bot = botworker.Worker()
        bot.start_daemon()
    except Exception as ex:
        # Just print(e) is cleaner and more likely what you want,
        # but if you insist on printing message specifically whenever possible...
        if hasattr(ex, 'message'):
            print(ex.message)
        else:
            print(ex)

    return bot


def common_predict(recognition=False, synthesis=False):
    ''' Работа с обученной моделью nlp. '''

    question = ''
    while(True):
        question = input('Вы: ')

def common_test():
    pass


def on_start():
    import curses
    curses.setupterm()
    if len(sys.argv) > 1:
        if '--start' in sys.argv:
            common_train()
        elif '--service' in sys.argv:
            common_service()
        elif '--predict' in sys.argv:
            common_predict()
        elif '--help' in sys.argv:
            print('Поддерживаемые варианты работы:')
            print('\t--start - обучение модели')
            print('\t--test - тестирование базовых элементов')
        else:
            print('[i] Выберите вариант работы бота:')
            print('\t1. start - обучение модели')
            print('\t2. predict')
            print('\t3. worker')
            print('\t4. test - тестирование базовых элементов')

            while True:
                choice = input('\rВаш выбор: ')
                if choice == '1':
                    common_train()
                elif choice == '2':
                    common_predict()
                elif choice == '3':
                    common_service()
                elif choice == '4':

                    common_test()
                else:
                    os.write(sys.stdout.fileno(), curses.tigetstr('cuu1'))
                    print('                                     ', end='')
    else:
        print("[E] Неверный аргумент командной строки. Введите --help для помощи.")
        print()
        sys.exit(0)

def on_stop(*args):
    print('\n[i] Бот остановлен')
    sys.exit(0)


if __name__ == '__main__':
    # При нажатии комбинаций Ctrl+Z, Ctrl+C либо закрытии терминала будет вызываться функция on_stop()
    # (Работает только на linux системах!)
    if platform.system() == 'Linux':
        for sig in (signal.SIGTSTP, signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, on_stop)
    # on_start()
