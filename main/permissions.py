from rest_framework.permissions import BasePermission


class IsAuthorPerm(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.author


class IsAuthorUserPerm(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.user


class IsProfileUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.data)
        print(view)
        print(obj.email)
        return request.user.is_authenticated and obj.email == obj.email


class IsAuthorImagePerm(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.post.author

