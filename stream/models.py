from django.db import models
import uuid

class VideoSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.session_id} - {'Active' if self.active else 'Inactive'}"

