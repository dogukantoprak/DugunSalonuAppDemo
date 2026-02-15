<div align="center">
  <img src="docs/assets/dashboard_screenshot.png" alt="DugunSalonuApp Dashboard" width="800"/>

  # 💍 DugunSalonuApp

  **Modern Düğün Salonu Yönetim Sistemi**

  Rezervasyonlardan personel takibine, mali raporlardan ayarlara kadar
  düğün salonu operasyonlarınızı tek panelden yönetin.

  [![Live Demo](https://img.shields.io/badge/🌐_Canlı_Demo-GitHub_Pages-blue?style=for-the-badge)](https://dogukantoprak.github.io/DugunSalonuAppDemo/)
  [![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.112-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Electron](https://img.shields.io/badge/Electron-31-47848F?style=for-the-badge&logo=electron&logoColor=white)](https://www.electronjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Canlı Demo](#-canlı-demo)
- [Özellikler](#-özellikler)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Teknoloji Stack](#-teknoloji-stack)
- [Mimari Yapı](#-mimari-yapı)
- [Lisans](#-lisans)

---

## 🎯 Proje Hakkında

**DugunSalonuApp**, düğün ve etkinlik salonlarının günlük operasyonlarını dijitalleştirmek için geliştirilmiş **tam kapsamlı (full-stack)** bir yönetim sistemidir. Uygulama hem **web tarayıcı** üzerinden hem de **Electron** ile masaüstü uygulama olarak çalışabilir.

### Neden Bu Projeyi Geliştirdim?

Düğün salonu işletmeleri genellikle kağıt üzerinde veya dağınık Excel tablolarıyla yönetilmektedir. Bu proje ile:
- ✅ Çakışmasız, takvim tabanlı **akıllı rezervasyon** sistemi
- ✅ Personel listesi, maaş takibi ve **haftalık planlama**
- ✅ Gelir-gider analizi ile **mali raporlama**
- ✅ Rol bazlı yetkilendirme ile **veri güvenliği**

tek bir modern arayüzde sunulmuştur.

---

## 🌐 Canlı Demo

> **[🔗 https://dogukantoprak.github.io/DugunSalonuAppDemo/](https://dogukantoprak.github.io/DugunSalonuAppDemo/)**

Proje tanıtım sayfasında uygulamanın özelliklerini, ekran görüntülerini ve teknoloji altyapısını inceleyebilirsiniz.

---

## ✨ Özellikler

| Modül | Açıklama |
|-------|----------|
| 📊 **Dashboard** | Yaklaşan etkinlikler, aylık istatistikler, 3 aylık takvim görünümü, hızlı işlem butonları |
| 📅 **Rezervasyonlar** | Tarih/saat bazlı rezervasyon oluşturma, çakışma kontrolü, salon seçimi, durum takibi |
| 👥 **Personel Yönetimi** | Kadrolu/part-time personel kayıtları, rol atamaları, maaş bilgileri, haftalık planlama |
| 💰 **Giderler** | Kategori bazlı harcama kaydı, rezervasyonla ilişkilendirme |
| 📈 **Raporlar** | Dönemsel gelir-gider analizi, grafik ve tablo formatında detaylı raporlama |
| ⚙️ **Ayarlar** | Salon tanımları, menü yönetimi, etkinlik türleri, uygulama konfigürasyonu |
| 🔐 **Kimlik Doğrulama** | Kullanıcı kayıt/giriş, rol bazlı erişim kontrolü (Admin, Staff, Viewer) |

### Öne Çıkan Teknik Detaylar

- 🗓️ **3 Aylık Takvim Görünümü** — Yoğun/boş günleri renk kodlarıyla anında görün
- 📄 **PDF & Excel Dışa Aktarım** — Sözleşme yazdırma ve rezervasyon verilerini Excel'e aktarma
- 🖥️ **Masaüstü Uygulama** — Electron entegrasyonu ile Windows için native .exe build
- 🌙 **Dark Mode Arayüz** — Göz yormayan, modern koyu tema tasarımı
- ⚡ **Gerçek Zamanlı API** — FastAPI ile yüksek performanslı RESTful backend

---

## 📸 Ekran Görüntüleri

<div align="center">

### Dashboard — Ana Panel
<img src="docs/assets/dashboard_screenshot.png" alt="Dashboard" width="750"/>

*3 aylık takvim, istatistik kartları ve hızlı işlem butonları*

---

### Yeni Rezervasyon — Detaylı Form
<img src="docs/assets/new_reservation.png" alt="Yeni Rezervasyon" width="750"/>

*Çok sekmeli form: Rezervasyon bilgileri, fiyat bilgileri ve menü bilgileri*

---

### Personel Yönetimi
<img src="docs/assets/personnel_screenshot.png" alt="Personel Yönetimi" width="750"/>

*Kadrolu/part-time filtreleme, maaş bilgileri, arama ve personel kartları*

---

### Rezervasyon Listesi
<img src="docs/assets/reservations_screenshot.png" alt="Rezervasyonlar" width="750"/>

*Tarih bazlı rezervasyon görüntüleme ve yeni rezervasyon oluşturma*

</div>

---

## 🛠️ Teknoloji Stack

### Frontend
| Teknoloji | Versiyon | Kullanım Amacı |
|-----------|----------|----------------|
| **React** | 19 | UI bileşen framework'ü |
| **TypeScript** | 5.9 | Tip güvenli geliştirme |
| **Vite** | 7.2 | Hızlı build ve geliştirme sunucusu |
| **React Router** | 7.9 | Sayfa yönlendirme |
| **Electron** | 31 | Masaüstü uygulama (Windows) |
| **jsPDF** | 4.0 | PDF sözleşme yazdırma |
| **xlsx** | 0.18 | Excel dışa aktarım |

### Backend
| Teknoloji | Versiyon | Kullanım Amacı |
|-----------|----------|----------------|
| **Python** | 3.x | Backend dili |
| **FastAPI** | 0.112 | REST API framework'ü |
| **Pydantic** | 2.8 | Veri validasyonu |
| **Uvicorn** | 0.30 | ASGI sunucusu |
| **SQLite** | — | Gömülü veritabanı |

---

## 🏗️ Mimari Yapı

```
┌─────────────────────────────────────────────────────────────┐
│                    ELECTRON SHELL (Windows)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              REACT FRONTEND (Vite + TS)               │  │
│  │                                                       │  │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │  │
│  │   │Dashboard │ │Rezervasyon│ │ Personel │ │Raporlar│ │  │
│  │   └──────────┘ └──────────┘ └──────────┘ └────────┘ │  │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐            │  │
│  │   │ Giderler │ │ Ayarlar  │ │  Auth    │            │  │
│  │   └──────────┘ └──────────┘ └──────────┘            │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      │ HTTP (REST API)                       │
│  ┌───────────────────▼───────────────────────────────────┐  │
│  │             FASTAPI BACKEND (Python)                   │  │
│  │                                                       │  │
│  │   ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │   │  Controllers │  │    Models    │  │  Database  │ │  │
│  │   │              │  │              │  │  (SQLite)  │ │  │
│  │   │ • Reservation│  │ • Reservation│  │            │ │  │
│  │   │ • Personnel  │  │ • User       │  │  salon.db  │ │  │
│  │   │ • Reports    │  │              │  │            │ │  │
│  │   │ • Settings   │  │              │  │            │ │  │
│  │   │ • Attendance │  │              │  │            │ │  │
│  │   │ • User       │  │              │  │            │ │  │
│  │   └──────────────┘  └──────────────┘  └────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Kaynak Kod

> ⚠️ **Bu proje özel (private) olarak geliştirilmektedir.**
>
> Kaynak kodları paylaşıma açık değildir. Proje hakkında daha fazla bilgi almak veya demo talep etmek için benimle iletişime geçebilirsiniz.

---

## 📄 Lisans

Bu proje eğitim ve portfolyo amacıyla geliştirilmiştir. Tüm hakları saklıdır.

---

<div align="center">

  **[🌐 Canlı Demo](https://dogukantoprak.github.io/DugunSalonuAppDemo/)** · **[⬆ Başa Dön](#-dugunsalonuappdemo)**

  *React 19 • TypeScript • FastAPI • Electron • SQLite ile geliştirildi*

</div>
