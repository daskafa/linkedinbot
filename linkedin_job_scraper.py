import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Telegram bot ayarları
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')

# Sessiz saatler (Telegram bildirimi gönderilmez, ama bot çalışır)
SILENT_HOURS_START = 0  # Gece 12 (00:00)
SILENT_HOURS_END = 9    # Sabah 9 (09:00)

# LinkedIn arama URL'leri (virgülle ayrılmış)
SEARCH_URLS_STR = os.environ.get('LINKEDIN_SEARCH_URLS', 
    'https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Turkey')

# Filtreleme için keywords (virgülle ayrılmış, opsiyonel)
FILTER_KEYWORDS_STR = os.environ.get('FILTER_KEYWORDS', '')
FILTER_KEYWORDS = [kw.strip().lower() for kw in FILTER_KEYWORDS_STR.split(',') if kw.strip()]

# URL'leri listeye çevir
SEARCH_URLS = [url.strip() for url in SEARCH_URLS_STR.split(',') if url.strip()]

# Her URL'e son 24 saat filtresini ekle
for i, url in enumerate(SEARCH_URLS):
    if '&f_TPR=' not in url:
        SEARCH_URLS[i] = url + '&f_TPR=r86400'

SEEN_FILE = 'seen_jobs.json'
JOBS_DIR = 'jobs_history'
STATS_FILE = 'stats.json'

def load_seen_jobs():
    """Daha önce görülen ilanları yükle"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return json.load(f)
    return []

def save_seen_jobs(seen):
    """Görülen ilanları kaydet"""
    with open(SEEN_FILE, 'w') as f:
        json.dump(seen, f, indent=2)

def save_daily_jobs(jobs):
    """Günlük ilanları kaydet"""
    if not os.path.exists(JOBS_DIR):
        os.makedirs(JOBS_DIR)
    
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"{JOBS_DIR}/{today}.json"
    
    # Bugünkü dosya varsa oku, yoksa boş liste
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            daily_jobs = json.load(f)
    else:
        daily_jobs = []
    
    # Yeni ilanları ekle (duplicate kontrolü)
    existing_links = {job['link'] for job in daily_jobs}
    for job in jobs:
        if job['link'] not in existing_links:
            job['found_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            daily_jobs.append(job)
    
    # Kaydet
    with open(filename, 'w') as f:
        json.dump(daily_jobs, f, indent=2, ensure_ascii=False)

def load_stats():
    """İstatistikleri yükle"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        "total_checked": 0,
        "total_new": 0,
        "last_run": None,
        "runs": []
    }

def save_stats(stats):
    """İstatistikleri kaydet"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def matches_keywords(job, keywords):
    """İlanın keyword'leri içerip içermediğini kontrol et"""
    if not keywords:
        return True  # Keyword filtresi yoksa hepsini kabul et
    
    # Başlık ve şirketi birleştir (küçük harfe çevir)
    text = f"{job['title']} {job['company']}".lower()
    
    # En az bir keyword eşleşmeli
    for keyword in keywords:
        if keyword in text:
            return True
    
    return False

def send_telegram_message(message):
    """Telegram'a bildirim gönder"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram ayarlari yapilmamis")
        return
    
    # Sessiz saatlerde bildirim gönderme
    current_hour = datetime.now().hour
    if SILENT_HOURS_START <= current_hour < SILENT_HOURS_END:
        print(f"Sessiz saat ({current_hour:02d}:00) - Telegram bildirimi atlanıyor")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("Telegram bildirimi gonderildi")
        else:
            print(f"Telegram hatasi: {response.status_code}")
            print(f"Hata detayi: {response.text}")
    except Exception as e:
        print(f"Telegram baglanti hatasi: {e}")

def scrape_linkedin_jobs(search_url):
    """LinkedIn ilanlarını çek"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        print(f"LinkedIn aranıyor: {search_url[:80]}...")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # İlan kartlarını bul
        job_cards = soup.find_all('div', class_='base-card')
        
        jobs = []
        for card in job_cards:  # Tüm ilanlar
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                link_elem = card.find('a', class_='base-card__full-link')
                
                if title_elem and link_elem:
                    job = {
                        'title': title_elem.text.strip(),
                        'company': company_elem.text.strip() if company_elem else 'N/A',
                        'location': location_elem.text.strip() if location_elem else 'N/A',
                        'link': link_elem['href'].split('?')[0]  # Query parametrelerini temizle
                    }
                    jobs.append(job)
            except Exception as e:
                print(f"Ilan parse hatasi: {e}")
                continue
        
        print(f"{len(jobs)} ilan bulundu")
        return jobs
        
    except Exception as e:
        print(f"Scraping hatasi: {e}")
        return []

