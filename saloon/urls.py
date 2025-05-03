from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet , CustomerQueryViewSet , KnowledgeBaseAPIView

router = DefaultRouter()
router.register(r"queries", CustomerQueryViewSet)
router.register(r'appointments', AppointmentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path("knowledge-base/", KnowledgeBaseAPIView.as_view(), name="knowledge-base"),

]