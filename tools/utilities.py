#!/usr/bin/python3

import sys

sys.path.append("../dbus")
import fanatec_input


def turn_off_light():
    """The fanatec_input module provides the CSLP1V2Wheel class for controlling
    the RevStripe™© on equipped models. This function is a quick hack to turn
    the stripe off without modifying the driver itself."""

    wheel = fanatec_input.CSLP1V2Wheel()

    wheel.set_sysfs_rpm(99)
    wheel.set_sysfs_rpm(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Random utilities for Fanatec wheels"
    )
    parser.add_argument(
        '-l', '--turn_off_light',
        action='store_true',
        help="Attempt to disable RevStripe for, e.g., CSL WRC wheel so it's \
        not shining in your face.")
    args = parser.parse_args()

    if args.turn_off_light:
        turn_off_light()
    else:
        parser.print_help()
