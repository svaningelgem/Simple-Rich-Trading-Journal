try:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent))
except Exception:
    raise

import contextlib
from atexit import register, unregister
from multiprocessing import Process, util
from subprocess import Popen
from time import sleep

import __ini__.cmdl
import __ini__.logtags
from config import config
from dash import Dash

__project_name__ = "Simple Rich Trading Journal"


def run() -> None:
    if __ini__.cmdl.ADMINISTRATIVE:
        config.init_config()  # Initialize config early
    else:
        red = [sys.executable, __file__, *sys.argv[1:]]
        red = Popen(
            red,
            stdin=sys.stdin,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        if not __ini__.cmdl.FLAGS.detach:
            while red.returncode is None:
                try:
                    red.communicate()
                except KeyboardInterrupt:
                    break
        else:
            pass


class Server(Process):
    def run(self) -> None:
        import __env__
        import layout

        __env__.server_manager.server_proc = self

        app = Dash(
            __project_name__,
            title=__env__.profile_manager.profile_name or __project_name__,
            update_title="working...",
            assets_folder=__env__.paths.dash_assets,
            assets_url_path=__env__._files.folder_profile_assets,
        )
        app.layout = layout.LAYOUT
        app._favicon = ".favicon.ico"
        try:
            pass
        except Exception:
            raise

        if __ini__.cmdl.FLAGS.quiet:

            class null:
                @staticmethod
                def write(*_) -> None:
                    return

                flush = write

            sys.stderr = null

        app.run(debug=__ini__.cmdl.FLAGS.debug, host=config.app.host, port=config.app.port)


def _suppress_exc(*args, **kwargs) -> None:
    with contextlib.suppress(KeyboardInterrupt):
        util._exit_function(*args, **kwargs)


if __name__ == "__main__":
    import __env__

    if ping := __env__.server_manager.ping():
        pass
    else:
        server_proc = Server(name="srtj-server")
        server_proc.start()

        # suppress exception ##############################################################################

        unregister(util._exit_function)
        register(_suppress_exc)

        ###################################################################################################

        # wait for server #################################################################################

        __env__.ui_utils.write_pong_file(server_proc.pid)

        for _i in range(1, 21):
            if __env__.server_manager.ping():
                break
            sleep(0.1)
        else:
            pass

        ###################################################################################################

    __env__.startup.call_gui()
