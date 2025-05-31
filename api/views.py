from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# Create your views here.
from accounts.models import Organization, Branch, Onboarding, MembershipTier, SubscriptionTier
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.controllers import RoleController, OnboardingController, UserController, MembershipController
from .serializers import CompletedOnboardingStepSerializer

from .controllers import CustomMembershipController



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
        
class CreateOnboardingView(APIView):
    def post(self, request):

        role_controller = RoleController()
        onboarding_controller = OnboardingController()
        data = request.data

        try:    
            user = request.user
            
            name = data.get("onboarding_name")
            user_roles = role_controller.get_user_roles(user)
            description = data.get("description")
            if not user_roles.exists():
                return Response({"error": "User has no roles assigned."}, status=status.HTTP_400_BAD_REQUEST)

            user_role = user_roles.first()

            onboarding_instance = onboarding_controller.create_onboarding(name, description, user_role)

            return Response({
                "message": "Onboarding instance created successfully",
                "role_id": onboarding_instance.id,
                "role_name": onboarding_instance.name
            })   
        except KeyError as e:
            return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


class CreateOnboardingStepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        onboarding_controller = OnboardingController()
        data = request.data

        try:
            onboarding_id = data.get("onboarding_id")
            step_name = data.get("step_name")
            description = data.get("description", "")
            level = data.get("level", 1)
            optional = data.get("optional", False)

            if not onboarding_id or not step_name:
                return Response(
                    {"error": "Missing required fields: 'onboarding_id' and 'step_name'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the onboarding instance
            try:
                onboarding = Onboarding.objects.get(id=onboarding_id)
            except Onboarding.DoesNotExist:
                return Response({"error": "Onboarding not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create the onboarding step using the controller
            step = onboarding_controller.create_onboarding_step(
                onboarding=onboarding,
                step_name=step_name,
                description=description,
                level=level,
                optional=optional,
            )

            return Response({
                "message": "Onboarding step created successfully",
                "step_id": step.id,
                "step_name": step.name,
                "level": step.level,
                "optional": step.optional,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        

class CompletedOnboardingStepsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        onboarding_name = request.query_params.get("onboarding_name")
        onboarding_controller = OnboardingController()

        if not onboarding_name:
            return Response(
                {"error": "Missing required query parameter: 'onboarding_name'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            completed_steps = onboarding_controller.get_all_completed_steps(onboarding_name)

            # You need a serializer to represent these steps — assumed here
            serialized = CompletedOnboardingStepSerializer(completed_steps, many=True)

            return Response({"completed_steps": serialized.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class SetOnboardingStepDoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        onboarding_name = data.get("onboarding_name")
        step_name = data.get("step_name")
        status_value = data.get("status", "done")  # optional, default to "done"

        if not onboarding_name or not step_name:
            return Response({
                "error": "onboarding_name and step_name are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        onboarding_controller = OnboardingController()

        try:
            onboarding = onboarding_controller.get_onboarding(onboarding_name)
            onboarding_step = onboarding_controller.get_onboarding_step_by_name(onboarding, step_name)
            completed_step = onboarding_controller.set_completed_step(
                user=user,
                onboarding_step=onboarding_step,
                status=status_value
            )

            return Response({
                "message": "Step marked as completed.",
                "step_id": completed_step.id,
                "step_status": completed_step.step_status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class CancelMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        membership_id = request.data.get("membership_id")
        if not membership_id:
            return Response(
                {"error": "membership_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = MembershipTier.objects.get(id=membership_id)
            MembershipController.cancel_membership(membership)
            return Response({"message": "Membership cancelled successfully."}, status=status.HTTP_200_OK)
        except MembershipTier.DoesNotExist:
            return Response({"error": "Membership not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
class CreateMembershipView(APIView):
    def post(self, request):
        user = request.user
        tier_id = request.data.get("subscription_tier_id")

        try:
            subscription_tier = SubscriptionTier.objects.get(id=tier_id)
        except SubscriptionTier.DoesNotExist:
            return Response({"error": "Subscription tier not found"}, status=404)

        membership = CustomMembershipController.create_membership(user, subscription_tier)

        return Response({
            "message": "Membership created",
            "membership_id": membership.membership_id
        }, status=201)        
    

class AssignMembershipRolesView(APIView):
    def post(self, request):
        user = request.user
        membership = CustomMembershipController.get_active_membership(user)
        if not membership:
            return Response({"error": "No active membership"}, status=400)

        MembershipController.assign_roles_from_tier(membership)
        return Response({"message": "Roles assigned successfully"})    
    
class CreateSubscriptionTierView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        try:
            tier = CustomMembershipController.create_subscription_tier(
                title=data.get("title"),
                description1=data.get("description1"),
                description2=data.get("description2"),
                description3=data.get("description3"),
                price=data.get("price"),
                is_active=data.get("is_active", True),
                role_template_ids=data.get("role_template_ids", []),
                payment_plans=data.get("payment_plans", {}),
            )

            return Response({
                "message": "Subscription tier created successfully.",
                "tier_id": tier.id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    