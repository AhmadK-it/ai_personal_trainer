from django.shortcuts import render
from rest_framework.decorators import api_view

@api_view(['GET','POST'])
def home(req):
    return render(request=req, template_name='home2.html')