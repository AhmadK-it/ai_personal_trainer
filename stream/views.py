from django.shortcuts import render

# Create your views here.

def video_stream(req):
    return render(request=req, template_name='video_stream.html')