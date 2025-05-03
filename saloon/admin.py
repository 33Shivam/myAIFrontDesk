from django.contrib import admin
from .models import Appointment , CustomerQuery , Customer , KnowledgeEntry

# Register your models here.
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ( "customer_name", "reservation_date", "reservation_time", "created_at")
    list_filter = ("reservation_date",)
    search_fields = ("customer_name",)
    ordering = ("-created_at",)


@admin.register(CustomerQuery)
class CustomerQueryAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "query", "answer", "query_date", "query_time" ,"was_resolved")
    


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "name", "phone_number")
    search_fields = ("customer_id", "name")
    ordering = ("-customer_id",)


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ("query", "answer")
   