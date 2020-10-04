import os


TOMATO_PY_STATE_FILE = os.environ.get(
    "TOMATO_PY_STATE_FILE",
    os.path.join(os.path.expanduser("~"), "./.config/tomato-py/tomato-py.json"),
)

parent = os.path.dirname(TOMATO_PY_STATE_FILE)
if not os.path.exists(parent):
    os.makedirs(parent)


DEFAULT_STATE = {"batch_count": 0, "pomodoro_count": 0}
