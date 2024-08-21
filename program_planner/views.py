from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import UserProfile
from django.shortcuts import get_object_or_404
from .models import PDFFile,Program, UserProgram, TrainingProgram
from .serializers import ProgramSerializer,UserProgramSerializer, TrainingProgramSerializer
from .program_processor import predict, loaded_pipeline
import json
from datetime import date, timedelta
import os
import server.settings as settings
from django.shortcuts import render


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_training_plan(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    print(f'profile - {profile}')
    # Update user profile with the data from the request
    profile_data = request.data.get('profile', {})
    print(profile_data)
    profile.update_basic_info(
        age=profile_data.get('age', profile.age),
        weight=profile_data.get('weight', profile.weight),
        height=profile_data.get('height', profile.height),
        weakness_points=profile_data.get('weakness_points', profile.weakness_points),
        experience_level=profile_data.get('experience_level', profile.experience_level)
    )
    
    recommended_prog_id = loaded_pipeline.predict()
    print(recommended_prog_id)
    if not recommended_prog_id:
        return Response({"detail": "Failed to generate plan"}, status= status.HTTP_400_BAD_REQUEST, content_type='application/json')
    
    try:
        program = Program.objects.get(index=recommended_prog_id)
    except Exception as e:
        print(f"error get data {e}")
        
    user_program, _= UserProgram.objects.get_or_create(
        user=request.user,
        defaults={'start_date': date.today()}
    )
    
    prog = TrainingProgram.objects.create(
        user_program=user_program,
        date=date.today(),
        program=program
    )
    
    serializer = UserProgramSerializer(user_program)
    res = {
        "id":user_program.id,
        "url": program.url
    }
    return Response(res, status= status.HTTP_201_CREATED, content_type='application/json')


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_training_plan(request, user_program_id):
    user_program = get_object_or_404(UserProgram, id=user_program_id, user=request.user)
    serializer = UserProgramSerializer(user_program)
    return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')


def serve_pdf_file(request, id):
    pdf_file = get_object_or_404(PDFFile, id=id)
    print(pdf_file.file_path)
    file_path = os.path.join(settings.STATIC_ROOT, pdf_file.file_path)
    print(file_path)
    # Check if the file exists
    if os.path.exists(file_path):
        # Generate the download link
        download_link = request.build_absolute_uri(
            f"/pdf/{pdf_file.id}/download/"
        )
        
        # Render the template with the download link
        return render(request, 'pdf_file.html', {'download_link': download_link})
    else:
        return Response('File not found', status=404)