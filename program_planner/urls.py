
from django.urls import path
from . import views


urlpatterns = [
    path('generate-training-plan/', views.generate_training_plan, name='generate_training_plan'),
    path('view-training-plan/<int:user_program_id>/', views.view_training_plan, name='view_training_plan'),
    path('pdf/<int:id>/', views.serve_pdf_file, name='serve_pdf_file'),
]
