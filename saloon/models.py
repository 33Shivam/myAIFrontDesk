from django.db import models
from django.utils import timezone
from datetime import timedelta


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # <-- NEW
    name = models.CharField(max_length=255)
    phone_number = models.IntegerField( unique=True)  # <-- NEW

    def __str__(self):
        return self.name



class CustomerQuery(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE , null=True , blank=True)  # <-- NEW
    query_id = models.AutoField(primary_key=True)  # <-- NEW
    customer_name = models.CharField(max_length=255)  # <-- NEW
    query = models.TextField()
    answer = models.TextField(null=True, blank=True)  # <-- NEW
    query_date = models.DateField(auto_now=True)
    query_time = models.TimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # <-- NEW
    has_expired = models.BooleanField(default=False)
    was_resolved = models.BooleanField(default=False)  # <-- NEW

    def save(self, *args, **kwargs):
        if not self.expires_at or self.expires_at== None:
            self.expires_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def update_expiry_status(self):
        if not self.has_expired and timezone.now() > self.expires_at:
            self.has_expired = True
            self.save(update_fields=['has_expired'])

    def __str__(self):
        return f"{self.customer_name} @ {self.query_date} {self.query_time}"




class Appointment(models.Model):
    customer_name = models.CharField(max_length=255)
    reservation_date = models.DateField(auto_now=True)
    reservation_time = models.TimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} @ {self.reservation_date} {self.reservation_time}"




class KnowledgeEntry(models.Model):
    query = models.TextField()
    answer = models.TextField()
    source = models.CharField(max_length=255, blank=True)  # e.g., "user query", "admin input"
    tags = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.query[:50]
    