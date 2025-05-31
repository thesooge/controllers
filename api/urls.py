from django.urls import path
from .views import UserRolesView, AssignRoleView, CreateOrUpdateRoleView, CreateOnboardingView, CreateOnboardingStepView, CompletedOnboardingStepsView, SetOnboardingStepDoneView, CancelMembershipView, AssignMembershipRolesView, CreateMembershipView, CreateSubscriptionTierView

urlpatterns = [
    path("user-roles/", UserRolesView.as_view()),
    path("assign-role/", AssignRoleView.as_view()),
    path('roles/create-or-update/', CreateOrUpdateRoleView.as_view()),
    path("onboarding/create", CreateOnboardingView.as_view()),
    path("onboarding-step/create", CreateOnboardingStepView.as_view()),
    path("completed-steps/", CompletedOnboardingStepsView.as_view()),
    path("onboarding-step/done", SetOnboardingStepDoneView.as_view()),
    path("cancel-membership/", CancelMembershipView.as_view()),
    path("assign-membership-roles/", AssignMembershipRolesView.as_view()),
    path("create-membership/", CreateMembershipView.as_view()),
    path("create-subscription-tier/", CreateSubscriptionTierView.as_view()),


]
