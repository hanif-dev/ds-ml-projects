# backend/edu_core/serializers.py
from rest_framework import serializers
from .models import School, Student

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__' # Akan menyertakan semua field dari model School

class StudentSerializer(serializers.ModelSerializer):
    # Ini akan menampilkan nama sekolah daripada hanya ID sekolah di API siswa
    school_name = serializers.ReadOnlyField(source='school.name')

    class Meta:
        model = Student
        fields = '__all__' # Menyertakan semua field
        # Jika Anda ingin lebih spesifik, gunakan tuple:
        # fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'school', 'school_name', 'enrollment_date', 'updated_at']
