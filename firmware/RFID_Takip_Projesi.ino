#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi Bilgileri
const char* WIFI_SSID     = "TurkTelekom_TP6E20_EXT";
const char* WIFI_PASSWORD = "93xTDJVxs4Rg";

// Python Flask Sunucu Adresin
const char* SERVER_URL    = "http://192.168.1.108:5000/api/attendance";

// ESP32 Pin Konfigürasyonu
#define SS_PIN     5
#define RST_PIN    4
#define BUZZER_PIN 14
#define LED_GREEN  2
#define LED_RED    15

LiquidCrystal_I2C lcd(0x27, 16, 2);
MFRC522 rfid(SS_PIN, RST_PIN);

// Pasif Buzzer İçin Yüksek Sesli Frekans Fonksiyonu
void playBeep(int freq, int durationMs) {
  tone(BUZZER_PIN, freq);
  delay(durationMs);
  noTone(BUZZER_PIN);
}

void updateReadyScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Lutfen Kartinizi");
  lcd.setCursor(0, 1);
  lcd.print("Okutunuz...");
}

void connectWiFi() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Wi-Fi Baglaniyor");
  Serial.print("Wi-Fi baglantisi kuruluyor");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi Baglandi!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Wi-Fi Baglandi!");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP().toString());
  delay(1500);
}

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);        // SDA: 21, SCL: 22
  SPI.begin(18, 19, 23, 5);  // SCK, MISO, MOSI, SS
  rfid.PCD_Init();

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  noTone(BUZZER_PIN);

  lcd.init();
  lcd.backlight();

  connectWiFi();

  // Açılış testi: Canlı ve yüksek bir "bip"
  playBeep(2400, 120);
  updateReadyScreen();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String uidStr = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uidStr += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    uidStr += String(rfid.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();

  Serial.println("[KART OKUNDU] UID: " + uidStr);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Kayit Yapiliyor");
  lcd.setCursor(0, 1);
  lcd.print("ID: " + uidStr);

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String jsonBody = "{\"uid\":\"" + uidStr + "\"}";
  int httpCode = http.POST(jsonBody);

  if (httpCode == 201 || httpCode == 200) {
    // Başarılı: Yeşil LED + Melodik Çift Yüksek Bip (2000Hz -> 2800Hz)
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Yoklama Alindi!");
    lcd.setCursor(0, 1);
    lcd.print("ID: " + uidStr);

    digitalWrite(LED_GREEN, HIGH);
    playBeep(2000, 90);
    delay(60);
    playBeep(2800, 130);
    
    delay(1500);
    digitalWrite(LED_GREEN, LOW);
  } else {
    // Hata: Kırmızı LED + Düşük Kalın Uyarı Sesi (800Hz)
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sunucu Hatasi!");
    lcd.setCursor(0, 1);
    lcd.print("Kod: " + String(httpCode));

    digitalWrite(LED_RED, HIGH);
    playBeep(800, 400);
    delay(1500);
    digitalWrite(LED_RED, LOW);
  }

  http.end();
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  updateReadyScreen();
}
