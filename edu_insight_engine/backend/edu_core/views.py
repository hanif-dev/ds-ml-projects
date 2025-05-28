from django.shortcuts import render

# Create your views here.
# backend/edu_core/views.py
from rest_framework import viewsets
from .models import School, Student
from .serializers import SchoolSerializer, StudentSerializer

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
