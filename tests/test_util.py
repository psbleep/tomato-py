import json
import click
import pytest
import sys

from collections import namedtuple
from datetime import datetime, timedelta

from tomato_py import util


def test_load_state_file_exists(runner):
    now = datetime.utcnow()
    with runner.isolated_filesystem():
        with open("test_state.json", "w") as f:
            json.dump({"step_ends": str(now)}, f)
        assert util.load_state(state_file="test_state.json") == {"step_ends": now}


def test_load_state_file_does_not_exist(runner):
    with runner.isolated_filesystem():
        assert util.load_state(state_file="does_not_exist.json") == util.DEFAULT_STATE


ctx_stub = namedtuple("CtxStub", "obj")


def test_save_state_wrapper(runner):
    @util.save_state
    def save_state_consumer(ctx):
        return True

    with runner.isolated_filesystem():
        ctx = ctx_stub(obj={"state_file": "test_state.json", "hello": "world"})
        assert save_state_consumer(ctx) is True
        with open("test_state.json") as f:
            assert json.load(f) == {"state_file": "test_state.json", "hello": "world"}


def test_get_next_step_work_period():
    state = {"work_periods": 0, "short_breaks": 0}
    assert util.get_next_step(state) == util.steps.WORK_PERIOD


def test_get_next_step_short_break():
    state = {"work_periods": 1, "short_breaks": 0}
    assert util.get_next_step(state) == util.steps.SHORT_BREAK


def test_get_next_step_long_break():
    state = {"work_periods": 4, "short_breaks": 3}
    assert util.get_next_step(state) == util.steps.LONG_BREAK


def test_get_next_step_another_step_is_active():
    state = {"active_step": util.steps.WORK_PERIOD}
    assert util.get_next_step(state) == util.steps.WORK_PERIOD


def test_get_status_msg(freezer):
    state = {
        "active_step": util.steps.WORK_PERIOD,
        "step_ends": datetime.utcnow() + timedelta(minutes=5),
        "work_periods": 1,
        "short_breaks": 2,
    }
    assert util.get_status_msg(
        state
    ) == "Pomodoros: 1\nShort Breaks: 2\nRunning: Pomodoro -> {} [{} seconds]".format(
        datetime.utcnow() + timedelta(minutes=5), 300
    )


def test_run_step(freezer):
    state = {}
    assert util.run_step(util.steps.WORK_PERIOD, state=state) == {
        "active_step": util.steps.WORK_PERIOD,
        "step_ends": str(datetime.utcnow() + timedelta(minutes=25)),
    }


def test_run_step_another_step_active():
    state = {"active_step": util.steps.WORK_PERIOD}
    with pytest.raises(click.Abort):
        util.run_step(util.steps.SHORT_BREAK, state)


def test_complete_step_work_period():
    state = {"work_periods": 1}
    assert util.complete_step(util.steps.WORK_PERIOD, state) == {
        "work_periods": 2,
        "active_step": None,
        "step_ends": None,
    }


def test_complete_step_short_break():
    state = {"short_breaks": 1}
    assert util.complete_step(util.steps.SHORT_BREAK, state) == {
        "short_breaks": 2,
        "active_step": None,
        "step_ends": None,
    }


def test_complete_step_long_break():
    state = {"short_breaks": 3, "work_periods": 3}
    assert util.complete_step(util.steps.LONG_BREAK, state) == util.get_default_state()


def test_run_daemon_active_step_not_complete(mocker, freezer):
    subprocess_run = mocker.patch("subprocess.run")
    if sys.platform in ("linux", "linux2"):
        notify = mocker.patch("gi.repository.Notify.Notification.new")
    else:
        notify = mocker.patch("pync.notify")

    state = {
        "active_step": util.steps.WORK_PERIOD,
        "step_ends": datetime.utcnow() + timedelta(seconds=10),
        "work_periods": 0,
    }
    assert util.run_daemon(state) == {
        "active_step": util.steps.WORK_PERIOD,
        "step_ends": datetime.utcnow() + timedelta(seconds=10),
        "work_periods": 0,
    }

    subprocess_run.assert_not_called()
    notify.assert_not_called()


def test_run_daemon_active_step_is_complete(mocker, freezer):
    subprocess_run = mocker.patch("subprocess.run")
    if sys.platform in ("linux", "linux2"):
        notify = mocker.patch("gi.repository.Notify.Notification.new")
    else:
        notify = mocker.patch("pync.notify")


    state = {
        "active_step": util.steps.WORK_PERIOD,
        "step_ends": datetime.utcnow() - timedelta(seconds=10),
        "work_periods": 0,
    }
    assert util.run_daemon(state) == {
        "active_step": None,
        "step_ends": None,
        "work_periods": 1,
    }

    subprocess_run.assert_called()
    notify.assert_called()


def test_run_daemon_no_active_step(mocker):
    subprocess_run = mocker.patch("subprocess.run")
    if sys.platform in ("linux", "linux2"):
        notify = mocker.patch("gi.repository.Notify.Notification.new")
    else:
        notify = mocker.patch("pync.notify")

    state = {"active_step": None}
    assert util.run_daemon(state) == state
    subprocess_run.assert_not_called()
    notify.assert_not_called()
