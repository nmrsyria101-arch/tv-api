import requests
import json
import datetime

M3U_SOURCE_URL = "https://gist.githubusercontent.com/yasiralbeatiy/a078d245888ce7eb892e04d120f1420c/raw/a6b268326c30276367a62947e4dc862b1b171410/beinsport.m3u"

def main():
    print("Starting scraper...")
    try:
        response = requests.get(M3U_SOURCE_URL)
        response.raise_for_status()
        lines = response.text.splitlines()
        final_channels = []
        
        for i, line in enumerate(lines):
            if "#EXTINF" in line and "bein" in line.lower():
                name = line.split(",")[-1].strip()
                if i + 1 < len(lines):
                    url = lines[i+1].strip()
                    if url.startswith("http"):
                        final_channels.append({
                            "id": len(final_channels)+1,
                            "name": name,
                            "stream_url": url,
                            "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/BeIN_Sports_logo.svg/1200px-BeIN_Sports_logo.svg.png"
                        })
        
        output = {"updated_at": str(datetime.datetime.now()), "channels": final_channels}
        with open("channels.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
