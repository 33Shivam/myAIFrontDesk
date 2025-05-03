# salon/routing.py
from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r"ws/appointments/$", consumer.AppointmentConsumer.as_asgi()),
    re_path(r"ws/queries/$", consumer.CustomerQueryConsumer.as_asgi()),

]
