===================
Meepo2 Documentation
===================

Welcome to meepo2's documentation. Meepo2 is a event sourcing and broadcasting
platform for database.

This documentation consists of two parts:

1. Meepo2 PubSub (`meepo2.pub` & `meepo2.sub`). This part is enough if you
   only needs a simple solution for your database events.

2. Meepo2 Apps (`meepo2.apps`). This part ships with eventsourcing and
   replicator apps for advanced use. You can refer to examples for demo.

Meepo2 source code is hosted on Github: https://github.com/huskar-org/meepo2

.. contents::
   :local:
   :depth: 2
   :backlinks: none


Features
========

Meepo2 can be used to do lots of things, including replication, eventsourcing,
cache refresh/invalidate, real-time analytics etc. The limit is all the tasks
should be row-based, since meepo2 only gives ``table_action`` -> ``pk``
style events.

* Row-based database replication.

  Meepo2 can be used to replicate data between databases including
  postgres, sqlite, etc.

  Refer to ``examples/repl_db`` script for demo.

* Replicate RDBMS to NoSQL and search engine.

  Meepo2 can also be used to replicate data changes from RDBMS to redis,
  elasticsearch etc.

  Refer to ``examples/repl_redis`` and ``examples/repl_elasticsearch`` for
  demo.

* Event Sourcing.

  Meepo2 can log and replay what has happened since some time using a simple
  event sourcing.

  Refer to ``examples/event_sourcing`` for demo.

.. note::

   Meepo2 can only replicate row based data, which means it DO NOT replicate
   schema changes, or bulk operations.


Installation
============

.. highlight:: bash

:Requirements: **Python 2.x >= 2.7** or **Python 3.x >= 3.2** or **PyPy**

To install the latest released version of Meepo2::

    $ pip install meepo2


Usage
=====

Meepo2 use blinker signal to hook into the events of mysql binlog and
sqlalchemy, the hook is very easy to install.

Hook with MySQL's binlog events:

.. code:: python

    from meepo2.pub import mysql_pub
    mysql_pub(mysql_dsn)

Hook with SQLAlchemy's events:

.. code:: python

    from meepo2.pub import sqlalchemy_pub
    sqlalchemy_pub(session)

Then you can connect to the signal and do tasks based the signal:

.. code:: python

    sg = signal("test_write")

    @sg.connect
    def print_test_write(pk)
        print("test_write -> %s" % pk)

Try out the demo scripts in ``example/tutorial`` for more about how meepo2
event works.


Pub Concept
===========

.. automodule:: meepo2.pub


MySQL Pub
---------

.. automodule:: meepo2.pub.mysql
    :members:

SQLAlchemy Pub
--------------

.. automodule:: meepo2.pub.sqlalchemy
    :members:

Meepo2 Sub
=========

.. automodule:: meepo2.sub

Dummy Sub
---------

.. automodule:: meepo2.sub.dummy
    :members:

0MQ Sub
-------

.. automodule:: meepo2.sub.zmq
    :members:


Applications
============

EventSourcing
-------------

Concept
~~~~~~~

.. automodule:: meepo2.apps.eventsourcing

Pub & Sub
`````````

.. automodule:: meepo2.apps.eventsourcing.pub
    :members:

.. automodule:: meepo2.apps.eventsourcing.sub
    :members:

EventStore
~~~~~~~~~~

.. automodule:: meepo2.apps.eventsourcing.event_store

    .. autoclass:: meepo2.apps.eventsourcing.event_store.RedisEventStore
        :members:

PrepareCommit
~~~~~~~~~~~~~

.. automodule:: meepo2.apps.eventsourcing.prepare_commit

    .. autoclass:: meepo2.apps.eventsourcing.prepare_commit.RedisPrepareCommit
        :members:

Replicator
----------

.. automodule:: meepo2.apps.replicator
    :members:
