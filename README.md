# LinkedIn Job Bot 🤖

LinkedIn'de yeni iş ilanlarını otomatik takip eden ve Telegram'dan bildirim gönderen bot.

## Özellikler

- ✅ Tamamen ücretsiz (GitHub Actions)
- ✅ PC kapalı olsa bile çalışır
- ✅ Her 4 saatte otomatik kontrol
- ✅ Telegram bildirimi
- ✅ Login gerektirmez

## Kurulum

### 1. Telegram Bot Oluştur

1. Telegram'da [@BotFather](https://t.me/BotFather) ile konuş
2. `/newbot` komutunu gönder
3. Bot için isim belirle
4. Aldığın **token**'ı kaydet (örn: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Chat ID Bul

1. [@userinfobot](https://t.me/userinfobot) ile konuş
2. Sana gönderdiği **ID**'yi kaydet (örn: `987654321`)

### 3. GitHub Repository Ayarları

1. Bu projeyi GitHub'a fork'la veya yeni repo oluştur
2. Repository → **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** ile şunları ekle:

   - `TELEGRAM_TOKEN`: Bot token'ın
   - `CHAT_ID`: Telegram ID'n
   - `LINKEDIN_SEARCH_URLS`: LinkedIn arama URL'lerin (virgülle ayır)
   - `FILTER_KEYWORDS`: (Opsiyonel) Filtreleme için keywords (virgülle ayır, örn: `Laravel,PHP,Symfony`)

### 4. LinkedIn Arama URL'leri Oluştur

1. [LinkedIn Jobs](https://www.linkedin.com/jobs/) sayfasına git
2. Arama yap (örn: "Python Developer", "Turkey")
3. Filtreleri uygula (uzaktan, tam zamanlı vs.)
4. Tarayıcıdaki URL'i kopyala
5. Birden fazla arama için virgülle ayır

**Tek arama:**
```
https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Turkey
```

**Birden fazla arama (virgülle ayır):**
```
https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Turkey,https://www.linkedin.com/jobs/search/?keywords=Node.js%20Developer&location=Turkey,https://www.linkedin.com/jobs/search/?keywords=Full%20Stack%20Developer&location=Turkey
```

6. GitHub secrets'a `LINKEDIN_SEARCH_URLS` olarak ekle

### 5. Keyword Filtresi (Opsiyonel)

Alakasız ilanları filtrelemek için keyword'ler belirle:

```
Laravel,PHP,Symfony,Backend
```

- İlan başlığı veya şirket adında en az bir keyword geçmeli
- Büyük/küçük harf duyarsız
- GitHub secrets'a `FILTER_KEYWORDS` olarak ekle

### 5. GitHub Actions'ı Aktifleştir

1. Repository → **Actions** sekmesi
2. "I understand my workflows, go ahead and enable them" butonuna tıkla
3. **LinkedIn Job Checker** workflow'unu seç
4. **Run workflow** ile manuel test et

## Kullanım

Bot her 4 saatte otomatik çalışır. Manuel çalıştırmak için:

1. **Actions** sekmesine git
2. **LinkedIn Job Checker** seçeneğini tıkla
3. **Run workflow** → **Run workflow**

## Ayarlar

### Çalışma Sıklığını Değiştir

`.github/workflows/job-checker.yml` dosyasında:

```yaml
# Her 2 saatte
- cron: '0 */2 * * *'

# Her 6 saatte
- cron: '0 */6 * * *'

# Günde 2 kez (09:00, 18:00 UTC)
- cron: '0 9,18 * * *'
```

### Arama Kriterlerini Değiştir

GitHub Secrets'taki `LINKEDIN_SEARCH_URLS`'i güncelle. Birden fazla arama için virgülle ayır.

## Sorun Giderme

### Bot çalışmıyor

1. **Actions** sekmesinde hata loglarını kontrol et
2. Secrets'ların doğru girildiğinden emin ol
3. Telegram bot token'ının geçerli olduğunu kontrol et

### Bildirim gelmiyor

1. Bot'a Telegram'da `/start` komutu gönder
2. Chat ID'nin doğru olduğunu kontrol et
3. Bot token'ının aktif olduğunu kontrol et

### İlan bulunamıyor

1. LinkedIn URL'inin public olduğundan emin ol
2. URL'de login gerektiren filtreler olmasın
3. Manuel test et: `python linkedin_job_scraper.py`

## Yerel Test

```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Environment variables ayarla
export TELEGRAM_TOKEN="your_token"
export CHAT_ID="your_chat_id"

# Tek arama
export LINKEDIN_SEARCH_URLS="https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Turkey"

# Birden fazla arama (virgülle ayır)
export LINKEDIN_SEARCH_URLS="https://www.linkedin.com/jobs/search/?keywords=Python&location=Turkey,https://www.linkedin.com/jobs/search/?keywords=Node.js&location=Turkey"

# Keyword filtresi (opsiyonel)
export FILTER_KEYWORDS="Laravel,PHP,Symfony"

# Çalıştır
python linkedin_job_scraper.py

# Dashboard'u başlat
python3 -m http.server 8000
# Tarayıcıda aç: http://localhost:8000/dashboard.html
```

## Notlar

- GitHub Actions ayda 2000 dakika ücretsiz (bu bot için fazlasıyla yeterli)
- Bot sadece yeni ilanları bildirir (tekrar göndermez)
- Son 500 ilan hafızada tutulur
- LinkedIn'in rate limit'ine takılmamak için 4 saatte bir çalışır

## Lisans

MIT
