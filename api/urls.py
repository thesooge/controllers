from django.urls import path
from .views import UserRolesView, AssignRoleView

urlpatterns = [
    path("user-roles", UserRolesView.as_view()),
    path("assign-role/", AssignRoleView.as_view()),
]
