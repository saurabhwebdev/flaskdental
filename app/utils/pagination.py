from flask import request
from sqlalchemy import or_

class PaginationHelper:
    def __init__(self, model, page=1, per_page=10):
        self.model = model
        self.page = page
        self.per_page = per_page

    def paginate_query(self, query):
        """Paginate a SQLAlchemy query."""
        return query.paginate(
            page=self.page,
            per_page=self.per_page,
            error_out=False
        )

    @staticmethod
    def get_page_args():
        """Get pagination arguments from request."""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except (TypeError, ValueError):
            page = 1
            per_page = 10
        return page, per_page

class SearchHelper:
    @staticmethod
    def apply_search(query, model, search_term, search_fields):
        """Apply search filter to query."""
        if not search_term:
            return query
            
        search_filters = []
        for field in search_fields:
            if hasattr(model, field):
                search_filters.append(getattr(model, field).ilike(f'%{search_term}%'))
        
        if search_filters:
            return query.filter(or_(*search_filters))
        return query

class FilterHelper:
    @staticmethod
    def apply_filters(query, model, filters):
        """Apply multiple filters to query."""
        if not filters:
            return query
            
        for field, value in filters.items():
            if value and hasattr(model, field):
                if isinstance(value, list):
                    query = query.filter(getattr(model, field).in_(value))
                else:
                    query = query.filter(getattr(model, field) == value)
        return query

def get_search_args():
    """Get search arguments from request."""
    search_term = request.args.get('search', '').strip()
    filters = {}
    
    # Get all filter parameters from request
    for key, value in request.args.items():
        if key.startswith('filter_'):
            field = key[7:]  # Remove 'filter_' prefix
            filters[field] = value
            
    return search_term, filters
