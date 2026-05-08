import django_filters


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Filter helper for comma-separated numeric query parameters."""
