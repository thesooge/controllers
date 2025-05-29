from rest_framework import serializers
from accounts.models import CompletedOnboardingStep

class CompletedOnboardingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedOnboardingStep
        fields = '__all__'