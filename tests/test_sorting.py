from datetime import datetime

import pytest

from flask_query_builder.exceptions import InvalidSortException
from flask_query_builder.querying import QueryBuilder, AllowedSort
from flask_query_builder.sorts import Sort


def test_assert_exception_raised_when_sort_not_allowed(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with pytest.raises(InvalidSortException):
        with request_context("/?sort=last_name"):
            users = QueryBuilder(models.User).allowed_sorts([
                AllowedSort.field("random_field"),
            ]) \
                .query \
                .all()


def test_ascending_sort_applied_to_query(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    users = models.User.query.all()
    assert users[0].first_name == user1.first_name
    assert users[1].first_name == user2.first_name
    assert users[2].first_name == user3.first_name

    with request_context("/?sort=first_name"):
        users = QueryBuilder(models.User).allowed_sorts([
            AllowedSort.field("first_name"),
        ]) \
            .query \
            .all()

        assert users[0].first_name == "Ann"
        assert users[1].first_name == "Charlie"
        assert users[2].first_name == "Frank"


def test_descending_sort_applied_to_query(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?sort=-first_name"):
        users = QueryBuilder(models.User).allowed_sorts([
            AllowedSort.field("first_name"),
        ]) \
            .query \
            .all()

        assert users[0].first_name == "Frank"
        assert users[1].first_name == "Charlie"
        assert users[2].first_name == "Ann"


def test_multiple_sorts_applied_to_query(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Ann', last_name='B', username='annb', birth_date=birth_date)
    user2 = models.User(first_name='Ann', last_name='A', username='anna', birth_date=birth_date)
    user3 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?sort=first_name,last_name"):
        users = QueryBuilder(models.User).allowed_sorts([
            AllowedSort.field("first_name"),
            AllowedSort.field("last_name"),
        ]) \
            .query \
            .all()

        assert users[0].first_name == "Ann"
        assert users[0].last_name == "A"
        assert users[1].first_name == "Ann"
        assert users[1].last_name == "B"
        assert users[2].first_name == "Frank"
        assert users[2].last_name == "Elliot"


def test_different_query_name_used_to_field(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?sort=name"):
        users = QueryBuilder(models.User).allowed_sorts([
            AllowedSort.field("name", "first_name"),
        ]) \
            .query \
            .all()

        assert users[0].first_name == "Ann"
        assert users[1].first_name == "Charlie"
        assert users[2].first_name == "Frank"


def test_string_allowed_sort_converted_to_field_sort(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    users = models.User.query.all()
    assert users[0].first_name == user1.first_name
    assert users[1].first_name == user2.first_name
    assert users[2].first_name == user3.first_name

    with request_context("/?sort=first_name"):
        users = QueryBuilder(models.User).allowed_sorts([
            "first_name",
        ]) \
            .query \
            .all()

        assert users[0].first_name == "Ann"
        assert users[1].first_name == "Charlie"
        assert users[2].first_name == "Frank"


def test_custom_sort(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    address1 = models.Address(road="X road")
    address2 = models.Address(road="A road")
    address3 = models.Address(road="D road")
    user1 = models.User(
        first_name='Frank',
        last_name='Elliot',
        username='frank',
        birth_date=birth_date,
        address=address1
    )
    user2 = models.User(
        first_name='Charlie',
        last_name='Joe',
        username='charlie',
        birth_date=birth_date,
        address=address2
    )
    user3 = models.User(
        first_name='Ann',
        last_name='Smith',
        username='ann',
        birth_date=birth_date,
        address=address3
    )

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    users = models.User.query.all()
    assert users[0].first_name == user1.first_name
    assert users[1].first_name == user2.first_name
    assert users[2].first_name == user3.first_name

    class AddressSort(Sort):
        def sort(self, query, model, sort_name, descending):
            if descending:
                return query.order_by(models.Address.road.desc())
            return query.order_by(models.Address.road)

    with request_context("/?sort=address"):
        users = QueryBuilder(models.User).allowed_sorts([
            AllowedSort.custom("address", AddressSort()),
        ]) \
            .query \
            .join(models.User.address) \
            .all()

        assert users[0].first_name == "Charlie"
        assert users[0].address.road == "A road"
        assert users[1].first_name == "Ann"
        assert users[1].address.road == "D road"
        assert users[2].first_name == "Frank"
        assert users[2].address.road == "X road"
