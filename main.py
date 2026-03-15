import sys
import os

# ==========================================
# 拦截 1：--internal-cli 哨兵（GUI 手动调用）
# ==========================================
if len(sys.argv) > 1 and sys.argv[1] == '--internal-cli':
    sys.argv = sys.argv[2:]

    import builtins
    builtins.input = lambda prompt="": ""

    os.environ["CI"] = "1"
    os.environ["TERM"] = "dumb"
    os.environ["NO_COLOR"] = "1"
    if hasattr(sys.stdout, 'isatty'): sys.stdout.isatty = lambda: False
    if hasattr(sys.stdin, 'isatty'): sys.stdin.isatty = lambda: False

    if sys.platform == "win32":
        try:
            import msvcrt
            msvcrt.getch = lambda: b'\r'
            msvcrt.getwch = lambda: '\r'
            msvcrt.kbhit = lambda: False
        except ImportError:
            pass

    try:
        import click
        click.pause = lambda *args, **kwargs: None
        click.confirm = lambda *args, **kwargs: True
        click.prompt = lambda *args, **kwargs: kwargs.get("default", "")
        import click.termui
        click.termui.getchar = lambda *args, **kwargs: '\r'
    except ImportError:
        pass

    try:
        import questionary
        def _fake_select(*args, **kwargs):
            class FakeResult:
                def ask(self, *a, **kw):
                    choices = kwargs.get('choices', [])
                    default = kwargs.get('default')
                    if default is not None:
                        return getattr(default, 'value', default)
                    if choices:
                        first = choices[0]
                        return getattr(first, 'value', first)
                    return None
            return FakeResult()
        questionary.select = _fake_select
        questionary.confirm = lambda *args, **kwargs: type('R', (), {'ask': lambda self: kwargs.get('default', True)})()
        questionary.text = lambda *args, **kwargs: type('R', (), {'ask': lambda self: kwargs.get('default', '')})()
        questionary.checkbox = lambda *args, **kwargs: type('R', (), {'ask': lambda self: []})()
    except ImportError:
        pass

    try:
        from copaw.cli.main import cli
        cli()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"执行 copaw 发生异常: {e}")
        sys.exit(1)

    sys.exit(0)

# ==========================================
# 拦截 2：copaw desktop 内部子进程调用
# desktop_cmd.py 会执行: sys.executable -m copaw app --host X --port Y
# uvicorn 用字符串 "copaw.app._app:app" 在 PyInstaller 下加载会失败
# 此处直接导入 app 对象绕过字符串加载
# ==========================================
if len(sys.argv) >= 3 and sys.argv[1] == '-m' and sys.argv[2] == 'copaw':
    sys.argv = [sys.argv[0]] + sys.argv[3:]

    import argparse
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('command', nargs='?', default='app')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8088)
    p.add_argument('--log-level', default='info')
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--reload', action='store_true')
    known, _ = p.parse_known_args(sys.argv[1:])

    try:
        import uvicorn
        from copaw.app._app import app
        from copaw.config.utils import write_last_api
        from copaw.utils.logging import setup_logger
        from copaw.constant import LOG_LEVEL_ENV

        write_last_api(known.host, known.port)
        os.environ[LOG_LEVEL_ENV] = known.log_level
        setup_logger(known.log_level)

        uvicorn.run(
            app,
            host=known.host,
            port=known.port,
            reload=False,
            workers=1,
            log_level=known.log_level,
        )
    except Exception as e:
        print(f"启动 app server 发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)

# ==========================================
# 图形界面部分 (PySide6)
# ==========================================
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtCore import QProcess, QProcessEnvironment

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("一键启动环境")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        layout.addWidget(self.log_output)

        self.start_btn = QPushButton("一键初始化并启动")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self.start_execution)
        layout.addWidget(self.start_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.process = QProcess(self)

        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(env)

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        self.current_step = 0

    def append_log(self, text):
        self.log_output.append(text)
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_execution(self):
        self.start_btn.setEnabled(False)
        self.log_output.clear()
        self.current_step = 1
        self.append_log(">>> 开始执行: copaw init --defaults --accept-security\n" + "-"*40)
        self.run_internal_command(["init", "--defaults", "--accept-security"])

    def run_internal_command(self, args):
        exe = sys.executable
        full_args = ["--internal-cli", "copaw"] + args
        self.process.start(exe, full_args)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        if data.strip():
            self.append_log(data.strip())

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        if data.strip():
            self.append_log(data.strip())

    def process_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.append_log(f"\n[!] 进程异常退出 (错误码: {exitCode})，请检查上方日志。")
            self.start_btn.setEnabled(True)
            self.current_step = 0
            return

        if self.current_step == 1:
            self.append_log("\n>>> 初始化完成！")
            self.current_step = 2
            self.append_log(">>> 开始执行: copaw desktop\n" + "-"*40)
            self.run_internal_command(["desktop"])

        elif self.current_step == 2:
            self.append_log("\n>>> 所有任务执行完毕！")
            self.start_btn.setEnabled(True)
            self.current_step = 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())