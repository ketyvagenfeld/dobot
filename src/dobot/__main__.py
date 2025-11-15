"""Entry-point module, in case you use `python -m dobot`.

Why does this file exist, and why `__main__`? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

from concurrent.futures import (
    wait,
    ALL_COMPLETED,
    ProcessPoolExecutor,
)

from dobot import robot, controller


def main():
    with ProcessPoolExecutor() as executor:
        robot_future = executor.submit(robot.main)
        controller_future = executor.submit(controller.main)

    _ = wait(*[robot_future, controller_future], return_when=ALL_COMPLETED)


if __name__ == "__main__":
    import sys

    sys.exit(main())
