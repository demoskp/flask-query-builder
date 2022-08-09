# Build SQLAlchemy queries from API requests

![Test Status](https://img.shields.io/github/workflow/status/demoskp/flask-query-builder/Release?label=tests)
![Build Status](https://img.shields.io/github/workflow/status/demoskp/flask-query-builder/Release?label=release)
[![PyPI Version](http://img.shields.io/pypi/v/flask-query-builder.svg)](https://pypi.python.org/pypi/flask-query-builder)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-query-builder)

This package allows you to filter and sort based on a request. Query parameter names follow the [JSON API specification](http://jsonapi.org/) as closely as possible.

## Basic usage

### Filter a query based on a request: `/users?filter[name]=John`:

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


### Sorting a query based on a request: `/users?sort=id`:

```python
users = (
    QueryBuilder(User)
        .allowed_sorts(['last_name'])
        .query
        .all()
    )
# all `User`s sorted by ascending last_name
```

### Works together nicely with existing queries:

```python
query = User.query.filter_by(name="John")

query = (
    QueryBuilder(model=User, query=query) // start from an existing query
        .allowed_filters(["first_name", "last_name"])
        .query
)
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