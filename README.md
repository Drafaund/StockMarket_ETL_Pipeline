# Stock Market and Sentiment Analysis
Repositori ini berisi file dan konfigurasi yang diperlukan untuk menyiapkan saluran ETL (Ekstrak, Transformasi, Muat) end-to-end untuk menganalisis data pasar saham dan sentimen berita.
- Link blog: https://automatic-carol-0a8.notion.site/Analisis-Hubungan-Harga-Saham-dan-Sentimen-Berita-14333084e14c80c8b3f6c14659db5ad4?pvs=4
- Link video: https://youtu.be/Ut4i2O9xIQI

## Struktur Folder
Repositori ini terdiri dari folder dan file berikut:

1. **config**: Folder ini berisi file konfigurasi untuk saluran ETL.
2. **dags**: Folder ini berisi DAG (Directed Acyclic Graph) Airflow yang mendefinisikan alur kerja dan penjadwalan proses ETL.
3. **ETL_env**: Folder ini berisi file konfigurasi lingkungan untuk proses ETL.
4. **logs**: Folder ini menyimpan log yang dihasilkan selama eksekusi saluran ETL.
5. **plugins**: Folder ini berisi plugin atau ekstensi kustom yang digunakan dalam pengaturan Airflow.
6. `.dockerignore`: File yang menentukan file dan direktori yang harus diabaikan saat membangun gambar Docker.
7. `.gitignore`: File yang menentukan file dan direktori yang harus diabaikan oleh Git.
8. `docker-compose.yaml`: File Docker Compose yang mendefinisikan layanan dan kontainer untuk saluran ETL.
9. `README.md`: File ini, yang menyediakan dokumentasi untuk proyek ini.
10. `requirements.txt`: File yang mencantumkan dependensi Python yang diperlukan untuk saluran ETL.

## Requirements
Sebelum Anda dapat menyiapkan saluran ETL, pastikan Anda memiliki perangkat berikut terinstal di sistem Anda:

- Docker
- Docker Compose
- Python 3.x

## Getting Started
1. Klon repositori:
   ```
   git clone https://github.com/your-username/stockmarket-etl-pipeline.git
   ```
2. Navigasi ke direktori proyek:
   ```
   cd stockmarket-etl-pipeline
   ```
3. Buat dan jalankan kontainer Docker menggunakan Docker Compose:
   ```
   docker-compose up -d
   ```
   Ini akan memulai penjadwal Airflow, server web, dan layanan lain yang diperlukan.
4. Akses UI web Airflow dengan membuka browser web dan navigasi ke `http://localhost:8080`. Anda harus melihat DAG yang didefinisikan dalam folder `dags`.
5. Jalankan saluran ETL dengan menonaktifkan jeda dan menjalankan DAG yang diinginkan.

## Konfigurasi
File konfigurasi untuk saluran ETL terletak di folder `.env`. Anda dapat menyesuaikan pengaturan berikut:

- **Kunci API Alpha Vantage**: Kunci API untuk mengakses API data saham Alpha Vantage.
- **Kunci API Berita**: Kunci API untuk mengakses API data berita.
- **Detail koneksi PostgreSQL**: Anda dapat langsung menghubungkan basis data Anda dengan Airflow di bagian Admin.

Perbarui file konfigurasi yang sesuai dengan kunci API dan kredensial basis data Anda sendiri.

## DAG Airflow
DAG Airflow yang mendefinisikan alur kerja ETL terletak di folder `dags`. Setiap DAG mewakili aspek tertentu dari saluran, seperti:

- Mengekstrak data saham dari Alpha Vantage
- Mengekstrak data berita dari API berita atau web scraping
- Mentransformasi dan memproses data
- Memuat data yang diproses ke dalam basis data PostgreSQL

Anda dapat menyesuaikan DAG untuk memenuhi kebutuhan spesifik Anda, seperti menambahkan sumber data tambahan, memodifikasi logika transformasi, atau mengubah penjadwalan.

## Kontainer Docker
Saluran ETL dikontainerkan menggunakan Docker. File `docker-compose.yaml` mendefinisikan layanan dan kontainer yang dibutuhkan untuk saluran ini, termasuk:

- Penjadwal dan server web Airflow
- Basis data PostgreSQL
- Layanan atau alat tambahan yang diperlukan untuk proses ETL

Anda dapat memodifikasi file Docker Compose untuk menambah atau menghapus layanan, mengubah alokasi sumber daya, atau mengonfigurasi jaringan sesuai kebutuhan.

