from django.db import models
from apps.users.models import User


class Record(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    distance = models.IntegerField(help_text='Distance in meters')
    latitude = models.FloatField()
    longitude = models.FloatField()
    weather_conditions = models.CharField(max_length=255)

    class Meta:
        ordering = ['-created']
