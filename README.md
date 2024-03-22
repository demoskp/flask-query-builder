# Build SQLAlchemy queries from API requests

![Test Status](https://img.shields.io/github/actions/workflow/status/demoskp/flask-query-builder/release.yml?branch=master&label=tests)
![Build Status](https://img.shields.io/github/actions/workflow/status/demoskp/flask-query-builder/release.yml?branch=master&label=build)
[![PyPI Version](http://img.shields.io/pypi/v/flask-query-builder.svg)](https://pypi.python.org/pypi/flask-query-builder)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-query-builder)

This package allows you to filter and sort based on a request. Query parameter names follow the [JSON API specification](http://jsonapi.org/) as closely as possible.

## Prerequisites
If you are using flask-sqlalchemy you don't need to perform any setup steps. 

If however you are using vanilla sqlalchemy you need to assign your query object to your base model like so:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///db")

session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine
    )
)

Model = declarative_base()
Model.query = session.query_property()
```


## Basic usage

### Filter a query based on a request

`/users?filter[name]=John`

```python
from flask_query_builder.querying import QueryBuilder

users = (
    QueryBuilder(User)
        .allowed_filters(['name'])
        .query
        .all()
    )

# all `User`s that contain the string "John" in their name
```


### Sorting a query based on a request

`/users?sort=id`

```python
users = (
    QueryBuilder(User)
        .allowed_sorts(['last_name'])
        .query
        .all()
    )
# all `User`s sorted by ascending last_name
```

### Works together nicely with existing queries

```python
query = User.query.filter_by(name="John")

query = (
    QueryBuilder(model=User, query=query) # start from an existing query
        .allowed_filters(["first_name", "last_name"])
        .query
)
```


## Filtering
You specify the filters on the query by using the keyword `filter` followed by the name of the filter inside square brackets `?filter[name]=John`

You can specify a list of values to filter by separated by commas `?filter[name]=John,Mary`

You can add multiple filters to the request `?filter[name]=John,Mary&filter[age]=30`

### Exact Filter
You can use an exact filter to perform an exact match on any fields that exist on the model by using `AllowedFilter.exact()`, for example:

Request query: `/users?filter[first_name]=John`

```python
users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.exact("first_name")
    ])
    .query
    .all()
)
```
If you use a string value instead of `AllowedFilter.exact` it has the same effect as it gets converted to an exact filter in the background for example:
```python
users = (
    QueryBuilder(User)
    .allowed_filters([
       "first_name"
    ])
    .query
    .all()
)
```

With the `exact` filter you can use a different filter name on the request to what is named on your model for example:

Request query: `/users?filter[name]=John`
```python
users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.exact("name", "first_name")
    ])
    .query
    .all()
)
```
The first parameter is always the name used on the request and the second one is the internal name on your models.


### Partial Filter
You can use a partial filter to perform a case-insensitive wildcard search on any fields that exist on the model by using `AllowedFilter.partial()`, for example:

Request query: `/users?filter[first_name]=John`
```python
users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.partial("first_name")
    ])
    .query
    .all()
)
```
With the `partial` filter you can use a different filter name on the request to what is named on your model for example:

Request query: `/users?filter[name]=John`
```python
users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.partial("name", "first_name")
    ])
    .query
    .all()
)
```
The first parameter is always the name used on the request and the second one is the internal name on your models.


### Custom Filter
When your filter is more complex that a simple field on a model you can create a custom filter and add it using `AllowedFilter.custom()`

To create a custom filter you need to inherit from `Filter` and implement the `filter` method defined in the base class.

Here we assume a user has a related model called Address where a user has an address.
We therefore create a custom filter where we can filter users by their address name.

`Note: Remember to join any tables used in a filter like we do below.`

```python
from flask_query_builder.filters import Filter


# query -> the query object that contains the existing queries
# model -> the model class that the QueryBuilder has been initialized on
# filter_name -> the external filter name used on the request
# values -> a list of values passed to the request

