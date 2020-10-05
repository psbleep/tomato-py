import time

import click

from copy import copy

from tomato_py import TOMATO_PY_STATE_FILE

from tomato_py import messages
from tomato_py import util


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = util.load_state(state_file=TOMATO_PY_STATE_FILE)


@cli.command()
@click.pass_context
def status(ctx):
    status_msg = util.get_status_msg(ctx.obj)
    click.echo(status_msg)


@cli.command()
@click.pass_context
@util.save_state
def next(ctx):
    next_step = util.get_next_step(ctx.obj)
    util.run_step(next_step, state=ctx.obj)
    click.echo(messages.run_step(next_step))


@util.save_state
@cli.command()
@click.pass_context
def skip(ctx):
    next_step = util.get_next_step(ctx.obj)
    util.skip_step(next_step, state=ctx.obj)
    click.echo(messages.skip_step(next_step))


@util.save_state
@cli.command()
@click.pass_context
def reset(ctx):
    ctx.obj = util.get_default_state()
    click.echo("Resetting tomato-py state.")


@cli.command()
def daemon():
    while True:
        time.sleep(5)
        orig_state = util.load_state(state_file=TOMATO_PY_STATE_FILE)
        state = util.run_daemon(copy(orig_state))
        if state != orig_state:
            util.save_state_file(state)


if __name__ == "__main__":
    cli()
