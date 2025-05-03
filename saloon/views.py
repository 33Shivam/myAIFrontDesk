from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Appointment , CustomerQuery , KnowledgeEntry
from .serializers import AppointmentSerializer , CustomerQuerySerializer , KnowledgeEntrySerializer
from rest_framework.views import APIView
from rest_framework.response import Response


# For WebSocket broadcasting
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        appointment = serializer.save()

        # Broadcast message to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "appointments",
            {
                "type": "appointment_notification",
                "message": f"New appointment: {appointment.customer_name} at {appointment.reservation_time}",
            },
        )



class CustomerQueryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CustomerQuery.objects.all().order_by("-created_at")
    serializer_class = CustomerQuerySerializer

    def perform_create(self, serializer):
        
        instance = serializer.save()

        channel_layer = get_channel_layer()


        async_to_sync(channel_layer.group_send)(
            "customer_queries",
            {
                "type": "customer_query_notification",
                "message": CustomerQuerySerializer(instance).data,
            },
        )




class KnowledgeBaseAPIView(APIView):
    def get(self, request):
        entries = KnowledgeEntry.objects.all()
        serializer = KnowledgeEntrySerializer(entries, many=True)
        return Response(serializer.data)
