from abc import abstractmethod

from sqlalchemy import desc


class Sort:
    """Base class for custom sorts"""
    @abstractmethod
    def sort(self, query, model, sort_name, descending):
        pass


class FieldSort(Sort):
    """Perform sorting on a model field"""
    def sort(self, query, model, sort_name, descending):
        if descending:
            return query.order_by(desc(sort_name))
        return query.order_by(sort_name)
