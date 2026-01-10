"""
SmartRujuk+ AI Agent - Streamlit Web Application
Smart referral system with geolocation, wait time prediction, and hospital capacity analysis
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import os
from dotenv import load_dotenv

# Import local modules
from src.database import SessionLocal, init_db
from src.models import Hospital, Patient, Referral, SeverityEnum, GenderEnum, StatusEnum
from src.agent import SmartReferralAgent
from src.predictor import WaitTimePredictor, CapacityAnalyzer
from src.maps_api import GoogleMapsClient


# Page configuration
st.set_page_config(
    page_title="SmartRujuk AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load environment variables
load_dotenv()


# Custom CSS
st.markdown("""
<style>
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()
if 'agent' not in st.session_state:
    st.session_state.agent = SmartReferralAgent(st.session_state.db)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<p class="main-header">🏥 SmartRujuk AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Sistem Rujukan Otomatis dengan Geolokasi, Prediksi Waktu Tunggu, dan Analisis Kapasitas Rumah Sakit</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1E88E5/FFFFFF?text=SmartRujuk%2B", use_container_width=True)
        st.markdown("---")
        
        menu = st.selectbox(
            "Menu",
            ["🏠 Dashboard", "🚑 Rujukan Baru", "🏥 Data Rumah Sakit", "👤 Data Pasien", "📊 Analisis & Prediksi"]
        )
        
        st.markdown("---")
        st.markdown("### Tentang Sistem")
        st.info("""
        SmartRujuk+ menggunakan:
        - **AI Agent** untuk rekomendasi cerdas
        - **Machine Learning** untuk prediksi waktu tunggu
        - **Google Maps API** untuk geolokasi
        - **Dataset Kaggle** untuk data faskes (BPJS Faskes)
        - **SATUSEHAT API** untuk data pasien & rujukan
        """)
    
    # Main content based on menu selection
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "🚑 Rujukan Baru":
        show_referral_form()
    elif menu == "🏥 Data Rumah Sakit":
        show_hospitals()
    elif menu == "👤 Data Pasien":
        show_patients()
    elif menu == "📊 Analisis & Prediksi":
        show_analytics()

