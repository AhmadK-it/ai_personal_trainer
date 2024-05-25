from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _ 

class MyUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_('please enter valid email'))
    
    def create_user(self, username, email, password, **extra_fields):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_('email is required'))
        
        if not username:
            raise ValueError(_('username is required'))
        

        user=self.model(username=username,email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_verified',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('super user must be staff dick head'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('super user must be defined as superuser dick head'))
        if extra_fields.get('is_verified') is not True:
            raise ValueError(_('super user must be verified dick head'))
        
        user = self.create_user(username=username, email=email, password=password, **extra_fields)
        user.save(using=self._db)
        return user
        