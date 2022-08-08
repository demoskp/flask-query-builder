from abc import abstractmethod


class Filter:
    """Base class for custom filters"""
    @abstractmethod
    def filter(self, query, model, filter_name, values):
        pass


class ExactFilter(Filter):
    """Perform an exact match filter on a model field"""
    def filter(self, query, model, filter_name, values):
        if len(values) == 1:
            return query.filter_by(**{filter_name: values[0]})
        return query.filter(getattr(model, filter_name).in_(values))


class PartialFilter(Filter):
    """Perform a case-insensitive wildcard filter on a model field"""
    def filter(self, query, model, filter_name, values):
        if len(values) == 1:
            return query.filter(getattr(model, filter_name).ilike(f"%{values[0]}%"))
        else:
            q = query
            for value in values:
                q = q.filter(getattr(model, filter_name).ilike(f"%{value}%"))
            return q
