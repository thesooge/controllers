from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated


# Create your views here.
from accounts.models import Organization, Branch
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.controllers import RoleController, OnboardingController, UserController



class UserRolesView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        role_controller = RoleController()
        user_roles = role_controller.get_user_roles(user)
        return Response({"roles": [r.name for r in user_roles]})
    
class AssignRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        role_name = data.get("role_name")
        access_level = data.get("access_level")
        org_ids = data.get("organization_ids", [])
        branch_ids = data.get("branch_ids", [])

        organizations = Organization.objects.filter(id__in=org_ids)
        branches = Branch.objects.filter(id__in=branch_ids)

        controller = RoleController()
        role = controller.get_or_create_role(role_name, access_level, organizations, branches)

        controller.update_user_roles(user, [role])

        return Response({
            "message": "Role assigned successfully",
            "role_id": role.id,
            "role_name": role.name
        })   