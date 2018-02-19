from rest_framework import filters

class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Return only objects owned by the current user
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owners__contains=[str(request.user.id)])


class IsMemberFilterBackend(filters.BaseFilterBackend):
    """
    Return only objects owned by the current user
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(members__contains=[str(request.user.id)])