class AddressRoadFilter(Filter):
    def filter(self, query, model, filter_name, values):
        if not len(values):
            return query
        return query.filter(Address.street_name.in_(values))

users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.custom("road", AddressRoadFilter())
    ])
    .query
    .join(User.address)
    .all()
)
```

## Sorting
You specify the sorts on the query by using the `sort` key

Sorting in ascending order is the default option `?sort=name`

Sorting in descending order is achieved by adding a `-` sign in front of the field `?sort=-name`

You can sort by multiple columns or custom sorts by separating values with a comma`?sort=name,id`

### Field Sort
You can use an field sort to sort by any fields that exist on the model by using `AllowedSort.field()`

Request query: `/users?sort=first_name`:
```python
users = (
    QueryBuilder(User)
    .allowed_sorts([
        AllowedSort.field("first_name")
    ])
    .query
    .all()
)
```
If you use a string value instead of `AllowedSort.field` it has the same effect as it gets converted to a field sort in the background for example:
```python
users = (
    QueryBuilder(User)
    .allowed_sorts([
       "first_name"
    ])
    .query
    .all()
)
```
With the `field` sort you can use a different sort name on the request to what is named on your model for example:

Request query: `/users?sort=name`:

```python
users = (
    QueryBuilder(User)
    .allowed_filters([
        AllowedFilter.exact("name", "first_name")
    ])
    .query
    .all()
)
```
The first parameter is always the name used on the request and the second one is the internal name on your models.

### Custom Sort
When your sort logic is more complex that a simple field on a model you can create a custom sort and add it using `AllowedSort.custom()`

To create a custom sort you need to inherit from `Sort` and implement the `sort` method defined in the base class.

Here we assume a user has a related model called Address where a user has an address.
We therefore create a custom sort where we can sort users by their address name.

`Note: Remember to join any tables used in a sort like we do below.`
```python
from flask_query_builder.sorts import Sort

# query -> the query object that contains the existing queries
# model -> the model class that the QueryBuilder has been initialized on
# sort_name -> the external sort name used on the request
# descending -> specifies if the sort is in descending order

class AddressRoadSort(Sort):
    def sort(self, query, model, sort_name, descending):
        if descending:
            return query.order_by(Address.street_name.desc())
        return query.order_by(Address.street_name)

users = (
    QueryBuilder(User)
    .allowed_sorts([
        AllowedSort.custom("road", AddressRoadSort())
    ])
    .query
    .join(User.address)
    .all()
)
```

## Exceptions
When using the `QueryBuilder` and adding any of the methods `allowed_sorts` or `allowed_filters`
if the frontend request a filter or a sort that was not included in any of those lists an Exception will be thrown letting
you know that the `filter` or the `sort` is not allowed.


## Installation

You can install the package via pip:

```bash
pip install flask-query-builder
```

## Documentation

You can find the documentation on https://petsas.dev/projects/flask-query-builder

Find yourself stuck using the package? Found a bug? Do you have general questions or suggestions for improving the media library? Feel free to [create an issue on GitHub](https://github.com/demoskp/flask-query-builder/issues), we'll try to address it as soon as possible.

If you've found a bug regarding security please mail [security@petsas.dev](mailto:security@petsas.dev) instead of using the issue tracker.

### Upgrading

Please see [UPGRADING.md](UPGRADING.md) for details.

### Testing

```bash
pytest tests/
```

### Changelog

Please see [CHANGELOG](CHANGELOG.md) for more information what has changed recently.

## Contributing

Please see [CONTRIBUTING](https://github.com/demoskp/flask-query-builder/CONTRIBUTING.md) for details.

### Security

If you've found a bug regarding security please mail [security@petsas.dev](mailto:security@petsas.dev) instead of using the issue tracker.

## License

The MIT License (MIT). Please see [License File](LICENSE.md) for more information.