from datetime import datetime

import pytest
from sqlalchemy import extract

from flask_query_builder.exceptions import InvalidFilterException
from flask_query_builder.filters import Filter
from flask_query_builder.querying import QueryBuilder, AllowedFilter

def test_assert_no_exception_raised_when_sort_not_allowed_and_raise_exceptions_is_disabled(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[first_name]=john"):
        users = QueryBuilder(models.User, raise_exceptions=False).allowed_filters([
            AllowedFilter.exact("random_field"),
        ]) \
            .query \
            .all()

        assert len(users) == 3


def test_assert_exception_raised_when_sort_not_allowed(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with pytest.raises(InvalidFilterException):
        with request_context("/?filter[first_name]=john"):
            users = QueryBuilder(models.User).allowed_filters([
                AllowedFilter.exact("random_field"),
            ]) \
                .query \
                .all()


def test_exact_filter_applied_to_query(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[first_name]=Ann"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            AllowedFilter.exact("first_name")
        ]) \
            .query \
            .all()

        assert len(users) == 1
        assert users[0].first_name == "Ann"


def test_multiple_values_requested_and_applied(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[first_name]=Ann,Charlie"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            AllowedFilter.exact("first_name")
        ]) \
            .query \
            .all()

        assert len(users) == 2


def test_partial_filter_applied_to_query(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Frodo', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[first_name]=fr"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            AllowedFilter.partial("first_name")
        ]) \
            .query \
            .all()

        assert len(users) == 2
        assert users[0].first_name == "Frank"
        assert users[1].first_name == "Frodo"


def test_filter_name_matches_different_internal_column_name(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(first_name='Frank', last_name='Elliot', username='frank', birth_date=birth_date)
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[name]=Ann"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            AllowedFilter.exact("name", "first_name")
        ]) \
            .query \
            .all()

        assert len(users) == 1
        assert users[0].first_name == "Ann"


def test_string_allowed_filter_converted_to_exact_filter(db_session, request_context, models):
    birth_date = datetime.strptime("1970-01-01", "%Y-%m-%d")
    user1 = models.User(
        first_name='Frank',
        last_name='Elliot',
        username='frank',
        birth_date=birth_date
    )
    user2 = models.User(first_name='Charlie', last_name='Joe', username='charlie', birth_date=birth_date)
    user3 = models.User(first_name='Ann', last_name='Smith', username='ann', birth_date=birth_date)

    db_session.add_all([user1, user2, user3])
    db_session.commit()

    with request_context("/?filter[first_name]=Ann"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            "first_name",
        ]) \
            .query \
            .all()

        assert len(users) == 1
        assert users[0].first_name == "Ann"


def test_custom_filter_is_applied(db_session, request_context, models):
    birth_date1 = datetime.strptime("1970-01-01", "%Y-%m-%d")
    birth_date2 = datetime.strptime("1970-06-25", "%Y-%m-%d")
    birth_date3 = datetime.strptime("2008-01-01", "%Y-%m-%d")
    user1 = models.User(
        first_name='Frank',
        last_name='Elliot',
        username='frank',
        birth_date=birth_date1
    )
    user2 = models.User(
        first_name='Charlie',
        last_name='Joe',
        username='charlie',
        birth_date=birth_date2
    )
    user3 = models.User(
        first_name='Ann',
        last_name='Smith',
        username='ann',
        birth_date=birth_date3
    )

    db_session.add_all([user1, user2, user3])
    db_session.commit()


    class BirthYearFilter(Filter):
        def filter(self, query, model, filter_name, values):
            if not len(values):
                return query
            return query.filter(
                extract("year", models.User.birth_date).in_(values)
            )

    with request_context("/?filter[year]=1970"):
        users = QueryBuilder(models.User) \
            .allowed_filters([
            AllowedFilter.custom("year", BirthYearFilter()),
        ]) \
            .query \
            .all()

        assert len(users) == 2
