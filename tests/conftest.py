# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
logging.basicConfig(level=logging.DEBUG)

import json
import os
import uuid

import pymysql
import pytest
import redis

from meepo2._compat import urlparse


@pytest.fixture(scope="session")
def conf():
    """Try load local conf.json
    """
    fname = os.path.join(os.path.dirname(__file__), "conf.json")
    if os.path.exists(fname):
        with open(fname) as f:
            return json.load(f)


@pytest.fixture(scope="session")
def redis_dsn(request, conf):
    """Redis server dsn
    """
    redis_dsn = conf["redis_dsn"] if conf else "redis://localhost:6379/1"

    def fin():
        r = redis.Redis.from_url(redis_dsn, socket_timeout=1)
        r.flushdb()
    request.addfinalizer(fin)
    return redis_dsn


@pytest.fixture(scope="module")
def mysql_dsn(conf):
    """MySQL server dsn

    This fixture will init a clean meepo2_test database with a 'test' table
    """
    logger = logging.getLogger("fixture_mysql_dsn")

    dsn = conf["mysql_dsn"] if conf else \
        "mysql+pymysql://root@localhost/meepo2_test"

    # init database
    parsed = urlparse(dsn)
    db_settings = {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "passwd": parsed.password
    }
    conn = pymysql.connect(**db_settings)
    cursor = conn.cursor()

    conn.begin()
    cursor.execute("DROP DATABASE IF EXISTS meepo2_test")
    cursor.execute("CREATE DATABASE meepo2_test")
    cursor.execute("DROP TABLE IF EXISTS meepo2_test.test")
    cursor.execute('''CREATE TABLE meepo2_test.test (
                        id INT NOT NULL AUTO_INCREMENT,
                        data VARCHAR (256) NOT NULL,
                        PRIMARY KEY (id)
                   )''')
    cursor.execute("RESET MASTER")
    conn.commit()

    logger.debug("executed")

    # release conn
    cursor.close()
    conn.close()

    return dsn


@pytest.fixture(scope="function")
def mock_session():
    class MockSession(object):
        def __init__(self):
            self.meepo2_unique_id = uuid.uuid4().hex
            self.info = {"name": "mock{}".format(self.meepo2_unique_id)}
    return MockSession()
