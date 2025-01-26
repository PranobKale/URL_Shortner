from django.db import models

class URL(models.Model):
    original_url = models.URLField(unique=True)
    shortened_url = models.CharField(max_length=6, unique=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    expiration_timestamp = models.DateTimeField()

class AccessLog(models.Model):
    shortened_url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name='access_logs')
    access_timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
