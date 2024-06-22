from django.db import models
from django.utils.translation import gettext_lazy as _


class Exercise(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True,verbose_name=_('Exercise name'))
    instructions = models.TextField(verbose_name=_('Exercise instructions'))
    targeted_muscles = models.TextField(verbose_name=_('Exercise target'))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Rank {self.id} for {self.name}'
    
    class Meta:
        ordering = ['-updated']