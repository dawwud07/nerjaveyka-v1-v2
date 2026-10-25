from django.db import models


class Feedback(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_feedback'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Feedback from {self.name}'


class ContactRequest(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_contactrequest'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Request from {self.name}'
