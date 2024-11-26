import streamlit as st
import pandas as pd
import pickle
from streamlit_option_menu import option_menu
import mysql.connector
import plotly.express as px

model = pickle.load(open('data/model.pkl', 'rb'))

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'rawan_db'
)

mycursor = mydb.cursor()
print('Connection Established')

hidden ='''
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        '''

st.markdown(hidden, unsafe_allow_html=True)

def main():
    st.write('')
    
    
if 'login' not in st.session_state:
    st.session_state.login = False

selected = option_menu(
    menu_title=None,
    options=["Login","Beranda","Input Form"],
    menu_icon= "cast",
    default_index=0,
    orientation="horizontal"
)   

if selected == 'Login':
    pilihan = st.sidebar.selectbox('Login/Signup', ['Login', 'Signup'])

    if pilihan == 'Login':
        st.subheader('Silakan login dulu')
        username = st.text_input('Username')
        password = st.text_input('Password', type= 'password')
        if st.button('Login'):
            sql = "select * FROM user where username = %s"
            val = (username,)
            mycursor.execute(sql, val)  
        
             
            result = mycursor.fetchone()  
            
            if result:
                user_id, db_username, db_password = result[0], result[1], result[2]
                
                if password == db_password:
                    st.session_state.login = True
                    st.session_state['user'] = result 
                    
                    st.success("Login berhasil!!")
                else:
                    st.error('Login gagal: Salah password')
            else:
                st.error('Login gagal: Username tidak ditemukan')
        
        if st.button('Logout', key='logout'):
            st.session_state.login = False
            st.success('Terima kasih sudah menggunakan website ini!')
            

    if pilihan == "Signup":
        st.subheader('Silakan daftar dulu')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Signup'):
            sql = 'insert into user(username, passsword) values(%s,%s)'
            val = (username, password)
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Akun berhasil dibuat")   