def show_dashboard():
    """Display dashboard"""
    st.header("Dashboard")

    db = st.session_state.db

    # Ambil data
    hospital_count = db.query(Hospital).count()
    available_hospitals = db.query(Hospital).filter(Hospital.available_beds > 0).count()
    patient_count = db.query(Patient).count()
    referral_count = db.query(Referral).count()

    # CSS untuk card tengah
    st.markdown("""
    <style>
    .dashboard-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .dashboard-card {
        background-color: #1f2937;
        padding: 20px 25px;
        border-radius: 12px;
        text-align: center;
        color: white;
        min-width: 250px;
        font-size: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .dashboard-number {
        font-size: 28px;
        font-weight: bold;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Tampilkan card tengah
    st.markdown(f"""
    <div class="dashboard-container">
        <div class="dashboard-card">
            Total Rumah Sakit
            <div class="dashboard-number">{hospital_count}</div>
        </div>
        <div class="dashboard-card">
            RS Tersedia
            <div class="dashboard-number">{available_hospitals}</div>
        </div>
        <div class="dashboard-card">
            Total Pasien
            <div class="dashboard-number">{patient_count}</div>
        </div>
        <div class="dashboard-card">
            Total Rujukan
            <div class="dashboard-number">{referral_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Judul peta
    st.markdown("<h3 style='text-align: center; margin-bottom :10px;'>Peta Rumah Sakit</h3>", unsafe_allow_html=True)

    # Menampilkan peta di tengah
    col_left, col_center, col_right = st.columns([1, 3, 1])
    with col_center:
        show_hospital_map()

    st.markdown("---")

    # Recent referrals
    st.subheader("Rujukan Terbaru")
    show_recent_referrals()



def show_referral_form():
    """Display referral form"""
    st.header("Buat Rujukan Baru")
    
    db = st.session_state.db
    agent = st.session_state.agent
    
    # Patient selection or creation
    st.subheader("Data Pasien")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Existing patient
        patients = db.query(Patient).all()
        patient_options = ["Pasien Baru"] + [f"{p.name} ({p.bpjs_number})" for p in patients]
        selected_patient = st.selectbox("Pilih Pasien", patient_options)
    
    patient_id = None
    
    if selected_patient == "Pasien Baru":
        with col2:
            st.info("Isi data pasien baru di bawah")
        
        # New patient form
        with st.form("new_patient_form"):
            bpjs_number = st.text_input("Nomor BPJS")
            name = st.text_input("Nama Lengkap")
            dob = st.date_input("Tanggal Lahir")
            gender_label = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            gender = "M" if gender_label == "Laki-laki" else "F"
            address = st.text_area("Alamat")
            phone = st.text_input("Nomor Telepon")
            
            if st.form_submit_button("Simpan Data Pasien"):
                if bpjs_number and name:
                    try:
                        new_patient = Patient(
                            bpjs_number=bpjs_number,
                            name=name,
                            date_of_birth=dob,
                            gender=GenderEnum(gender),
                            address=address,
                            phone=phone
                        )
                        db.add(new_patient)
                        db.commit()
                        db.refresh(new_patient)   # pastikan id terisi
                        patient_id = new_patient.id
                        st.success(f"Data pasien {name} berhasil disimpan (ID: {patient_id})!")
                    except Exception as e:
                        db.rollback()
                        st.error(f"Gagal menyimpan pasien: {str(e)}")
                else:
                    st.error("Nomor BPJS dan Nama harus diisi!")

    else:
        # Get existing patient
        patient_name = selected_patient.split(" (")[0]
        patient = db.query(Patient).filter(Patient.name == patient_name).first()
        if patient:
            patient_id = patient.id
            col2.success(f"Pasien: {patient.name} - BPJS: {patient.bpjs_number}")
    
    st.markdown("---")
    
    # Referral details
    st.subheader("Detail Rujukan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Location input
        st.write("**Lokasi Pasien Saat Ini**")
        location_method = st.radio("Metode Input Lokasi", ["Koordinat Manual", "Alamat"])
        
        if location_method == "Koordinat Manual":
            patient_lat = st.number_input("Latitude", value=-6.2088, format="%.6f")
            patient_lon = st.number_input("Longitude", value=106.8456, format="%.6f")
        else:
            address = st.text_input("Alamat", "Jakarta")
            if st.button("Geocode Alamat"):
                maps_client = GoogleMapsClient()
                coords = maps_client.geocode_address(address)
                if coords:
                    patient_lat, patient_lon = coords
                    st.success(f"Koordinat: {patient_lat}, {patient_lon}")
                else:
                    st.error("Gagal mengkonversi alamat")
                    patient_lat, patient_lon = -6.2088, 106.8456
    
    with col2:
        condition = st.text_area("Deskripsi Kondisi")
        severity = st.selectbox("Tingkat Keparahan", ["low", "medium", "high", "critical"])
        max_distance = st.slider("Jarak Maksimal (km)", 5, 100, 50)
    
    # Recommendation button
    if st.button("🔍 Cari Rumah Sakit Terbaik", type="primary"):
        if patient_id and condition:
            with st.spinner("Menganalisis rumah sakit terbaik..."):
                recommendation = agent.recommend_hospital(
                    patient_lat, patient_lon, severity, max_distance
                )
                
                if recommendation['success']:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Rekomendasi Rumah Sakit Ditemukan!")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display recommendation
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Rumah Sakit", recommendation['hospital_name'])
                        st.write(f"**Alamat:** {recommendation['hospital_address']}")
                    
                    with col2:
                        st.metric("Jarak", f"{recommendation['distance_km']:.2f} km")
                        st.metric("Waktu Tunggu Prediksi", f"{recommendation['predicted_wait_time']} menit")
                    
                    with col3:
                        st.metric("Tempat Tidur Tersedia", recommendation['available_beds'])
                        st.metric("Tingkat Okupansi", f"{recommendation['occupancy_rate']:.1f}%")
                    
                    # Map
                    st.subheader("Peta Lokasi")
                    m = folium.Map(
                        location=[(patient_lat + recommendation['latitude'])/2, 
                                 (patient_lon + recommendation['longitude'])/2],
                        zoom_start=12
                    )
                    
                    # Patient marker
                    folium.Marker(
                        [patient_lat, patient_lon],
                        popup="Lokasi Pasien",
                        icon=folium.Icon(color='red', icon='user')
                    ).add_to(m)
                    
                    # Hospital marker
                    folium.Marker(
                        [recommendation['latitude'], recommendation['longitude']],
                        popup=recommendation['hospital_name'],
                        icon=folium.Icon(color='green', icon='plus-sign')
                    ).add_to(m)
                    
                    # Draw line
                    folium.PolyLine(
                        [[patient_lat, patient_lon], 
                         [recommendation['latitude'], recommendation['longitude']]],
                        color='blue',
                        weight=2,
                        opacity=0.8
                    ).add_to(m)
                    
                    folium_static(m, width=800, height=400)
                    
                    # Alternative hospitals
                    if recommendation['alternatives']:
                        st.subheader("Alternatif Rumah Sakit Lain")
                        alt_df = pd.DataFrame(recommendation['alternatives'])
                        st.dataframe(alt_df, use_container_width=True)
                    
                    # Create referral button
                    if st.button("✅ Konfirmasi Rujukan"):
                        try:
                            new_referral = Referral(
                                patient_id=patient_id,
                                to_hospital_id=recommendation['hospital_id'],
                                condition_description=condition,
                                severity_level=SeverityEnum(severity),
                                predicted_wait_time=recommendation['predicted_wait_time'],
                                distance_km=recommendation['distance_km'],
                                status=StatusEnum.pending,
                                referral_date=datetime.now()
                            )
                            db.add(new_referral)
                            db.commit()
                            db.refresh(new_referral)
                            st.success("✅ Rujukan berhasil dibuat dan disimpan ke database!")
                            st.info(f"📋 Rujukan ID: {new_referral.id} | Status: {new_referral.status.value}")
                            st.session_state['last_referral_id'] = new_referral.id
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"❌ Gagal membuat rujukan: {str(e)}")
                else:
                    st.error(recommendation['message'])
        else:
            st.warning("Pastikan data pasien dan kondisi sudah diisi!")

def show_hospitals():
    """Display hospitals data with pagination and filtering"""
    st.header("Data Rumah Sakit")
    
    db = st.session_state.db
    
    # Add new hospital
    with st.expander("➕ Tambah Rumah Sakit Baru"):
        with st.form("new_hospital_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nama Rumah Sakit")
                address = st.text_area("Alamat")
                latitude = st.number_input("Latitude", format="%.6f")
                longitude = st.number_input("Longitude", format="%.6f")
            
            with col2:
                hospital_type = st.text_input("Tipe", value="Umum")
                hospital_class = st.selectbox("Kelas", ["A", "B", "C", "D"])
                total_beds = st.number_input("Total Tempat Tidur", min_value=0, value=100)
                available_beds = st.number_input("Tempat Tidur Tersedia", min_value=0, value=50)
                phone = st.text_input("Telepon")
                emergency = st.checkbox("IGD Tersedia", value=True)
            
            if st.form_submit_button("Simpan"):
                if name and address:
                    new_hospital = Hospital(
                        name=name,
                        address=address,
                        latitude=latitude,
                        longitude=longitude,
                        type=hospital_type,
                        class_=hospital_class,
                        total_beds=total_beds,
                        available_beds=available_beds,
                        phone=phone,
                        emergency_available=emergency
                    )
                    db.add(new_hospital)
                    db.commit()
                    st.success(f"Rumah Sakit {name} berhasil ditambahkan!")
                    st.rerun()
    
    st.markdown("---")
    
    # Filters and Search
    st.subheader("🔍 Filter & Pencarian")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_query = st.text_input("Cari Nama RS", placeholder="Ketik nama rumah sakit...")
    
    with col2:
        # Get unique hospital classes from database
        all_classes = db.query(Hospital.class_).distinct().all()
        class_options = ["Semua"] + [c[0] for c in all_classes if c[0]]
        filter_class = st.selectbox("Filter Kelas", class_options)
    
    with col3:
        filter_emergency = st.selectbox("IGD", ["Semua", "Tersedia", "Tidak Tersedia"])
    
    with col4:
        filter_availability = st.selectbox("Ketersediaan Bed", ["Semua", "Tersedia (>0)", "Penuh (=0)"])
    
    # Build query with filters
    query = db.query(Hospital)
    
    # Apply search filter
    if search_query:
        query = query.filter(Hospital.name.contains(search_query))
    
    # Apply class filter
    if filter_class != "Semua":
        query = query.filter(Hospital.class_ == filter_class)
    
    # Apply emergency filter
    if filter_emergency == "Tersedia":
        query = query.filter(Hospital.emergency_available == True)
    elif filter_emergency == "Tidak Tersedia":
        query = query.filter(Hospital.emergency_available == False)
    
    # Apply availability filter
    if filter_availability == "Tersedia (>0)":
        query = query.filter(Hospital.available_beds > 0)
    elif filter_availability == "Penuh (=0)":
        query = query.filter(Hospital.available_beds == 0)
    
    # Get total count for pagination
    total_hospitals = query.count()
    
    # Pagination settings
    items_per_page = 50
    total_pages = (total_hospitals + items_per_page - 1) // items_per_page
    
    # Initialize page number in session state
    if 'hospital_page' not in st.session_state:
        st.session_state.hospital_page = 1
    
    st.markdown("---")
    
    # Display total count
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"📊 Menampilkan **{total_hospitals}** rumah sakit")
    with col2:
        if total_hospitals > 0:
            st.write(f"Halaman {st.session_state.hospital_page} dari {total_pages}")
    
    if total_hospitals > 0:
        # Apply pagination
        offset = (st.session_state.hospital_page - 1) * items_per_page
        hospitals = query.offset(offset).limit(items_per_page).all()
        
        # Create DataFrame
        hospital_data = []
        for h in hospitals:
            hospital_data.append({
                'ID': h.id,
                'Nama': h.name,
                'Alamat': h.address[:50] + '...' if len(h.address) > 50 else h.address,
                'Kelas': h.class_ if h.class_ else '-',
                'Total Beds': h.total_beds,
                'Tersedia': h.available_beds,
                'Okupansi': f"{((h.total_beds - h.available_beds) / h.total_beds * 100):.1f}%" if h.total_beds > 0 else "0%",
                'IGD': '✅' if h.emergency_available else '❌'
            })
        
        df = pd.DataFrame(hospital_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Pagination controls
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ Pertama", disabled=(st.session_state.hospital_page == 1)):
                    st.session_state.hospital_page = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Sebelumnya", disabled=(st.session_state.hospital_page == 1)):
                    st.session_state.hospital_page -= 1
                    st.rerun()
            
            with col3:
                # Page selector
                page_options = list(range(1, total_pages + 1))
                selected_page = st.selectbox(
                    "Pilih Halaman",
                    page_options,
                    index=st.session_state.hospital_page - 1,
                    label_visibility="collapsed"
                )
                if selected_page != st.session_state.hospital_page:
                    st.session_state.hospital_page = selected_page
                    st.rerun()
            
            with col4:
                if st.button("Selanjutnya ▶️", disabled=(st.session_state.hospital_page == total_pages)):
                    st.session_state.hospital_page += 1
                    st.rerun()
            
            with col5:
                if st.button("Terakhir ⏭️", disabled=(st.session_state.hospital_page == total_pages)):
                    st.session_state.hospital_page = total_pages
                    st.rerun()
    else:
        st.info("Tidak ada rumah sakit yang sesuai dengan filter. Silakan ubah filter atau tambahkan data baru.")

def show_patients():
    """Display patients data"""
    st.header("Data Pasien")
    
    db = st.session_state.db
    
    patients = db.query(Patient).all()
    
    if patients:
        patient_data = []
        for p in patients:
            patient_data.append({
                'ID': p.id,
                'BPJS': p.bpjs_number,
                'Nama': p.name,
                'Tanggal Lahir': p.date_of_birth.strftime('%Y-%m-%d') if p.date_of_birth else '-',
                'Jenis Kelamin': p.gender.value,
                'Telepon': p.phone or '-'
            })
        
        df = pd.DataFrame(patient_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data pasien.")

def show_analytics():
    """Display analytics and predictions"""
    st.header("Analisis & Prediksi")
    
    db = st.session_state.db
    analyzer = CapacityAnalyzer()
    predictor = st.session_state.agent.wait_time_predictor
    
    # Train predictor if not trained
    if not predictor.is_trained:
        with st.spinner("Training prediction model..."):
            predictor.train(db)
    
    tab1, tab2, tab3 = st.tabs(["Kapasitas RS", "Prediksi Waktu Tunggu", "Statistik Rujukan"])
    
    with tab1:
        st.subheader("Analisis Kapasitas Rumah Sakit")
        
        hospitals = db.query(Hospital).all()
        
        if hospitals:
            capacity_data = []
            for h in hospitals:
                capacity = analyzer.analyze_hospital_capacity(db, h.id)
                capacity_data.append({
                    'Rumah Sakit': h.name,
                    'Status': capacity['status'],
                    'Tersedia': capacity['available_beds'],
                    'Total': capacity['total_beds'],
                    'Okupansi': f"{capacity['occupancy_rate']}%"
                })
            
            df = pd.DataFrame(capacity_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data rumah sakit")
    
    with tab2:
        st.subheader("Prediksi Waktu Tunggu")
        
        hospitals = db.query(Hospital).all()
        
        if hospitals:
            hospital_names = [h.name for h in hospitals]
            selected_hospital = st.selectbox("Pilih Rumah Sakit", hospital_names)
            
            hospital = next(h for h in hospitals if h.name == selected_hospital)
            
            st.write("**Prediksi waktu tunggu berdasarkan tingkat keparahan:**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                low_time = predictor.predict_wait_time(hospital.id, 'low')
                st.metric("Ringan", f"{low_time} menit")
            
            with col2:
                medium_time = predictor.predict_wait_time(hospital.id, 'medium')
                st.metric("Sedang", f"{medium_time} menit")
            
            with col3:
                high_time = predictor.predict_wait_time(hospital.id, 'high')
                st.metric("Berat", f"{high_time} menit")
            
            with col4:
                critical_time = predictor.predict_wait_time(hospital.id, 'critical')
                st.metric("Kritis", f"{critical_time} menit")
        else:
            st.info("Tidak ada data rumah sakit")
    
    with tab3:
        st.subheader("Statistik Rujukan")
        
        # Check for newly created referral
        if 'last_referral_id' in st.session_state:
            st.success(f"✅ Rujukan terbaru berhasil ditambahkan (ID: {st.session_state['last_referral_id']})")
            del st.session_state['last_referral_id']
        
        referrals = db.query(Referral).all()
        
        if referrals:
            # Total rujukan
            total_referrals = len(referrals)
            st.info(f"📊 Total Rujukan: {total_referrals}")
            
            # Status distribution
            status_counts = {}
            for r in referrals:
                status = r.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            st.write("**Distribusi Status Rujukan:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Pending", status_counts.get('pending', 0))
            with col2:
                st.metric("Accepted", status_counts.get('accepted', 0))
            with col3:
                st.metric("Rejected", status_counts.get('rejected', 0))
            with col4:
                st.metric("Completed", status_counts.get('completed', 0))
            
            # Recent referrals table
            st.write("**Rujukan Terbaru:**")
            recent_referrals = db.query(Referral).order_by(Referral.referral_date.desc()).limit(10).all()
            
            referral_data = []
            for r in recent_referrals:
                patient = db.query(Patient).filter(Patient.id == r.patient_id).first()
                hospital = db.query(Hospital).filter(Hospital.id == r.to_hospital_id).first()
                
                referral_data.append({
                    'ID': r.id,
                    'Pasien': patient.name if patient else 'Unknown',
                    'Rumah Sakit': hospital.name if hospital else 'Unknown',
                    'Tingkat Keparahan': r.severity_level.value,
                    'Status': r.status.value,
                    'Tanggal': r.referral_date.strftime('%Y-%m-%d %H:%M') if r.referral_date else 'N/A'
                })
            
            df = pd.DataFrame(referral_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data rujukan")

def show_hospital_map(max_markers=100):
    """Display map with limited hospitals to avoid API quota issues"""
    db = st.session_state.db
    
    # Limit to max_markers hospitals to avoid Google Maps API quota issues
    hospitals = db.query(Hospital).limit(max_markers).all()
    
    if hospitals:
        # Center of Indonesia
        m = folium.Map(location=[-2.5, 118.0], zoom_start=5)
        
        marker_count = 0
        for hospital in hospitals:
            # Color based on availability
            if hospital.available_beds > 20:
                color = 'green'
            elif hospital.available_beds > 10:
                color = 'orange'
            else:
                color = 'red'
            
            folium.Marker(
                [hospital.latitude, hospital.longitude],
                popup=f"<b>{hospital.name}</b><br>Tersedia: {hospital.available_beds} beds",
                icon=folium.Icon(color=color, icon='plus-sign')
            ).add_to(m)
            marker_count += 1
        
        folium_static(m, width=1400, height=550)
        
        # Show info about limited display
        total_hospitals = db.query(Hospital).count()
        if total_hospitals > max_markers:
            st.info(f"ℹ️ Menampilkan {marker_count} dari {total_hospitals} rumah sakit di peta untuk menghemat quota API. Gunakan menu 'Data Rumah Sakit' untuk melihat semua data.")
    else:
        st.info("Belum ada data rumah sakit untuk ditampilkan di peta")

def show_recent_referrals():
    """Display recent referrals"""
    db = st.session_state.db
    referrals = db.query(Referral).order_by(Referral.referral_date.desc()).limit(10).all()
    
    if referrals:
        referral_data = []
        for r in referrals:
            patient = db.query(Patient).filter(Patient.id == r.patient_id).first()
            hospital = db.query(Hospital).filter(Hospital.id == r.to_hospital_id).first()
            
            referral_data.append({
                'Tanggal': r.referral_date.strftime('%Y-%m-%d %H:%M') if r.referral_date else '-',
                'Pasien': patient.name if patient else '-',
                'Rumah Sakit': hospital.name if hospital else '-',
                'Keparahan': r.severity_level.value,
                'Status': r.status.value,
                'Jarak': f"{r.distance_km:.2f} km" if r.distance_km else '-'
            })
        
        df = pd.DataFrame(referral_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data rujukan")

if __name__ == "__main__":
    main()
