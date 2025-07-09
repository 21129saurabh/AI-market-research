import uuid
from django.db import models
from django.utils.timezone import localtime

class Website(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    api_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain


class ChatUser(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company_name = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat User"
        verbose_name_plural = "Chat Users"

    def __str__(self):
        return f"{self.name} ({self.email}) "


class ChatMessage(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    session_id = models.CharField(max_length=255)
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ['-timestamp']

    

    def __str__(self):
        local_time = localtime(self.timestamp)  # Converts UTC to IST (or current TIME_ZONE)
        return f"{self.user.name if self.user else 'Anonymous'} | @ {local_time.strftime('%Y-%m-%d %H:%M')}"

class IngestedFile(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="ingested_files")
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Ingestion for {self.website.domain} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"

