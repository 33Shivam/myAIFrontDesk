from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment , CustomerQuery , KnowledgeEntry
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(post_save, sender=Appointment)
def appointment_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "appointments",
            {
                "type": "appointment_notification",
                "message": f"New appointment: {instance.customer_name} at {instance.reservation_time}",
            },
        )
@receiver(post_save, sender=CustomerQuery)
def notify_new_query(sender, instance, created, **kwargs):
    if created:  # Only notify when a new query is created
        channel_layer = get_channel_layer()
        

        # Send a message to the "queries" group
        async_to_sync(channel_layer.group_send)(
            "queries",  # Group name
            {
                "type": "query_notification",  # The method in the consumer that will handle the message
                "message": f"New query from {instance.customer_name}: {instance.query}",
            }
        )




@receiver(pre_save, sender=CustomerQuery)
def add_to_knowledge_base_on_resolve(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip if it's a new query (not an update)

    try:
        old_instance = CustomerQuery.objects.get(pk=instance.pk)
    except CustomerQuery.DoesNotExist:
        return

    # Check if was_resolved is being updated to True
    if not old_instance.was_resolved and instance.was_resolved:
        if instance.answer:
            KnowledgeEntry.objects.create(
                query=instance.query,
                answer=instance.answer
            )