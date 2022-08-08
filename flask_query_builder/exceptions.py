class InvalidFilterException(Exception):
    """Exception for when a filter is present on request that was not allowed as part of the QueryBuilder"""
    pass


class InvalidSortException(Exception):
    """Exception for when a sort is present on request that was not allowed as part of the QueryBuilder"""
    pass
