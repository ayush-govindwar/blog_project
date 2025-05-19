from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    custom permission to only allow authors of a blog to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS: #tuple of readoly methods
            return True

        # Write permissions are only allowed to the author of the blog.
        return obj.author == request.user #if logged in user is aithor of blog

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    custom permission to only allow admins to edit or delete objects.
    regular users can read only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff