# -*- coding: utf-8 -*-

"""Console script for stathakis."""
import logging

import click

from .app import make_app

logger = logging.getLogger(__name__)

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
    # load configuration (connexxion app contains flask app)
    app.app.config.from_object('stathakis.config')
    configured = app.app.config.from_envvar('STATHAKIS_SETTINGS', silent=True)
    if not configured:
        logger.debug("configuration file not found. Use STATHAKIS_SETTINGS to point to config file.")
    app.run(debug=debug, port=8080)


if __name__ == "__main__":
    main()
