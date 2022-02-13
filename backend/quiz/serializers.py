from dataclasses import fields
from rest_framework import serializers
from .models import Quiz

# Quiz Serializer
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'