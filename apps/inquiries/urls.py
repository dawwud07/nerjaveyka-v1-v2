from django.urls import path

from .views import ContactRequestCreateView, FeedbackCreateView

urlpatterns = [
    path('feedbacks/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('requests/', ContactRequestCreateView.as_view(), name='request-create'),
]
