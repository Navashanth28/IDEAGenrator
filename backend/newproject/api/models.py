from django.db import models

class Survey(models.Model):
    industry = models.CharField(max_length=255)
    industry_other = models.CharField(max_length=255, blank=True, null=True)
    target_audience = models.CharField(max_length=255)
    technology = models.JSONField(default=list)
    sub_technology = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=255, blank=True, null=True)
    web_frontend = models.JSONField(default=list, blank=True, null=True)
    web_backend = models.JSONField(default=list, blank=True, null=True)
    web_hosting = models.JSONField(default=list, blank=True, null=True)
    web_database = models.JSONField(default=list, blank=True, null=True)
    security_features = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.industry} - {self.created_at.strftime('%Y-%m-%d')}"