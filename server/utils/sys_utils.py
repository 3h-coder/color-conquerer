import sys


def get_kwargs():
    kwargs = {}
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            key, value = arg.split("=")
            kwargs[key] = value

    return kwargs
