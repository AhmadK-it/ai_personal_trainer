from rest_framework import serializers
from .models import Program, UserProgram, TrainingProgram

#daily meal
class TrainingProgramSerializer(serializers.ModelSerializer):
    program_url = serializers.SerializerMethodField()

    class Meta:
        model = TrainingProgram
        fields = ['date','program_url']
        
    def get_program_url(self, obj):
        return obj.program.url

#Meal Plan
class UserProgramSerializer(serializers.ModelSerializer):
    programs = TrainingProgramSerializer(many=True, read_only=True,source='user_program')
    class Meta:
        model = UserProgram
        fields = ['id','start_date', 'created_at', 'programs']


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['index','url']