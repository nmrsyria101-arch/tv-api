import requests
import json
import datetime
import re
from bs4 import BeautifulSoup

# === إعدادات المصادر ===
# رابط ملف القنوات (الذي نأخذ منه البث)
IPTV_URL = "https://gist.githubusercontent.com/yasiralbeatiy/a078d245888ce7eb892e04d120f1420c/raw/a6b268326c30276367a62947e4dc862b1b171410/beinsport.m3u"

def get_iptv_links():
    """جلب روابط القنوات وتنظيف أسمائها"""
    print("جاري جلب روابط البث...")
    channels = {}
    try:
        response = requests.get(IPTV_URL)
        lines = response.text.splitlines()
        for i, line in enumerate(lines):
            if "#EXTINF" in line and "http" in lines[i+1]:
                # محاولة تنظيف اسم القناة ليسهل البحث عنه
                raw_name = line.split(",")[-1].strip().lower()
                # حذف الرموز وترك الارقام والحروف فقط (bein sports 1 -> beinsports1)
                clean_name = re.sub(r'[^a-z0-9]', '', raw_name)
                url = lines[i+1].strip()
                channels[clean_name] = url
    except Exception as e:
        print(f"Error fetching IPTV: {e}")
    return channels

def get_today_matches():
    """جلب مباريات اليوم من مصدر عربي موثوق (يلا كورة كمثال للدقة العربية)"""
    print("جاري جلب جدول المباريات...")
    matches = []
    try:
        # نستخدم يلا كورة لأنه يوفر اسم القناة بالعربي وهذا يسهل الربط
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://www.yallakora.com/match-center/", headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # البحث عن كل المباريات في الصفحة
        all_matches = soup.find_all('div', class_='item')
        
        for item in all_matches:
            try:
                # استخراج البيانات
                team_a = item.find('div', class_='teamA').find('p').text.strip()
                logo_a = item.find('div', class_='teamA').find('img')['src']
                
                team_b = item.find('div', class_='teamB').find('p').text.strip()
                logo_b = item.find('div', class_='teamB').find('img')['src']
                
                match_time = item.find('span', class_='time').text.strip()
                
                # استخراج القناة الناقلة
                channel_div = item.find('div', class_='channel')
                channel_name = channel_div.text.strip() if channel_div else "غير معروف"
                
                # حالة المباراة (جارية، انتهت، لم تبدأ)
                status = "upcoming"
                if "now" in item.get('class', []): status = "live"
                if "finish" in item.get('class', []): status = "finished"

                matches.append({
                    "team_a": team_a, "logo_a": logo_a,
                    "team_b": team_b, "logo_b": logo_b,
                    "time": match_time,
                    "channel": channel_name,
                    "status": status
                })
            except:
                continue
    except Exception as e:
        print(f"Error fetching matches: {e}")
    return matches

def main():
    iptv_data = get_iptv_links()
    matches_data = get_today_matches()
    
    final_list = []
    
    print("جاري ربط المباريات بروابط البث...")
    for match in matches_data:
        stream_link = ""
        
        # محاولة ذكية للربط: هل اسم القناة الناقلة موجود في ملف الروابط؟
        # تحويل "beIN Sports 1" إلى "beinsports1"
        target_channel = re.sub(r'[^a-z0-9]', '', match['channel'].lower().replace("hd", ""))
        
        # البحث في الروابط
        for ch_key, ch_url in iptv_data.items():
            if target_channel in ch_key or ch_key in target_channel:
                stream_link = ch_url
                break
        
        # اضافة المباراة للقائمة النهائية
        final_list.append({
            **match,
            "stream_url": stream_link
        })
        
    # حفظ الملف النهائي
    output = {
        "updated_at": str(datetime.datetime.now()),
        "matches": final_list
    }
    
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("تم التحديث بنجاح! 🎉")

if __name__ == "__main__":
    main()
