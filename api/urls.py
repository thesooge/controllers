from django.urls import path
from .views import UserRolesView, AssignRoleView, CreateOrUpdateRoleView

urlpatterns = [
    path("user-roles", UserRolesView.as_view()),
    path("assign-role/", AssignRoleView.as_view()),
    path('roles/create-or-update/', CreateOrUpdateRoleView.as_view()),
]
