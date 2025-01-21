from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, validators=[RegexValidator(r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$', 'Enter a valid email address.')])
    full_name = models.CharField(max_length=255, default='Admin')
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits.')])
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{6}$', 'Pincode must be 6 digits.')])

    # Ensure password validation criteria
    password = models.CharField(max_length=255)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone', 'pincode', 'password']

    def __str__(self):
        return self.full_name

    def clean_password(self):
        """
        Password validation: Minimum 8 characters, 1 uppercase, 1 lowercase
        """
        password = self.password
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        return password

    def save(self, *args, **kwargs):
        # Validate password before saving
        self.clean_password()
        super().save(*args, **kwargs)

# Create Content Model
class Content(models.Model):
    title = models.CharField(max_length=30)
    body = models.TextField(max_length=300)
    summary = models.CharField(max_length=60)
    document = models.FileField(upload_to='documents/')
    categories = models.JSONField()  # Store categories as a list of strings
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)