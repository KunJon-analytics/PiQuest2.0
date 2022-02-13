from .models import Quiz
from .serializers import QuizSerializer
from rest_framework import viewsets, permissions

# Quiz viewset
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    permission_classes = [permissions.AllowAny]