import os
import sys

if sys.platform == "linux" or sys.platform == "linux2":
    from gi import require_version

    require_version("Notify", "0.7")

    from gi.repository import Notify

    Notify.init("tomato-py")


TOMATO_PY_STATE_FILE = os.environ.get(
    "TOMATO_PY_STATE_FILE",
    os.path.join(os.path.expanduser("~"), ".config/tomato-py/tomato-py.json"),
)

parent = os.path.dirname(TOMATO_PY_STATE_FILE)
if not os.path.exists(parent):
    os.makedirs(parent)


DEFAULT_STATE = {"batch_count": 0, "pomodoro_count": 0}
