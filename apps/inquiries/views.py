from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import ContactRequest, Feedback
from .serializers import ContactRequestSerializer, FeedbackSerializer


class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (AllowAny,)


class ContactRequestCreateView(generics.CreateAPIView):
    queryset = ContactRequest.objects.all()
    serializer_class = ContactRequestSerializer
    permission_classes = (AllowAny,)
