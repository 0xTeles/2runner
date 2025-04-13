import argparse
import os

from tworunner import __version__
from tworunner.main import runner


def main():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '--version', action='version', version=__version__, help='Show version'
    )
    parser.add_argument(
        '--tokens', type=str, required=True,
        default='tokens.txt', help='File with all tokens'
    )
    parser.add_argument(
        '--hosts', type=str, required=True,
        default='hosts.txt', help='File with all hosts'
    )
    parser.add_argument(
        '--workflow', type=str, required=True,
        default='workflow.yml', help='File with workflow'
    )

    args = parser.parse_args()

    if not os.path.exists(args.tokens) or not os.path.exists(args.hosts) or \
        not os.path.exists(args.workflow):
        print(f'[X] {args.tokens}, {args.hosts} or {args.workflow} not found!!')
        return

    tokens = open(args.tokens, encoding='utf-8').read().split('\n')
    hosts = open(args.hosts, encoding='utf-8').read()
    workflow = open(args.workflow, encoding='utf-8').read()
    runner(tokens, hosts, workflow)


if __name__ == '__main__':
    main()
