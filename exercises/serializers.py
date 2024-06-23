from rest_framework.serializers import ModelSerializer
from .models import Exercise

class ExcerciseSerializer(ModelSerializer):
    class Meta:
        model= Exercise
        fields = ('id', 'name', 'instructions', 'targeted_muscles', 'groupID', 'groupName')
