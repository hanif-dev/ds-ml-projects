# backend/populate_data.py

import os
import django
from django.conf import settings

# Konfigurasi Django agar script ini dapat mengakses model
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_insight_api.settings')
django.setup()

from edu_core.models import School, Student
import random
from faker import Faker
from django.utils import timezone # Import timezone untuk tanggal


fake = Faker('id_ID')  # Untuk menghasilkan data berbahasa Indonesia

# Fungsi untuk membuat data dummy
def create_dummy_data(num_schools=5, num_students_per_school=20):
    print(f"Membuat {num_schools} sekolah dan {num_students_per_school} siswa per sekolah...")

    # Hapus data lama (opsional, untuk memastikan database bersih)
    Student.objects.all().delete()
    School.objects.all().delete()
    print("Data lama (jika ada) berhasil dihapus.")

    for _ in range(num_schools):
        school_name = fake.company() + ' School'
        # Pastikan nama sekolah unik, jika sudah ada, coba lagi
        while School.objects.filter(name=school_name).exists():
            school_name = fake.company() + ' School'

        school = School.objects.create(
            name=school_name,
            address=fake.address(),
            city=fake.city(),
            province=fake.state(),
            contact_person=fake.name(),
            contact_email=fake.email(),
        )
        print(f"  Membuat Sekolah: {school.name}")

        for _ in range(num_students_per_school):
            gender = random.choice(['L', 'P'])
            student_first_name = fake.first_name_male() if gender == 'L' else fake.first_name_female()
            student_last_name = fake.last_name()

            # Coba membuat siswa. Jika ada UniqueTogetherConstraint, coba lagi
            # Ini penting karena kita punya unique_together di model Student
            created = False
            attempts = 0
            while not created and attempts < 10: # Batasi percobaan
                try:
                    student = Student.objects.create(
                        first_name=student_first_name,
                        last_name=student_last_name,
                        date_of_birth=fake.date_between(start_date='-18y', end_date='-6y'), # Siswa usia 6-18
                        gender=gender,
                        school=school,
                        enrollment_date=fake.date_between(start_date='-2y', end_date='today'), # Terdaftar 2 tahun terakhir
                    )
                    created = True
                except django.db.utils.IntegrityError:
                    # Jika kombinasi (first_name, last_name, date_of_birth, school) tidak unik,
                    # coba ubah nama atau tanggal lahir sedikit
                    student_first_name = fake.first_name_male() if gender == 'L' else fake.first_name_female()
                    student_last_name = fake.last_name()
                    attempts += 1
                    print(f"    Percobaan ulang membuat siswa karena duplikasi...")
            if created:
                print(f"    Membuat Siswa: {student.first_name} {student.last_name} ({school.name})")
            else:
                print(f"    Gagal membuat siswa setelah {attempts} percobaan.")


if __name__ == '__main__':
    # Memastikan pengaturan Django sudah dimuat sebelum menjalankan fungsi
    create_dummy_data(num_schools=5, num_students_per_school=20)
    print("Data dummy berhasil dibuat sepenuhnya.")
