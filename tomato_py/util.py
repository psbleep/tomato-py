import functools
import json
import os
import subprocess
import sys

import click

from copy import deepcopy
from datetime import datetime, timedelta
from types import SimpleNamespace


from tomato_py import TOMATO_PY_STATE_FILE


steps = SimpleNamespace(
    WORK_PERIOD="Pomodoro", SHORT_BREAK="Short break", LONG_BREAK="Long break"
)


DEFAULT_STATE = {
    "active_step": None,
    "step_ends": None,
    "work_periods": 0,
    "short_breaks": 0,
    "state_file": TOMATO_PY_STATE_FILE,
}

INTERVALS = {
    steps.WORK_PERIOD: timedelta(minutes=25),
    steps.SHORT_BREAK: timedelta(minutes=5),
    steps.LONG_BREAK: timedelta(minutes=25),
}


def save_state(func):
    @functools.wraps(func)
    def save_state_inner(ctx, *args, **kwargs):
        resp = func(ctx, *args, **kwargs)
        save_state_file(ctx.obj)
        return resp

    return save_state_inner


def save_state_file(state):
    with open(state["state_file"], "w") as f:
        json.dump(state, f)


def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file) as f:
            state = json.load(f)
        if state["step_ends"]:
            state["step_ends"] = datetime.strptime(
                state["step_ends"], "%Y-%m-%d %H:%M:%S.%f"
            )
        return state
    return get_default_state()


def get_default_state():
    return deepcopy(DEFAULT_STATE)


def get_status_msg(state):
    next_step = get_next_step(state)
    active_step_exists = state.get("active_step") is not None

    msg = "Pomodoros: {}\nShort Breaks: {}\n".format(
        state["work_periods"], state["short_breaks"]
    )

    if active_step_exists:
        delay = int((state["step_ends"] - datetime.utcnow()).total_seconds())
        msg += "Running: {} -> {} [{} seconds]".format(
            next_step, state["step_ends"], delay
        )
    else:
        msg += "Next: {}".format(next_step)

    return msg


def get_next_step(state):
    active_step = state.get("active_step")
    if active_step:
        return active_step
    if state["work_periods"] > state["short_breaks"]:
        if state["short_breaks"] >= 3:
            return steps.LONG_BREAK
        return steps.SHORT_BREAK
    return steps.WORK_PERIOD


def run_step(step, state):
    if state.get("active_step") is not None:
        raise click.Abort("Step already running: " + state["active_step"])
    state["active_step"] = step
    state["step_ends"] = str(datetime.utcnow() + INTERVALS[step])
    return state


def complete_step(step, state):
    if step == steps.LONG_BREAK:
        return get_default_state()

    state["active_step"] = None
    state["step_ends"] = None

    if step == steps.WORK_PERIOD:
        state["work_periods"] += 1
    elif step == steps.SHORT_BREAK:
        state["short_breaks"] += 1
    return state


def run_daemon(state):
    if not state["active_step"]:
        return state
    delay = (state["step_ends"] - datetime.utcnow()).total_seconds()
    if delay > 0:
        return state
    subprocess.run(
        ["mpv", os.path.join(os.path.dirname(__file__), "alert.mp3")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    notification_msg = "{} completed".format(state["active_step"])
    if sys.platform in ("linux", "linux2"):
        from gi.repository import Notify
        Notify.Notification.new(notification_msg).show()
    else:
        import pync
        pync.notify(notification_msg)
    return complete_step(state["active_step"], state)
