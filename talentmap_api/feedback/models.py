from django.db import models
from django.contrib.postgres.fields import JSONField
import hashlib


class FeedbackEntry(models.Model):
    """
    Represents an individual feedback item
    """

    comments = models.TextField(null=True, max_length=280)
    user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, null=True, help_text="The commenting user, if available")

    is_interested_in_helping = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["-date_created"]


class FrontendSecrets(models.Model):
    """
    Represents a public/secret key for a frontend
    """

    public_secret = models.TextField(unique=True)
    private_secret = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)

    def is_authorized_request(self, request):
        req_auth = request.get("auth", "")
        req_time = request.get("time", "")

        return req_auth == hashlib.sha256(f"{req_time}{self.private_secret}".encode('utf-8')).hexdigest()

    class Meta:
        managed = True


class ReportedError(models.Model):
    """
    Represents an error reported by the frontend
    """

    public_secret = models.TextField()
    error = JSONField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["-date_created"]


class ReportedEvent(models.Model):
    """
    Represents an event reported by the frontend
    """

    public_secret = models.TextField()
    event = JSONField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["-date_created"]
