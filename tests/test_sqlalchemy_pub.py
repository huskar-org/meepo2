# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
logging.basicConfig(level=logging.DEBUG)

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from meepo.pub import sqlalchemy_pub
from meepo.signals import signal

(t_writes, t_updates, t_deletes) = ([] for _ in range(3))


def _clear():
    del t_writes[:]
    del t_updates[:]
    del t_deletes[:]


def setup_module(module):
    def test_sg(sg_list):
        return lambda pk: sg_list.append(pk)

    # connect table action signal
    signal("test_write").connect(test_sg(t_writes), weak=False)
    signal("test_update").connect(test_sg(t_updates), weak=False)
    signal("test_delete").connect(test_sg(t_deletes), weak=False)


def teardown_module(module):
    pass


def setup_function(function):
    _clear()


def teardown_function(function):
    pass


@pytest.fixture(scope="module")
def model_cls():
    Base = declarative_base()

    class model_cls(Base):
        __tablename__ = "test"
        id = sa.Column(sa.Integer, primary_key=True)
        data = sa.Column(sa.String)
    return model_cls


@pytest.fixture(scope="module")
def session(mysql_dsn):
    # sqlalchemy prepare
    engine = sa.create_engine(mysql_dsn)
    session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

    # install sqlalchemy_pub hook
    sqlalchemy_pub(session)
    return session


def test_sa_empty_commit(session):
    """Direct commit generates nothing
    """
    session.commit()

    assert [t_writes, t_updates, t_deletes] == [[]] * 3


def test_sa_single_write(session, model_cls):
    """Write commit generate a write event with row pk.
    """
    t_a = model_cls(data='a')
    session.add(t_a)
    session.commit()

    assert t_writes == [t_a.id]
    assert [t_updates, t_deletes] == [[]] * 2


def test_sa_single_flush_write(session, model_cls):
    """Flush - Write is the same with write.
    """
    t_b = model_cls(data='b')
    session.add(t_b)
    session.flush()
    session.commit()

    assert t_writes == [t_b.id]
    assert [t_updates, t_deletes] == [[]] * 2


def test_sa_multi_writes(session, model_cls):
    # test multiple writes
    t_c = model_cls(data='c')
    t_d = model_cls(data='d')
    session.add(t_c)
    session.add(t_d)
    session.commit()

    assert set(t_writes) == {t_c.id, t_d.id}
    assert [t_updates, t_deletes] == [[]] * 2


def test_sa_single_update(session, model_cls):
    # test single update
    t_a = session.query(model_cls).filter(model_cls.data == 'a').one()
    t_a.data = "aa"
    session.commit()

    assert set(t_updates) == {t_a.id}
    assert [t_writes, t_deletes] == [[]] * 2


def test_sa_single_flush_update(session, model_cls):
    # test single flush - update
    t_a = session.query(model_cls).filter(model_cls.data == 'aa').one()
    t_a.data = "a"
    session.flush()
    session.commit()

    assert set(t_updates) == {t_a.id}
    assert [t_writes, t_deletes] == [[]] * 2


def test_sa_mixed_write_update_delete_and_multi_flushes(session, model_cls):
    """The most compliated situation, the test goes through the following
    process:
    1. add one row, update one row
    2. flush to database
    3. delete one row
    4. flush to database
    5. commit
    """
    t_b, t_c = session.query(model_cls).\
        filter(model_cls.data.in_(('b', 'c'))).all()
    t_e = model_cls(data='e')
    session.add(t_e)
    t_b.data = "x"
    session.flush()
    session.delete(t_c)
    session.flush()
    session.commit()

    assert (t_writes, t_updates, t_deletes) == ([t_e.id], [t_b.id], [t_c.id])


def test_sa_empty_rollback(session):
    """Direct rollback generates nothing
    """
    session.rollback()

    assert [t_writes, t_updates, t_deletes] == [[]] * 3


def test_sa_early_rollback(session, model_cls):
    """Rollback happened before flush, nothing recorded.
    """
    t_e = model_cls(data='e')
    session.add(t_e)
    session.rollback()

    assert [t_writes, t_updates, t_deletes] == [[]] * 3


def test_sa_flush_rollback(session, model_cls):
    """Rollback happened after flush, event recorded.
    Since rollback happened after flush, the write have a pk value.
    """
    t_e = model_cls(data='e')
    session.add(t_e)
    session.flush()
    session.rollback()

    assert [t_writes, t_updates, t_deletes] == [[]] * 3


def test_sa_session_remove(session, model_cls):
    session.remove()
    t_f = model_cls(data='f')
    session.add(t_f)
    session.commit()

    assert t_writes == [t_f.id]
