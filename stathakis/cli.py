# -*- coding: utf-8 -*-

"""Console script for stathakis."""
import logging

import click

from .app import make_app


@click.command()
@click.option(
    '--debug/--no-debug',
    default=False,
    help='Start application in debugger mode.'
)
def main(debug, args=None):
    """Console script for stathakis."""
    # configure logging
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    app = make_app()
    app.run(debug=debug, port=8080)


if __name__ == "__main__":
    main()