if selected == "Input Form":
    if 'tingkat' not in st.session_state:
        st.session_state['tingkat'] = None

    if st.session_state['login'] == True:
        st.subheader('Prediksi Kerawanan Jalan')

        option = st.sidebar.selectbox("Pilih", ['Input', 'Data', 'Hapus'])

        if option == 'Input':
            st.write('Penginputan kondisi jalan')
            provinsi = st.selectbox('Provinsi', ['Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi', 'Sumatera Selatan', 'Bengkulu', 'Lampung', 'Kep. Bangka Belitung', 'Kep. Riau', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'Jawa Timur', 'D.I. Yogyakarta', 'Banten', 'Bali', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur', 'Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara', 'Sulawesi Utara','Sulawesi Tengah','Sulawesi Selatan','Sulawesi Tenggara', 'Gorontalo', 'Sulawesi Barat', 'Maluku', 'Maluku Utara', 'Papua Barat', 'Papua'], placeholder='Pilih Provinsi')
            provinsi = str(provinsi)
            tahun = st.text_input('Tahun')
            baik = st.number_input('Baik (km)', placeholder='km')
            sedang = st.number_input('Sedang (km)',placeholder='km')
            rusak = st.number_input('Rusak (km)',placeholder='km')
            rusak_berat = st.number_input('Rusak Berat (km)', placeholder='km')

            sum_km = baik + sedang + rusak + rusak_berat
            jumlah_km = st.number_input('Jumlah Kilometer (km)', value=sum_km, disabled=True)

            mobil = st.number_input('Mobil')
            bis = st.number_input('Bis')
            truk = st.number_input('Truk')
            sepeda_motor = st.number_input('Sepeda Motor')

            sum_kend = mobil + bis + truk + sepeda_motor
            jumlah_kend = st.number_input('Jumlah Kendaraan', value=sum_kend, disabled=True)

            jumlah_kecelakaan = st.number_input('Jumlah Kecelakaan')

            if st.button('Hasil'):
                hasil = model.predict([[baik, sedang, rusak, rusak_berat, jumlah_km, mobil, bis, truk, sepeda_motor, jumlah_kend, jumlah_kecelakaan]]) 
                if hasil[0] == 0:
                    st.session_state['tingkat'] = 'rendah'
                else: 
                    st.session_state['tingkat'] = 'tinggi'
                
                st.write(f'Tingkat kerawanan di provinsi {provinsi} {st.session_state["tingkat"]}')

            if st.session_state['tingkat'] is not None:
                tingkat = str(st.session_state['tingkat'])

            if st.button('Submit'):
                if st.session_state['tingkat'] is None:
                    st.warning("Silakan klik tombol 'Hasil' terlebih dahulu untuk mendapatkan prediksi.")
                else:
                    sql = """
                        INSERT INTO datalengkap (provinsi, tahun, baik, sedang, rusak, rusak_berat, jumlah_km, mobil, bis, truk, sepeda_motor, jumlah_kend, jumlah_kec, kerawanan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (provinsi, tahun, baik, sedang, rusak, rusak_berat, jumlah_km, mobil, bis, truk, sepeda_motor, jumlah_kend, jumlah_kecelakaan, tingkat)
                    mycursor.execute(sql, val)
                    mydb.commit()  
                    st.success("Data berhasil disimpan")

        if option == 'Data':
            st.subheader('Data')
            mycursor.execute('SELECT * FROM datalengkap')
            df = mycursor.fetchall()
            data = pd.DataFrame(df, columns=['No','Provinsi', 'Tahun', 'Baik', 'Sedang', 'Rusak', 'Rusak Berat', 'Jumlah Kilometer', 'Mobil','Bis','Truk','Sepeda Motor', 'Jumlah Kendaraan', 'Jumlah Kecelakaan', 'Tingkat Kerawanan'])
            st.write(data)

        if option == 'Hapus':
            mycursor.execute('SELECT * FROM datalengkap')
            df = mycursor.fetchall()
            data = pd.DataFrame(df, columns=['No','Provinsi', 'Tahun', 'Baik', 'Sedang', 'Rusak', 'Rusak Berat', 'Jumlah Kilometer', 'Mobil','Bis','Truk','Sepeda Motor', 'Jumlah Kendaraan', 'Jumlah Kecelakaan', 'Tingkat Kerawanan'])

            provinsi = st.selectbox("Provinsi", data['Provinsi'].unique())
            tahun = st.selectbox('Tahun', data['Tahun'].unique())
            if st.button('Hapus'):
                sql = "delete from datalengkap where provinsi=%s and tahun=%s"
                val = (provinsi, tahun,)
                mycursor.execute(sql,val)
                mydb.commit()
                st.success('Data berhasil dihapus')
            
    else:
        st.subheader('Mohon untuk login terlebih dahulu')

if selected == 'Beranda':
    mycursor.execute('SELECT * FROM datalengkap')
    df = mycursor.fetchall()
    data = pd.DataFrame(df, columns=['No','Provinsi', 'Tahun', 'Baik', 'Sedang', 'Rusak', 'Rusak Berat', 'Jumlah Kilometer', 'Mobil','Bis','Truk','Sepeda Motor', 'Jumlah Kendaraan', 'Jumlah Kecelakaan', 'Tingkat Kerawanan'])

    st.header('Rawan')
    st.subheader('Website Prediksi Tingkat Kerawanan Jalan')

    provinsi_pilihan = st.selectbox('Pilih Provinsi', data['Provinsi'].unique())

    df_provinsi = data[data['Provinsi'] == provinsi_pilihan]
    df_provinsi_sorted = df_provinsi.sort_values(by='Tahun')

    option = st.sidebar.selectbox("Pilih", ['Text', 'Grafik'])

    if option == 'Text':
        if not df_provinsi.empty:
            st.write(f"Provinsi {provinsi_pilihan}:")

            cols = st.columns(len(df_provinsi))
            
            for i, (index, row) in enumerate(df_provinsi.iterrows()):
                with cols[i]:
                    st.write(f"### Tahun: {row['Tahun']}")
                    st.write(f"- Kondisi Jalan Baik: {row['Baik']} km")
                    st.write(f"- Kondisi Jalan Sedang: {row['Sedang']} km")
                    st.write(f"- Kondisi Jalan Rusak: {row['Rusak']} km")
                    st.write(f"- Kondisi Jalan Rusak Berat: {row['Rusak Berat']} km")
                    st.write(f"- Jumlah Kilometer: {row['Jumlah Kilometer']} km")
                    st.write(f"- Jumlah Kendaraan: {row['Jumlah Kendaraan']}")
                    st.write(f"- Jumlah Kecelakaan: {row['Jumlah Kecelakaan']}")
                    st.write(f"- Tingkat Kerawanan: {row['Tingkat Kerawanan']}")
            

            st.write("### Perbandingan:")
            
            if len(df_provinsi) > 1:

                for i in range(1, len(df_provinsi_sorted)):
                    current_year = df_provinsi_sorted.iloc[i]
                    previous_year = df_provinsi_sorted.iloc[i - 1]
                    
                    st.write(f"#### {previous_year['Tahun']} vs {current_year['Tahun']}")
                    
                    if current_year['Baik'] == previous_year['Baik']:
                        st.write(f"- *Kondisi Jalan Baik**: {previous_year['Baik']} km ➡ {current_year['Baik']} km (Tidak ada perubahan)")
                    else:
                        st.write(f"- **Kondisi Jalan Baik**: {previous_year['Baik']} km ➡ {current_year['Baik']} km "
                                f"({'Membaik' if current_year['Baik'] > previous_year['Baik'] else 'Memburuk'})")

                    if current_year['Sedang'] == previous_year['Sedang']:
                        st.write(f"- **Kondisi Jalan Sedang**: {previous_year['Sedang']} km ➡ {current_year['Sedang']} km (Tidak ada perubahan)")
                    else:
                        st.write(f"- **Kondisi Jalan Sedang**: {previous_year['Sedang']} km ➡ {current_year['Sedang']} km "
                                f"({'Membaik' if current_year['Sedang'] < previous_year['Sedang'] else 'Memburuk'})")
                        
                    if current_year['Rusak'] == previous_year['Rusak']:
                        st.write(f"- **Kondisi Jalan Rusak**: {previous_year['Rusak']} km ➡ {current_year['Rusak']} km (Tidak ada perubahan)")
                    else:
                        st.write(f"- **Kondisi Jalan Rusak**: {previous_year['Rusak']} km ➡ {current_year['Rusak']} km "
                                f"({'Membaik' if current_year['Rusak'] < previous_year['Rusak'] else 'Memburuk'})")

                    if current_year['Rusak Berat'] == previous_year['Rusak Berat']:
                        st.write(f"- **Kondisi Jalan Rusak Berat**: {previous_year['Rusak Berat']} km ➡ {current_year['Rusak Berat']} km (Tidak ada perubahan)")
                    else:
                        st.write(f"- **Kondisi Jalan Rusak Berat**: {previous_year['Rusak Berat']} km ➡ {current_year['Rusak Berat']} km "
                                f"({'Membaik' if current_year['Rusak Berat'] < previous_year['Rusak Berat'] else 'Memburuk'})")
                        
                    if current_year['Jumlah Kecelakaan'] == previous_year['Jumlah Kecelakaan']:
                        st.write(f"- **Jumlah Kecelakaan**: {previous_year['Jumlah Kecelakaan']} ➡ {current_year['Jumlah Kecelakaan']} (Tidak ada perubahan)")
                    else:
                        st.write(f"- **Jumlah Kecelakaan**: {previous_year['Jumlah Kecelakaan']} ➡ {current_year['Jumlah Kecelakaan']}"
                                f"({'Membaik' if current_year['Jumlah Kecelakaan'] < previous_year['Jumlah Kecelakaan'] else 'Memburuk'})")
                        
                    st.write(f"- **Tingkat Kerawanan**: {previous_year['Tingkat Kerawanan']} ➡ {current_year['Tingkat Kerawanan']}")
                    
            else:
                st.write("Data tidak cukup untuk melakukan perbandingan")

    if option == 'Grafik':
        if not df_provinsi.empty:
            st.write(f"Provinsi {provinsi_pilihan}:")

            if len(df_provinsi) > 1:
                st.write("### Grafik Perubahan Kondisi Jalan dan Jumlah Kecelakaan")

                fig = px.line(df_provinsi_sorted, x='Tahun', y=['Baik', 'Sedang', 'Rusak', 'Rusak Berat'],
                            labels={'value': 'Kilometer', 'Tahun': 'Tahun'},
                            title=f'Perubahan Kondisi Jalan di {provinsi_pilihan}')
                st.plotly_chart(fig)

                fig2 = px.line(df_provinsi_sorted, x='Tahun', y='Jumlah Kecelakaan',
                            labels={'Jumlah Kecelakaan': 'Jumlah Kecelakaan', 'Tahun': 'Tahun'},
                            title=f'Perubahan Jumlah Kecelakaan di {provinsi_pilihan}')
                st.plotly_chart(fig2)
                    
            else:
                st.write("Data tidak cukup untuk melakukan perbandingan")
    
if __name__== '__main__':
    main()
        
        




        






