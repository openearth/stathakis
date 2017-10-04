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
    logger.warn("requesting", BASE_URL)
    return requests.get(BASE_URL)


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""

    assert 'status' in response.json()
