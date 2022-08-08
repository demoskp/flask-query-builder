import re
from typing import List

from flask import request
from sqlalchemy.orm import Query
from sqlalchemy.orm import declarative_base

from flask_query_builder.exceptions import InvalidFilterException, InvalidSortException
from flask_query_builder.filters import Filter, ExactFilter, PartialFilter
from flask_query_builder.sorts import Sort, FieldSort

BaseModel = declarative_base()


class AppliedSort:
    """Helper class for sorts applied on the request"""

    def __init__(self, name, descending=False):
        self.name = name
        self.descending = descending


class AllowedFilter:
    """A class for specifying a filter that is allowed on the request"""

    def __init__(self, name: str, filter_class: Filter, internal_name: str = None):
        self.name = name
        self.internal_name = internal_name
        self.filter_class = filter_class

    @classmethod
    def exact(cls, name, internal_name: str = None):
        """Specify an exact match filter"""
        return cls(name, ExactFilter(), internal_name)

    @classmethod
    def partial(cls, name, internal_name: str = None):
        """Specify a case-insensitive filter wildcard filter"""
        return cls(name, PartialFilter(), internal_name)

    @classmethod
    def custom(cls, name: str, filter_class: Filter):
        """Specify a custom filter by providing your own custom filter"""
        return cls(name, filter_class)


class AllowedSort:
    """A class for specifying a sort that is allowed on the request"""

    def __init__(self, name: str, sort_class: Sort, internal_name: str = None):
        self.name = name
        self.internal_name = internal_name
        self.sort_class = sort_class

    @classmethod
    def field(cls, name: str, internal_name: str = None):
        """Specify a field sort"""
        return cls(name, FieldSort(), internal_name)

    @classmethod
    def custom(cls, name: str, sort_class: Sort, internal_name: str = None):
        """Specify a custom sort by providing your own custom sort"""
        return cls(name, sort_class, internal_name)


class QueryBuilder:
    """The base class for starting your query"""

    def __init__(self, model: BaseModel, query=None):
        self.model = model
        self._query = query or model.query

    def allowed_filters(self, filters):
        """Provide a list of filters that can be applied on the request"""
        applied_filters = self._get_applied_filters()
        allowed_filter_map = self._get_filter_map(filters)
        for applied_filter in applied_filters:
            if applied_filter not in allowed_filter_map:
                raise InvalidFilterException(f"Applied filter '{applied_filter}' not allowed")
            self._apply_filter(allowed_filter_map.get(applied_filter))
        return self

    def allowed_sorts(self, sorts):
        """Provide a list of sorts that can be applied on the request"""
        applied_sorts = self._get_applied_sorts()
        allowed_sort_map = self._get_sort_map(sorts)
        for applied_sort in applied_sorts:
            if applied_sort.name not in allowed_sort_map:
                raise InvalidSortException(f"Applied sort '{applied_sort.name}' not allowed")
            self._apply_sort(allowed_sort_map.get(applied_sort.name), applied_sort.descending)
        return self

    def _get_filter_map(self, filters):
        """Get a dictionary of filter names with their corresponding filter"""
        filter_map = {}
        for filter in filters:
            if isinstance(filter, AllowedFilter):
                filter_map[filter.name] = filter
            else:
                filter_map[filter] = AllowedFilter.exact(filter)
        return filter_map

    def _get_sort_map(self, sorts):
        """Get a dictionary of sort names with their corresponding sort"""
        sort_map = {}
        for sort in sorts:
            if isinstance(sort, AllowedSort):
                sort_map[sort.name] = sort
            else:
                sort_map[sort] = AllowedSort.field(sort)
        return sort_map

    def _get_applied_sorts(self) -> List[AppliedSort]:
        """Get the list of sorts applied on the request"""
        raw_sorts = request.args.get("sort")
        if raw_sorts is None:
            return []

        raw_sorts = raw_sorts.split(",")
        formatted_sorts = []
        for sort in raw_sorts:
            if sort[0] == "-":
                final_sort = AppliedSort(sort[1:], True)
            else:
                final_sort = AppliedSort(sort)

            formatted_sorts.append(final_sort)

        return formatted_sorts

    def _get_applied_filters(self) -> List[str]:
        """Get the list of filters applied on the request"""
        applied_filters = []
        for arg in request.args:
            matches = re.findall(r"(?<=filter\[).[a-z._-]+", arg)
            if len(matches) == 1:
                applied_filters.append(matches[0])
        return applied_filters

    def _apply_filter(self, allowed_filter) -> None:
        """Mutate the query by applying a filter"""
        values = self._get_filter_values(allowed_filter.name)
        filter_name = allowed_filter.internal_name or allowed_filter.name
        self._query = allowed_filter.filter_class.filter(self._query, self.model, filter_name, values)

    def _apply_sort(self, allowed_sort, descending) -> None:
        """Mutate the query by applying a sort"""
        sort_name = allowed_sort.internal_name or allowed_sort.name
        self._query = allowed_sort.sort_class.sort(self._query, self.model, sort_name, descending)

    @property
    def query(self) -> Query:
        """Get the query object back from the QueryBuilder"""
        return self._query

    def _get_qualified_filter_name(self, value):
        """Get the filter name as it was applied on the request"""
        return f"filter[{value}]"

    def _get_filter_values(self, filter_name) -> List[str]:
        """Get a list of values that were applied on the request"""
        name = self._get_qualified_filter_name(filter_name)
        value = request.args.get(name)
        return value.split(",")
