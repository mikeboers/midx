"""midx is a mini file sequence index.

See: `midx <command> --help` for more on individual commands.

"""

import argparse
import os
import pkg_resources


def argument(*args, **kwargs):
    return args, kwargs

def group(title, *args):
    return title, args

def command(*args, **kwargs):
    def _decorator(func):
        func.__aque_command__ = (args, kwargs)
        return func
    return _decorator


def main(argv=None):

    parser = argparse.ArgumentParser(
        prog='midx',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    subparsers = parser.add_subparsers(metavar='COMMAND')

    funcs = [ep.load() for ep in pkg_resources.iter_entry_points('midx_commands')]
    funcs.sort(key=lambda f: f.__aque_command__[1].get('name', f.__name__))

    for func in funcs:
        args, kwargs = func.__aque_command__
        name = kwargs.pop('name', func.__name__)
        kwargs.setdefault('formatter_class', argparse.RawDescriptionHelpFormatter)
        subparser = subparsers.add_parser(name, **kwargs)
        subparser.set_defaults(func=func)

        for arg_args, arg_kwargs in args:
            if isinstance(arg_args, basestring):
                group = subparser.add_argument_group(arg_args)
                for arg_args, arg_kwargs in arg_kwargs:
                    group.add_argument(*arg_args, **arg_kwargs)
            else:
                subparser.add_argument(*arg_args, **arg_kwargs)

    args = parser.parse_args(argv)
    if not args.func:
        parser.print_usage()
        exit(1)
    
    res = args.func(args) or 0

    if __name__ == '__main__':
        exit(res)
    else:
        return res


