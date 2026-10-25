from django.contrib import admin

from .models import ContactRequest, Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email', 'message')


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at')
    search_fields = ('name', 'phone', 'email')