def main():
    print(f"\n{'='*50}")
    print(f"LinkedIn Job Bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # İstatistikleri yükle
    stats = load_stats()
    
    # Görülen ilanları yükle
    seen_jobs = load_seen_jobs()
    print(f"Daha once gorulen ilan sayisi: {len(seen_jobs)}")
    print(f"Arama sayisi: {len(SEARCH_URLS)}")
    if FILTER_KEYWORDS:
        print(f"Filtre keywords: {', '.join(FILTER_KEYWORDS)}")
    print()
    
    # Tüm ilanları topla
    all_jobs = []
    for idx, search_url in enumerate(SEARCH_URLS, 1):
        print(f"[{idx}/{len(SEARCH_URLS)}] ", end="")
        jobs = scrape_linkedin_jobs(search_url)
        all_jobs.extend(jobs)
        
        # LinkedIn'i yormamak için kısa bekleme
        if idx < len(SEARCH_URLS):
            import time
            time.sleep(2)
    
    # Duplicate ilanları temizle (aynı link birden fazla aramada çıkabilir)
    unique_jobs = []
    seen_links = set()
    for job in all_jobs:
        if job['link'] not in seen_links:
            unique_jobs.append(job)
            seen_links.add(job['link'])
    
    print(f"\nToplam unique ilan: {len(unique_jobs)}")
    
    # Keyword filtresi uygula
    if FILTER_KEYWORDS:
        filtered_jobs = [job for job in unique_jobs if matches_keywords(job, FILTER_KEYWORDS)]
        print(f"Filtre sonrasi: {len(filtered_jobs)} ilan")
        unique_jobs = filtered_jobs
    
    if not unique_jobs:
        print("Hic ilan bulunamadi")
        # Yine de özet gönder
        summary = f"""━━━━━━━━━━━━━━━━━━━━━━
BOT CALISMA OZETI

Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Taranan: 0 ilan
Yeni: 0 ilan
Durum: Yeni ilan bulunamadi
━━━━━━━━━━━━━━━━━━━━━━"""
        send_telegram_message(summary)
        return
    
    # Yeni ilanları filtrele
    new_jobs = [job for job in unique_jobs if job['link'] not in seen_jobs]
    
    print(f"Yeni ilan sayisi: {len(new_jobs)}")
    
    # İstatistikleri güncelle
    stats['total_checked'] += len(unique_jobs)
    stats['total_new'] += len(new_jobs)
    stats['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stats['runs'].append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'checked': len(unique_jobs),
        'new': len(new_jobs)
    })
    
    # Son 100 çalıştırmayı tut
    stats['runs'] = stats['runs'][-100:]
    
    # Yeni ilanları bildir
    for job in new_jobs:
        message = f"""━━━━━━━━━━━━━━━━━━━━━━
YENI IS ILANI

Pozisyon: {job['title']}
Sirket: {job['company']}
Lokasyon: {job['location']}

Link: {job['link']}
━━━━━━━━━━━━━━━━━━━━━━"""
        
        print(f"\nBildirim: {job['title']} - {job['company']}")
        send_telegram_message(message)
        
        # Görülen listeye ekle
        seen_jobs.append(job['link'])
    
    # Özet mesajı gönder
    summary = f"""━━━━━━━━━━━━━━━━━━━━━━
BOT CALISMA OZETI

Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Taranan: {len(unique_jobs)} ilan
Yeni: {len(new_jobs)} ilan
Durum: {'Yeni ilanlar bulundu' if new_jobs else 'Yeni ilan yok'}
━━━━━━━━━━━━━━━━━━━━━━"""
    send_telegram_message(summary)
    
    # Günlük ilanları kaydet
    if new_jobs:
        save_daily_jobs(new_jobs)
    
    # Kaydet (son 500 ilan)
    save_seen_jobs(seen_jobs[-500:])
    save_stats(stats)
    
    print(f"\nIslem tamamlandi\n")

if __name__ == "__main__":
    main()
