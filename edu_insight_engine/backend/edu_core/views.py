from django.shortcuts import render

# Create your views here.
# backend/edu_core/views.py
from rest_framework import viewsets
from .models import School, Student
from .serializers import SchoolSerializer, StudentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count 

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class SchoolAnalyticsView(APIView):
    """
    API View to get analytics data for schools,
    e.g., student count per school.
    """
    def get(self, request, *args, **kwargs):
        schools_with_student_count = School.objects.annotate(
            student_count=Count('students')
        ).order_by('name')

        data = []
        for school in schools_with_student_count:
            male_students = school.students.filter(gender='L').count()
            female_students = school.students.filter(gender='P').count()

            data.append({
                'id': school.id,
                'name': school.name,
                'city': school.city,
                'province': school.province,
                'student_count': school.student_count,
                'gender_distribution': {
                    'L': male_students,
                    'P': female_students
                }
            })
        return Response(data)
