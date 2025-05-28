// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  // State untuk Schools
  const [schools, setSchools] = useState([]);
  const [newSchool, setNewSchool] = useState({
    name: '', address: '', city: '', province: '', contact_person: '', contact_email: ''
  });
  const [editingSchool, setEditingSchool] = useState(null);

  // State untuk Students
  const [students, setStudents] = useState([]);
  const [newStudent, setNewStudent] = useState({
    first_name: '', last_name: '', date_of_birth: '', gender: '', school: ''
  });
  const [editingStudent, setEditingStudent] = useState(null);

  // Global State untuk Loading, Error, dan Current View
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('schools'); // 'schools' or 'students'

  // --- Fungsi-fungsi untuk Schools ---

  const fetchSchools = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:8000/api/schools/');
      setSchools(response.data);
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
      console.error("Error fetching schools:", err);
      if (err.request) {
        alert("Koneksi ke backend gagal. Pastikan server Django berjalan di port 8000 dan tidak ada masalah CORS. Periksa console browser Anda!");
      }
    }
  };

  const handleSchoolChange = (e) => {
    const { name, value } = e.target;
    if (editingSchool) {
      setEditingSchool(prevSchool => ({ ...prevSchool, [name]: value }));
    } else {
      setNewSchool(prevSchool => ({ ...prevSchool, [name]: value }));
    }
  };

  const handleAddSchool = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/schools/', newSchool);
      setSchools(prevSchools => [...prevSchools, response.data]);
      setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
      alert('Sekolah berhasil ditambahkan!');
    } catch (err) {
      console.error("Error adding school:", err.response ? err.response.data : err.message);
      alert('Gagal menambahkan sekolah. Periksa console untuk detail.');
    }
  };

  const handleEditSchoolClick = (school) => {
    setEditingSchool(school);
    setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' }); // Clear new form
  };

  const handleUpdateSchool = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`http://127.0.0.1:8000/api/schools/${editingSchool.id}/`, editingSchool);
      setSchools(prevSchools => prevSchools.map(school =>
        school.id === editingSchool.id ? response.data : school
      ));
      setEditingSchool(null);
      alert('Sekolah berhasil diperbarui!');
    } catch (err) {
      console.error("Error updating school:", err.response ? err.response.data : err.message);
      alert('Gagal memperbarui sekolah. Periksa console untuk detail.');
    }
  };

  const handleDeleteSchool = async (id) => {
    if (window.confirm('Apakah Anda yakin ingin menghapus sekolah ini? Semua siswa di sekolah ini juga akan terhapus.')) {
      try {
        await axios.delete(`http://127.0.0.1:8000/api/schools/${id}/`);
        setSchools(prevSchools => prevSchools.filter(school => school.id !== id));
        // Juga hapus siswa yang terkait dari state lokal
        setStudents(prevStudents => prevStudents.filter(student => student.school !== id));
        if (editingSchool && editingSchool.id === id) {
          setEditingSchool(null);
          setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
        }
        alert('Sekolah berhasil dihapus!');
      } catch (err) {
        console.error("Error deleting school:", err.response ? err.response.data : err.message);
        alert('Gagal menghapus sekolah. Periksa console untuk detail.');
      }
    }
  };

  const handleCancelEditSchool = () => {
    setEditingSchool(null);
    setNewSchool({ name: '', address: '', city: '', province: '', contact_person: '', contact_email: '' });
  };

  // --- Fungsi-fungsi untuk Students ---

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:8000/api/students/');
      setStudents(response.data);
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
      console.error("Error fetching students:", err);
      if (err.request) {
        alert("Koneksi ke backend gagal. Pastikan server Django berjalan di port 8000 dan tidak ada masalah CORS. Periksa console browser Anda!");
      }
    }
  };

  const handleStudentChange = (e) => {
    const { name, value } = e.target;
    if (editingStudent) {
      setEditingStudent(prevStudent => ({ ...prevStudent, [name]: value }));
    } else {
      setNewStudent(prevStudent => ({ ...prevStudent, [name]: value }));
    }
  };

  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      // Pastikan school ID ada dan valid
      if (!newStudent.school) {
          alert("Mohon pilih sekolah untuk siswa.");
          return;
      }
      const response = await axios.post('http://127.0.0.1:8000/api/students/', newStudent);
      setStudents(prevStudents => [...prevStudents, response.data]);
      setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
      alert('Siswa berhasil ditambahkan!');
    } catch (err) {
      console.error("Error adding student:", err.response ? err.response.data : err.message);
      alert('Gagal menambahkan siswa. Pastikan semua field terisi dan ID Sekolah valid. Periksa console untuk detail.');
    }
  };

  const handleEditStudentClick = (student) => {
    setEditingStudent(student);
    setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' }); // Clear new form
  };

  const handleUpdateStudent = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`http://127.0.0.1:8000/api/students/${editingStudent.id}/`, editingStudent);
      setStudents(prevStudents => prevStudents.map(student =>
        student.id === editingStudent.id ? response.data : student
      ));
      setEditingStudent(null);
      alert('Siswa berhasil diperbarui!');
    } catch (err) {
      console.error("Error updating student:", err.response ? err.response.data : err.message);
      alert('Gagal memperbarui siswa. Periksa console untuk detail.');
    }
  };

  const handleDeleteStudent = async (id) => {
    if (window.confirm('Apakah Anda yakin ingin menghapus siswa ini?')) {
      try {
        await axios.delete(`http://127.0.0.1:8000/api/students/${id}/`);
        setStudents(prevStudents => prevStudents.filter(student => student.id !== id));
        if (editingStudent && editingStudent.id === id) {
          setEditingStudent(null);
          setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
        }
        alert('Siswa berhasil dihapus!');
      } catch (err) {
        console.error("Error deleting student:", err.response ? err.response.data : err.message);
        alert('Gagal menghapus siswa. Periksa console untuk detail.');
      }
    }
  };

  const handleCancelEditStudent = () => {
    setEditingStudent(null);
    setNewStudent({ first_name: '', last_name: '', date_of_birth: '', gender: '', school: '' });
  };

  // --- UseEffect untuk memuat data berdasarkan currentView ---
  useEffect(() => {
    // Saat komponen dimuat atau currentView berubah, kita ambil data yang relevan
    // Pastikan kedua data (sekolah dan siswa) diambil agar dropdown sekolah selalu tersedia
    const initializeData = async () => {
        setLoading(true);
        try {
            await fetchSchools(); // Selalu ambil sekolah
            await fetchStudents(); // Selalu ambil siswa
        } catch (e) {
            console.error("Error initializing data:", e);
            // Error handling sudah ada di masing-masing fetch function
        } finally {
            setLoading(false);
        }
    };
    initializeData();
  }, []); // Hanya berjalan sekali saat komponen mount

  // --- Tampilan Loading/Error Global ---
  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Memuat data...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red', marginTop: '50px' }}>Terjadi Kesalahan: {error.message}. Silakan periksa console browser Anda untuk detail (misalnya, masalah CORS).</div>;
  }

  // --- Render Aplikasi ---
  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: 'auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Edu Insight Engine Dashboard</h1>

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
      </div>

      {/* Kondisional Render Berdasarkan currentView */}
      {currentView === 'schools' ? (
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
      ) : (
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

const listItemStyle = { // Ini yang tadi terlewat!
  background: '#f9f9f9',
  border: '1px solid #ddd',
  borderRadius: '8px',
  margin: '10px 0',
  padding: '15px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

export default App;
