from rest_framework import serializers
from .models import Appointment , CustomerQuery , KnowledgeEntry
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import timedelta
from django.utils import timezone
import logging
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)  # Configure this in settings if not already

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'



class CustomerQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQuery
        fields = "__all__"

    def update(self, instance, validated_data):
        old_answer = instance.answer  # store current value
        instance = super().update(instance, validated_data)

        # Trigger WebSocket only if answer was updated
        new_answer = validated_data.get("answer")
        one_minutes_ago = timezone.now() - timedelta(minutes=1)

        if new_answer and old_answer != new_answer :
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "customer_queries",  # Same group as your consumer
                {
                    "type": "query.answered",
                    "event": "ANSWER_ADDED",
                    "data": {
                        "id": instance.query_id,
                        "customer_name": instance.customer_id,
                        "query": instance.query,
                        "answer": instance.answer,
                    },
                },
            )
        else:
            raise ValidationError("Query expired. Cannot update answer after 1 minute.")


        return instance
    


class KnowledgeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeEntry
        fields = ['query', 'answer']
