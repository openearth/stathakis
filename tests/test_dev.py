#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `stathakis` package."""

import logging

import pytest
import requests

logger = logging.getLogger(__name__)
logging.basicConfig()


def get_base_url():
    """return the base url"""
    try:
        import boto3
    except ImportError:
        logging.exception("could not find boto3, using local server for testing")
        return "http://0.0.0.0:8080"
    # if we have boto, find the instance
    client = boto3.client('elasticbeanstalk')
    resp = client.describe_environments(EnvironmentNames=['stathakis-dev'])
    environments = resp['Environments']
    assert len(environments) == 1, "we should have 1 stathakis-dev environment"
    environment = environments[0]
    cname = environment['CNAME']
    return 'http://' + cname


BASE_URL = get_base_url()

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    logger.warn("requesting %s", BASE_URL)
    return requests.get(BASE_URL)

@pytest.fixture
def grid_response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """

    url = BASE_URL + '/stathakis/1.0.0/grids/ncep/measurements/wind?lat=52&lon=4&start_time=2017-01-01&end_time=2017-03-03'
    logger.warn("requesting %s", url)
    return requests.get(url)


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""

    assert 'status' in response.json()

def test_grid_response(grid_response):
    """Sample pytest test function with the pytest fixture as an argument."""

    assert 'series' in grid_response.json(), 'expected series'
