existing_active_step_error = ("",)


def run_step(s):
    return "Running: {}.".format(s)


def skip_step(s):
    return "Skipping: {}.".format(s)
