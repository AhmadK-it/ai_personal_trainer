from django.shortcuts import render
from rest_framework.decorators import api_view
import logging


logger = logging.getLogger(__name__)
# @api_view(['GET','POST'])
def home(req):
    logger.info(f"Home view called with method: {req.method}")
    return render(request=req, template_name='home.html')