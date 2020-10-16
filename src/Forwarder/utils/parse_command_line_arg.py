""" This class handle parse argument from command line """

import argparse


def parse_command_line_args():
    parser = argparse.ArgumentParser(description=(
        'Argument friday-controller'))

    parser.add_argument(
        '--host_1',
        default='localhost',
        help='Host name Raspberry Server')

    parser.add_argument(
        '--port_1',
        type=int,
        default=1883,
        help='Port raspberry server')

    parser.add_argument(
        '--host_2',
        default='192.168.1.114',  # ip ForwarderServer
        help='Host name Raspberry forwarder')

    parser.add_argument(
        '--port_2',
        type=int,
        default=1883,
        help='Port raspberry forwarder')

    return parser.parse_args()


__all__ = ['parse_command_line_args']
