import heinz_bot
import pydevd_pycharm


if __name__ == '__main__':
    pydevd_pycharm.settrace('localhost', port=1234, stdoutToServer = True, stderrToServer = True)
    heinz_bot.main()