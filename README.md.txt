# 📡 ESP32 Akıllı RFID Yoklama ve Erişim Takip Sistemi

<p align="center">
  <img src="https://img.shields.io/badge/ESP32-Microcontroller-red?style=for-the-badge&logo=espressif&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-REST_API-black?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge" />
</p>

<p align="center">
  <b>Donanım tabanlı RFID kimlik doğrulama, RESTful ağ haberleşmesi ve canlı koyu temalı web yönetim paneli içeren uçtan uca IoT erişim sistemi.</b>
</p>

---

## 🌟 Öne Çıkan Özellikler

* **Donanım Katmanı:** 13.56 MHz RFID kartları MFRC522 modülü ile SPI protokolü üzerinden okur. Durum bildirimlerini I2C 16x2 LCD ekran, çift durum LED'i ve frekans kontrollü pasif buzzer ile kullanıcıya anında sunar.
* **Ağ ve Güvenlik Doğrulaması:** Okunan kart UID'lerini HTTP POST isteğiyle arka yüz sunucusuna iletir. Yetkili kartlara anında onay (`HTTP 200`), yetkisiz kartlara ise ret uyarısı (`HTTP 403`) döner.
* **Modern Web Paneli:** Flask ile geliştirilmiş, 3 saniyede bir otomatik yenilenen, canlı istatistik kartları ve durum rozetleri içeren koyu temalı gösterge paneli.
* **Kalıcı Veri Depolama:** Kart UID'si, kart sahibi ismi ve zaman damgası SQLite veritabanına otomatik kaydedilir.

---

## 🛠️ Donanım ve Pin Bağlantı Şeması

| Bileşen | Pin Fonksiyonu | ESP32 Pini | Haberleşme Protokolü |
| :--- | :--- | :--- | :--- |
| **MFRC522 RFID Okuyucu** | SDA (SS) | GPIO 5 | SPI |
| | SCK | GPIO 18 | SPI |
| | MOSI | GPIO 23 | SPI |
| | MISO | GPIO 19 | SPI |
| | RST | GPIO 4 | Dijital Pin |
| | 3.3V / GND | 3.3V / GND | Güç |
| **I2C LCD 1602 Ekran** | SDA | GPIO 21 | I2C |
| | SCL | GPIO 22 | I2C |
| | VCC / GND | 5V (VIN) / GND | Güç |
| **Durum Bildiriciler** | Yeşil LED (Onay) | GPIO 2 | Dijital Çıkış |
| | Kırmızı LED (Yetkisiz) | GPIO 15 | Dijital Çıkış |
| | Pasif Buzzer | GPIO 14 | PWM / Ton |

---

## 🔌 Sistem Mimarisi

```text
 [ RFID Kart ] 
       │ (13.56 MHz)
       ▼
 [ ESP32 İstemci ] ──(Wi-Fi / JSON POST)──► [ Flask Arka Yüz :5000 ]
  ├─ LCD 1602 (I2C)                                │
  ├─ Durum LED'leri                                ├─ SQLite DB (attendance.db)
  └─ Pasif Buzzer                                  └─ Web Paneli (Canlı UI)
  
  
  ## 🚀 Kurulum ve Çalıştırma

### 1. Arka Yüz (Backend) Kurulumu
```bash
cd backend
pip install -r requirements.txt
py app.py

2. Mikrodenetleyici (ESP32) Yapılandırması
 -firmware/esp32_attendance.ino dosyasını Arduino IDE ile açın.
 -Gerekli kütüphaneleri yükleyin (MFRC522, LiquidCrystal_I2C).
 -Wi-Fi bilgilerinizi ve sunucu IP adresinizi tanımlayıp karta yükleyin.
 
3. Wi-Fi ve IP Bilgilerini Güncelleyip Karta Yükleme
  -const char* WIFI_SSID     = "YOUR_WIFI_SSID";
  -const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
  -const char* SERVER_URL    = "http://YOUR_SERVER_IP:5000/api/attendance";
  -Kodu ESP32 kartınıza yükleyin.  

  📄 Lisans
Bu proje MIT Lisansı ile korunmaktadır.
  
  
  
  
  