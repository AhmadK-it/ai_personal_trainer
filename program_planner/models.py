from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

#meal
class Program(models.Model):
    index = models.IntegerField(primary_key=True ,default=0)
    url = models.URLField()
    
    def __str__(self):
        return f"{self.identifire} this is noise {self.url}"
#meal plan
class UserProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='program')
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return f"{self.user.username}"
    
#daily meal
class TrainingProgram(models.Model):
    user_program = models.ForeignKey(UserProgram, on_delete=models.CASCADE, related_name='user_program')
    date = models.DateField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.program.index}, from date: {self.date}"

# Assuming you have a model to store PDF file information
class PDFFile(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)






