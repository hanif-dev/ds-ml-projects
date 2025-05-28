from django.db import models

# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Schools" # Agar di admin panel terbaca "Schools" bukan "Schoolss"

    def __str__(self):
        return self.name

class Student(models.Model):
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
        ('O', 'Lainnya'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students') # Relasi ke model School
    enrollment_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('first_name', 'last_name', 'date_of_birth', 'school') # Kombinasi unik
        ordering = ['last_name', 'first_name'] # Pengurutan default

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name or ''}".strip()
        return f"{full_name} ({self.school.name})" if self.school else full_name
