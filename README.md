# 🌍 Hermes GeoStudio

**Geospatial analysis extension for Hermes Agent** — powered by Google Earth Engine.

[Hermes Agent](https://github.com/NousResearch/hermes-agent) × [Google Earth Engine](https://earthengine.google.com/)

---

## 📋 Deskripsi

Hermes GeoStudio adalah ekstensi untuk [Hermes Agent](https://github.com/NousResearch/hermes-agent) yang memungkinkan agen AI melakukan analisis geospasial secara otonom menggunakan data satelit dari **Google Earth Engine (GEE)**.

### Fitur Utama

- **Analisis Citra Satelit** — Sentinel-2, Landsat 8/9, MODIS
- **Indeks Spektral** — NDVI, EVI, NDWI, MNDWI, NDBI, NDMI
- **Analisis Topografi** — Slope, aspect, elevation dari SRTM/ASTER DEM
- **Klasifikasi Tutupan Lahan** — Simplified & ML-based classification
- **Layout Peta Profesional** — A4/A3 portrait/landscape dengan legenda & skala
- **Laporan PDF** — Dokumentasi lengkap dengan metodologi & interpretasi
- **Ekspor Multi-Format** — Shapefile (.shp), GeoTIFF, GeoJSON, CSV

### Contoh Prompt

```
"Buat komposit Sentinel-2 untuk Bandung Barat periode Jan-Mar 2024"
"Hitung NDVI dan ekspor sebagai GeoTIFF"
"Buat peta kemiringan lereng dari data SRTM"
"Hitung luas setiap kelas tutupan lahan di area studi"
"Buat layout A4 landscape dan laporan PDF dari hasil analisis"
```

---

## 🏗️ Arsitektur

```
Hermes Agent → MCP Server (stdio) → Python GIS Engine → Google Earth Engine API
                                              ↓
                              rasterio / geopandas / matplotlib / reportlab
                                              ↓
                                    Output: SHP, GeoTIFF, PDF, PNG
```

### Modul

| Modul | Fungsi |
|-------|--------|
| `gee/` | Koneksi GEE, pencarian citra, indeks spektral, analisis terrain |
| `gis/` | Pemrosesan raster/vektor lokal, CRS handling, export |
| `cartography/` | Layout peta profesional (A4/A3, legend, scale bar, north arrow) |
| `reporting/` | Generasi laporan PDF teknis |
| `workflows/` | Orkestrasi workflow end-to-end |
| `tools.py` | Definisi tool MCP untuk Hermes Agent |

---

## 📦 Instalasi

### Prasyarat

- Python 3.11+ (direkomendasikan 3.12)
- Akses internet untuk GEE API
- Chrome/Chromium browser untuk OAuth (sekali saja)

### Langkah Instalasi

```bash
# Clone repository
git clone https://github.com/ilhamriadi/hermes-geostudio.git
cd hermes-geostudio

# Buat virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env jika menggunakan service account
```

### Konfigurasi GEE

#### Opsi 1: OAuth (Recommended untuk personal use)
```bash
python -c "import ee; ee.Authenticate()"
python -c "import ee; ee.Initialize()"
```
Browser akan terbuka untuk otorisasi sekali saja.

#### Opsi 2: Service Account (untuk server/production)
```bash
export GEE_PROJECT_ID="your-cloud-project-id"
export GEE_CREDENTIALS_FILE="/path/to/service-account-key.json"
```

---

## 🔧 Integrasi dengan Hermes Agent

Tambahkan ke `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  geostudio:
    command: python
    args: ["-m", "hermes_geostudio.server"]
    cwd: "/path/to/hermes-geostudio"
    env:
      GEE_PROJECT_ID: "your-project-id"  # optional
      GEOSTUDIO_OUTPUT_DIR: "~/geostudio-output"
```

Atau jalankan manual:
```bash
hermes mcp add geostudio -- python -m hermes_geostudio.server
```

---

## 🛠️ Tool yang Tersedia

| Tool | Deskripsi |
|------|-----------|
| `gee_check_connection` | Cek koneksi GEE |
| `gee_authenticate` | Mulai OAuth authentication |
| `gee_search_imagery` | Cari citra satelit di area & periode |
| `gee_create_composite` | Buat komposit median/mean/max citra |
| `gee_calculate_index` | Hitung NDVI, EVI, NDWI, dll |
| `gee_terrain_analysis` | Analisis slope/aspect/elevation dari DEM |
| `gis_export_data` | Export ke SHP, GeoJSON, CSV |
| `map_create_layout` | Buat layout peta A4/A3 |
| `report_create_pdf` | Buat laporan PDF teknis |
| `geostudio_run_workflow` | Workflow orchestrator (multi-step) |

---

## 📁 Struktur Output

Hasil analisis disimpan di direktori output (default: `./output/`):

```
output/
├── slope_20261116_143000.tif      # Raster kemiringan lereng
├── ndvi_20261116_143000.tif       # Raster NDVI
├── map_Bandung_West_2026.png      # Layout peta
└── report_laporan_geospasial.pdf   # Laporan teknis
```

---

## 🧪 Pengujian

```bash
# Jalankan unit tests
pytest tests/ -v

# Jalankan dengan coverage
pytest tests/ -v --cov=src/hermes_geostudio --cov-report=html
```

---

## ⚠️ Batasan & Catatan

1. **GEE Quota** — Penggunaan GEE gratis untuk riset/non-komersial dengan kuota harian (~10k image operations/hari).
2. **Akurasi Klasifikasi** — Klasifikasi tutupan lahan menggunakan metode sederhana. Untuk akurasi tinggi, gunakan data validasi lapangan.
3. **Ukuran Area** — Area studi maksimal 10.000 km² per request untuk mencegah timeout.
4. **CRS** — Semua output menggunakan CRS yang dinyatakan eksplisit. Tidak ada reproyeksi diam-diam.
5. **Shapefile Package** — Export SHP dikemas dalam ZIP berisi `.shp`, `.shx`, `.dbf`, `.prj`.

---

## 🔒 Keamanan

- Credential GEE **tidak pernah** disimpan di source code atau Git
- `.env` dan file credentials masuk `.gitignore`
- Output data (PDF, SHP, GeoTIFF) tidak di-push ke repository

---

## 📝 Lisensi

MIT License — lihat file [LICENSE](LICENSE) untuk detail.

*Dikembangkan oleh NEXORA AI Team*
*Powered by Google Earth Engine & Hermes Agent*
