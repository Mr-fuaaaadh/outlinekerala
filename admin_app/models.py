from django.db import models

# Create your models here.
# In models.py or utils
from rest_framework.authtoken.models import Token

def generate_auth_token(self):
    token, _ = Token.objects.get_or_create(user=self)
    return token.key
