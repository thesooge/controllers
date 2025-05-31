from accounts.controllers import MembershipController, RoleController
from accounts.models import MembershipTier, SubscriptionTier, RoleTemplate
from django.core.exceptions import ValidationError

class CustomMembershipController(MembershipController):

    @classmethod
    def create_membership(cls, user, subscription_tier, invite=None, roles=[]):
        membership = MembershipTier.objects.create(
            user=user,
            subscription_tier=subscription_tier,
            subscription_status='active',
            invite=invite
        )
        membership.roles.set(roles)
        return membership

    @classmethod
    def update_status(cls, membership: MembershipTier, new_status: str):
        membership.subscription_status = new_status
        membership.save()
        return membership
    
    @classmethod
    def get_active_membership(cls, user):
        return MembershipTier.objects.filter(user=user, subscription_status='active').first()
    
    @classmethod
    def assign_roles_from_tier(cls, membership: MembershipTier):
        role_templates = membership.subscription_tier.role_templates.all()
        for template in role_templates:
            # use RoleController to create role from template
            role = RoleController().create_role_base_on_template(template, role_name=f"{template.name} - {membership.user.username}")
            membership.roles.add(role)

    @staticmethod
    def create_subscription_tier(
        title,
        description1=None,
        description2=None,
        description3=None,
        price=0.0,
        is_active=True,
        role_template_ids=None,
        payment_plans=None
    ):
        if not title:
            raise ValidationError("Title is required for Subscription Tier.")

        tier = SubscriptionTier.objects.create(
            title=title,
            description1=description1,
            description2=description2,
            description3=description3,
            price=price,
            is_active=is_active,
            payment_plans=payment_plans or {},
        )

        if role_template_ids:
            templates = RoleTemplate.objects.filter(id__in=role_template_ids)
            tier.role_templates.set(templates)

        return tier        