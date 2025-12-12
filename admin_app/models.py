from django.db import models

# Create your models here.
# In models.py or utils
from rest_framework.authtoken.models import Token

def generate_auth_token(self):
    token, _ = Token.objects.get_or_create(user=self)
    return token.key



from django.db import models

class Ward(models.Model):
    ward_number = models.IntegerField(unique=True)
    ward_name = models.CharField(max_length=150)
    total_voters = models.IntegerField() 

    def __str__(self):
        return f"Ward {self.ward_number} - {self.ward_name}"
    


class ElectionResult(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    address = models.TextField()
    party = models.CharField(max_length=100)
    party_logo = models.ImageField(upload_to='party_logos/')
    candidate_photo = models.ImageField(upload_to='candidate_photos/')
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - Ward {self.ward.ward_number}"

