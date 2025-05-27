from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


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
        return Response({"roles": [r.name for r in user_roles], 
                        "role_ids": [r.id for r in user_roles]}, 
                        status=status.HTTP_200_OK)
    
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
    

class CreateOrUpdateRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        role_controller = RoleController()

        try:
            # Step 1: Get or create template
            template = role_controller.get_or_create_role_template(
                name=data["template_name"],
                access_level=data["access_level"],
                role_type=data["role_type"],
            )

            # Step 2: Get organizations and branches
            organizations = Organization.objects.filter(id__in=data.get("organization_ids", []))
            branches = Branch.objects.filter(id__in=data.get("branch_ids", []))

            # Step 3: Generate role name
            role_name = role_controller.role_name_generator(template, organizations[0]) if organizations else data["template_name"]
            
            # Step 4: Check if role exists
            existing_role = role_controller.get_role(
                name=role_name,
                access_level=template.access_level,
                organizations=organizations,
                branches=branches,
            )
           
            if existing_role and data.get("use_existing", False):
                role = role_controller.update_role_base_on_template(
                    role=existing_role,
                    template=template,
                    role_name=role_name,
                    organizaitons=organizations,
                    branches=branches,
                )
                message = "Role updated"
            else:
            
                role = role_controller.create_role_base_on_template(
                    template=template,
                    role_name=role_name,
                    organizations=organizations,
                    branches=branches,
                )
                message = "Role created"

            return Response({"message": message, "role_id": role.id, "role_name": role.name})

        except KeyError as e:
            return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    