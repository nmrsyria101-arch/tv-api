import requests
import json
import datetime
import re
from bs4 import BeautifulSoup

# --- إعدادات ---
# رابط ملف القنوات (iptv)
IPTV_URL = "https://gist.githubusercontent.com/yasiralbeatiy/a078d245888ce7eb892e04d120f1420c/raw/a6b268326c30276367a62947e4dc862b1b171410/beinsport.m3u"

# رابط المباريات (فيلجول - مصدر خفيف ومستقر)
MATCHES_URL = "https://www.filgoal.com/matches/today"

def get_iptv_links():
    """جلب وتنظيف روابط القنوات"""
    print("Fetching IPTV...")
    channels = {}
    try:
        response = requests.get(IPTV_URL, timeout=10)
        lines = response.text.splitlines()
        for i, line in enumerate(lines):
            if "#EXTINF" in line and i+1 < len(lines):
                # تنظيف الاسم (bein sports 1 -> beinsports1)
                name = line.split(",")[-1].strip().lower()
                clean = re.sub(r'[^a-z0-9]', '', name)
                url = lines[i+1].strip()
                if url.startswith("http"):
                    channels[clean] = url
    except Exception as e:
        print(f"IPTV Error: {e}")
    return channels

def get_matches():
    """جلب جدول المباريات من فيلجول"""
    print("Fetching Matches...")
    matches = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        resp = requests.get(MATCHES_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # البحث عن كروت المباريات
        match_cards = soup.find_all('div', class_='mc-block')
        
        for card in match_cards:
            try:
                # استخراج أسماء الفرق
                teams = card.find_all('div', class_='team-name')
                if len(teams) < 2: continue
                
                team_a = teams[0].text.strip()
                team_b = teams[1].text.strip()
                
                # استخراج الصور (إن وجدت)
                imgs = card.find_all('img')
                logo_a = imgs[0]['src'] if len(imgs) > 0 else ""
                logo_b = imgs[1]['src'] if len(imgs) > 1 else ""
                
                # تصحيح روابط الصور الناقصة
                if logo_a.startswith('//'): logo_a = 'https:' + logo_a
                if logo_b.startswith('//'): logo_b = 'https:' + logo_b
                
                # استخراج التوقيت
                time_area = card.find('div', class_='match-timing')
                time_str = time_area.find('span').text.strip() if time_area else "اليوم"
                
                # استخراج اسم القناة الناقلة
                ch_area = card.find('div', class_='channel-icon')
                channel = ch_area.text.strip() if ch_area else "غير محدد"
                
                matches.append({
                    "team_a": team_a, "logo_a": logo_a,
                    "team_b": team_b, "logo_b": logo_b,
                    "time": time_str,
                    "channel": channel,
                    "stream_url": "" # سنملؤه لاحقاً
                })
            except:
                continue
                
    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return matches

def main():
    try:
        # 1. جلب البيانات
        iptv_data = get_iptv_links()
        matches_data = get_matches()
        
        final_list = []
        
        # 2. عملية الربط (Matching)
        for match in matches_data:
            url = ""
            # تنظيف اسم القناة من المباراة (beIN Sports 1 HD -> beinsports1)
            target = re.sub(r'[^a-z0-9]', '', match['channel'].lower())
            
            # البحث عن الرابط المناسب
            for key, val in iptv_data.items():
                if target in key or key in target:
                    url = val
                    break
            
            final_list.append({**match, "stream_url": url})
            
        # 3. الحفظ
        output = {"updated_at": str(datetime.datetime.now()), "matches": final_list}
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print("Updated Successfully!")
        
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
    
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("تم التحديث بنجاح! 🎉")

if __name__ == "__main__":
    main()
