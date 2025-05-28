// frontend/src/App.jsx

import { useState, useEffect } from 'react';
import axios from 'axios';
// IMPOR UNTUK CHART.JS
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Daftarkan komponen Chart.js yang dibutuhkan
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  // --- State Manajemen ---
  const [schools, setSchools] = useState([]);
  const [newSchool, setNewSchool] = useState({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
  const [editingSchool, setEditingSchool] = useState(null);

  const [students, setStudents] = useState([]);
  const [newStudent, setNewStudent] = useState({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
  const [editingStudent, setEditingStudent] = useState(null);

  // State untuk Data Analitik
  const [schoolAnalytics, setSchoolAnalytics] = useState([]);

  // Global State untuk Loading dan Current View
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('schools'); // Default view

  // --- Handlers dan Fetchers ---

  // School Handlers
  const fetchSchools = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/schools/');
      setSchools(response.data);
    } catch (err) {
      console.error("Error fetching schools:", err);
      setError(err);
    }
  };

  const handleSchoolChange = (e) => {
    const { name, value } = e.target;
    if (editingSchool) {
      setEditingSchool({ ...editingSchool, [name]: value });
    } else {
      setNewSchool({ ...newSchool, [name]: value });
    }
  };

  const handleAddSchool = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/api/schools/', newSchool);
      setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
      fetchSchools();
      fetchSchoolAnalytics(); // Refresh analytics after adding school
    } catch (err) {
      console.error("Error adding school:", err);
      setError(err);
    }
  };

  const handleEditSchoolClick = (school) => {
    setEditingSchool({ ...school });
    setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' }); // Clear new school form
  };

  const handleUpdateSchool = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`http://127.0.0.1:8000/api/schools/${editingSchool.id}/`, editingSchool);
      setEditingSchool(null);
      setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
      fetchSchools();
      fetchSchoolAnalytics(); // Refresh analytics after updating school
    } catch (err) {
      console.error("Error updating school:", err);
      setError(err);
    }
  };

  const handleCancelEditSchool = () => {
    setEditingSchool(null);
    setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
  };

  const handleDeleteSchool = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/schools/${id}/`);
      fetchSchools();
      fetchSchoolAnalytics(); // Refresh analytics after deleting school
    } catch (err) {
      console.error("Error deleting school:", err);
      setError(err);
    }
  };

  // Student Handlers
  const fetchStudents = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/students/');
      setStudents(response.data);
    } catch (err) {
      console.error("Error fetching students:", err);
      setError(err);
    }
  };

  const handleStudentChange = (e) => {
    const { name, value } = e.target;
    if (editingStudent) {
      setEditingStudent(prev => ({ ...prev, [name]: value }));
    } else {
      setNewStudent(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/api/students/', newStudent);
      setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
      fetchStudents();
      fetchSchoolAnalytics(); // Refresh analytics after adding student
    } catch (err) {
      console.error("Error adding student:", err);
      setError(err);
    }
  };

  const handleEditStudentClick = (student) => {
    setEditingStudent({ ...student });
    setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' }); // Clear new student form
  };

  const handleUpdateStudent = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`http://127.0.0.1:8000/api/students/${editingStudent.id}/`, editingStudent);
      setEditingStudent(null);
      setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
      fetchStudents();
      fetchSchoolAnalytics(); // Refresh analytics after updating student
    } catch (err) {
      console.error("Error updating student:", err);
      setError(err);
    }
  };

  const handleCancelEditStudent = () => {
    setEditingStudent(null);
    setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
  };

  const handleDeleteStudent = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/students/${id}/`);
      fetchStudents();
      fetchSchoolAnalytics(); // Refresh analytics after deleting student
    } catch (err) {
      console.error("Error deleting student:", err);
      setError(err);
    }
  };

  // --- School Analytics Fetcher ---
  const fetchSchoolAnalytics = async () => {
      try {
          const response = await axios.get('http://127.0.0.1:8000/api/school-analytics/');
          setSchoolAnalytics(response.data);
      } catch (err) {
          console.error("Error fetching school analytics:", err);
          setError(err);
      }
  };

  // --- useEffect untuk memuat data saat komponen mount ---
  useEffect(() => {
    const initializeData = async () => {
      setLoading(true);
      try {
        await fetchSchools();
        await fetchStudents();
        await fetchSchoolAnalytics(); // PANGGIL FUNGSI ANALITIK SAAT INISIALISASI
      } catch (e) {
        console.error("Error initializing data:", e);
        setError(e);
      } finally {
        setLoading(false);
      }
    };
    initializeData();
  }, []);

  // --- Render Komponen ---
  return (
    <div className="App" style={{ fontFamily: 'Arial, sans-serif', maxWidth: '900px', margin: '30px auto', padding: '20px', border: '1px solid #e0e0e0', borderRadius: '10px', boxShadow: '0 5px 15px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '30px' }}>Edu Insight Engine</h1>

      {/* Navigasi */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <button
          onClick={() => setCurrentView('schools')}
          style={{ ...navButtonStyle, backgroundColor: currentView === 'schools' ? '#007bff' : '#6c757d' }}
        >
          Manajemen Sekolah
        </button>
        <button
          onClick={() => setCurrentView('students')}
          style={{ ...navButtonStyle, backgroundColor: currentView === 'students' ? '#007bff' : '#6c757d' }}
        >
          Manajemen Siswa
        </button>
        <button
          onClick={() => setCurrentView('analytics')}
          style={{ ...navButtonStyle, backgroundColor: currentView === 'analytics' ? '#28a745' : '#6c757d' }}
        >
          Statistik Sekolah
        </button>
      </div>

      {/* Kondisional Render Berdasarkan currentView */}
      {loading ? (
        <p style={{ textAlign: 'center', fontSize: '18px', color: '#555' }}>Memuat data...</p>
      ) : error ? (
        <p style={{ textAlign: 'center', fontSize: '18px', color: 'red' }}>Error: {error.message}</p>
      ) : currentView === 'schools' ? (
        // --- Tampilan Manajemen Sekolah ---
        <>
          <h2 style={{ textAlign: 'center', color: '#0056b3' }}>Manajemen Sekolah</h2>
          <div style={{
            background: editingSchool ? '#fff3e0' : '#e6f7ff',
            border: `1px solid ${editingSchool ? '#ffc107' : '#91d5ff'}`,
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '30px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ textAlign: 'center', color: editingSchool ? '#e65100' : '#0056b3', marginBottom: '20px' }}>
              {editingSchool ? 'Edit Sekolah' : 'Tambah Sekolah Baru'}
            </h3>
            <form onSubmit={editingSchool ? handleUpdateSchool : handleAddSchool} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <input type="text" name="name" placeholder="Nama Sekolah"
                value={editingSchool ? editingSchool.name : newSchool.name} onChange={handleSchoolChange} required style={inputStyle} />
              <input type="text" name="address" placeholder="Alamat"
                value={editingSchool ? editingSchool.address : newSchool.address} onChange={handleSchoolChange} required style={inputStyle} />
              <input type="text" name="city" placeholder="Kota"
                value={editingSchool ? editingSchool.city : newSchool.city} onChange={handleSchoolChange} required style={inputStyle} />
              <input type="text" name="province" placeholder="Provinsi"
                value={editingSchool ? editingSchool.province : newSchool.province} onChange={handleSchoolChange} required style={inputStyle} />
              <input type="text" name="contact_person" placeholder="Nama Kontak"
                value={editingSchool ? editingSchool.contact_person : newSchool.contact_person} onChange={handleSchoolChange} required style={inputStyle} />
              <input type="email" name="contact_email" placeholder="Email Kontak"
                value={editingSchool ? editingSchool.contact_email : newSchool.contact_email} onChange={handleSchoolChange} required style={inputStyle} />
              <button type="submit" style={buttonStyle}>
                {editingSchool ? 'Perbarui Sekolah' : 'Tambah Sekolah'}
              </button>
              {editingSchool && (
                <button type="button" onClick={handleCancelEditSchool} style={{ ...buttonStyle, backgroundColor: '#dc3545', marginLeft: '10px' }}>
                  Batal Edit
                </button>
              )}
            </form>
          </div>

          {/* Daftar Sekolah */}
          {schools.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#555' }}>Tidak ada data sekolah yang ditemukan.</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {schools.map(school => (
                <li key={school.id} style={{
                  ...listItemStyle,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h4 style={{ color: '#0056b3', margin: '0 0 5px 0' }}>{school.name}</h4>
                    <p style={{ margin: '2px 0', fontSize: '0.9em' }}>{school.address}, {school.city}, {school.province}</p>
                    <p style={{ margin: '2px 0', fontSize: '0.9em' }}>{school.contact_person} ({school.contact_email})</p>
                  </div>
                  <div>
                    <button
                      onClick={() => handleEditSchoolClick(school)}
                      style={{ ...actionButtonStyle, backgroundColor: '#ffc107' }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteSchool(school.id)}
                      style={{ ...actionButtonStyle, backgroundColor: '#dc3545', marginLeft: '5px' }}
                    >
                      Hapus
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      ) : currentView === 'students' ? (
        // --- Tampilan Manajemen Siswa ---
        <>
          <h2 style={{ textAlign: 'center', color: '#0056b3' }}>Manajemen Siswa</h2>
          <div style={{
            background: editingStudent ? '#fff3e0' : '#e6f7ff',
            border: `1px solid ${editingStudent ? '#ffc107' : '#91d5ff'}`,
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '30px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ textAlign: 'center', color: editingStudent ? '#e65100' : '#0056b3', marginBottom: '20px' }}>
              {editingStudent ? 'Edit Siswa' : 'Tambah Siswa Baru'}
            </h3>
            <form onSubmit={editingStudent ? handleUpdateStudent : handleAddStudent} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <input type="text" name="first_name" placeholder="Nama Depan"
                value={editingStudent ? editingStudent.first_name : newStudent.first_name} onChange={handleStudentChange} required style={inputStyle} />
              <input type="text" name="last_name" placeholder="Nama Belakang"
                value={editingStudent ? editingStudent.last_name : newStudent.last_name} onChange={handleStudentChange} required style={inputStyle} />
              <input type="date" name="date_of_birth" placeholder="Tanggal Lahir"
                value={editingStudent ? editingStudent.date_of_birth : newStudent.date_of_birth} onChange={handleStudentChange} required style={inputStyle} />
              <select name="gender" value={editingStudent ? editingStudent.gender : newStudent.gender} onChange={handleStudentChange} required style={inputStyle}>
                <option value="">Pilih Gender</option>
                <option value="L">Laki-laki</option>
                <option value="P">Perempuan</option>
              </select>
              {/* Dropdown untuk memilih sekolah */}
              <select name="school" value={editingStudent ? editingStudent.school : newStudent.school} onChange={handleStudentChange} required style={{ ...inputStyle, gridColumn: '1 / -1' }}>
                <option value="">Pilih Sekolah</option>
                {schools.map(school => (
                  <option key={school.id} value={school.id}>
                    {school.name}
                  </option>
                ))}
              </select>
              <button type="submit" style={buttonStyle}>
                {editingStudent ? 'Perbarui Siswa' : 'Tambah Siswa'}
              </button>
              {editingStudent && (
                <button type="button" onClick={handleCancelEditStudent} style={{ ...buttonStyle, backgroundColor: '#dc3545', marginLeft: '10px' }}>
                  Batal Edit
                </button>
              )}
            </form>
          </div>

          {/* Daftar Siswa */}
          {students.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#555' }}>Tidak ada data siswa yang ditemukan.</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {students.map(student => (
                <li key={student.id} style={{
                  ...listItemStyle,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h4 style={{ color: '#0056b3', margin: '0 0 5px 0' }}>{student.first_name} {student.last_name}</h4>
                    <p style={{ margin: '2px 0', fontSize: '0.9em' }}>Tanggal Lahir: {student.date_of_birth}</p>
                    <p style={{ margin: '2px 0', fontSize: '0.9em' }}>Gender: {student.gender === 'L' ? 'Laki-laki' : 'Perempuan'}</p>
                    {/* Menampilkan nama sekolah, bukan ID */}
                    <p style={{ margin: '2px 0', fontSize: '0.9em' }}>Sekolah: {schools.find(s => s.id === student.school)?.name || 'Tidak Diketahui'}</p>
                  </div>
                  <div>
                    <button
                      onClick={() => handleEditStudentClick(student)}
                      style={{ ...actionButtonStyle, backgroundColor: '#ffc107' }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteStudent(student.id)}
                      style={{ ...actionButtonStyle, backgroundColor: '#dc3545', marginLeft: '5px' }}
                    >
                      Hapus
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      ) : currentView === 'analytics' ? ( // --- BLOK BARU INI UNTUK ANALISIS ---
        <>
          <h2 style={{ textAlign: 'center', color: '#28a745' }}>Statistik Sekolah</h2>
          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }}>
            <h3 style={{ textAlign: 'center', marginBottom: '20px', color: '#218838' }}>Jumlah Siswa per Sekolah</h3>
            {schoolAnalytics.length > 0 ? (
                <Bar
                    data={{
                        labels: schoolAnalytics.map(s => s.name),
                        datasets: [
                            {
                                label: 'Jumlah Siswa',
                                data: schoolAnalytics.map(s => s.student_count),
                                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1,
                            },
                        ],
                    }}
                    options={{
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Jumlah Siswa per Sekolah',
                            },
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                            },
                        },
                    }}
                />
            ) : (
                <p style={{ textAlign: 'center', color: '#555' }}>Tidak ada data analitik sekolah yang tersedia.</p>
            )}
          </div>

          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.1)', marginTop: '30px' }}>
            <h3 style={{ textAlign: 'center', marginBottom: '20px', color: '#218838' }}>Distribusi Gender Siswa per Sekolah</h3>
            {schoolAnalytics.length > 0 ? (
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {schoolAnalytics.map(school => (
                        <li key={school.id} style={{ ...listItemStyle, display: 'block' }}>
                            <h5 style={{ margin: '0 0 5px 0', color: '#0056b3' }}>{school.name}</h5>
                            <p style={{ margin: '2px 0' }}>Laki-laki: {school.gender_distribution.L} siswa</p>
                            <p style={{ margin: '2px 0' }}>Perempuan: {school.gender_distribution.P} siswa</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p style={{ textAlign: 'center', color: '#555' }}>Tidak ada data analitik gender yang tersedia.</p>
            )}
          </div>
        </>
      ) : (
        <p style={{ textAlign: 'center' }}>Pilih opsi di atas untuk melihat data.</p>
      )}
    </div>
  );
}

// --- Gaya (Styles) ---
// Dipindahkan ke luar komponen agar tidak dibuat ulang setiap render
const inputStyle = {
  padding: '10px',
  borderRadius: '4px',
  border: '1px solid #ccc',
  width: 'calc(100% - 22px)',
  boxSizing: 'border-box'
};
const buttonStyle = {
  gridColumn: '1 / -1',
  padding: '10px 20px',
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '16px',
  fontWeight: 'bold',
  marginTop: '10px',
};

const navButtonStyle = {
  padding: '10px 20px',
  margin: '0 5px',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  fontSize: '16px',
  fontWeight: 'bold',
  color: 'white'
};

const actionButtonStyle = {
  width: 'auto',
  padding: '8px 12px',
  fontSize: '14px',
  borderRadius: '4px',
  cursor: 'pointer',
  color: 'white',
  border: 'none',
  fontWeight: 'bold'
};
const listItemStyle = {
  background: '#f9f9f9',
  border: '1px solid #ddd',
  borderRadius: '8px',
  margin: '10px 0',
  padding: '15px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

export default App;
