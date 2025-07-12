
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def scrape_rakuten_campaigns():
    """
    楽天の関連ページからキャンペーン情報を収集し、高度なフィルタリングをかけてCSVに出力する
    """
    # 1. URLパターンの学習（これらを含むURLを優先）
    VALID_URL_PATTERNS = [
        '/campaign/', '/event/', '/sale/', 'feature.co.jp', 'campaign.rakuten.co.jp'
    ]

    # 2. NGワードの追加
    EXCLUDE_KEYWORDS = [
        '規約', 'プライバシー', 'policy', '個人情報', 'サイトマップ', 'sitemap', 
        '企業情報', 'corp', '採用', 'recruit', 'お問い合わせ', 'contact', 'help',
        'ガイド', 'guide', '一覧', 'list', 'ログイン', 'login', '登録', 'register',
        'ランキング', 'ranking', 'カテゴリ', 'category', '会社概要', 'about', '楽天グループ'
    ]
    
    GENERIC_TITLES = [
        '詳細はこちら', 'もっと見る', 'こちら', 'click here', 'see more', 'details'
    ]

    urls = {
        'rakuten_top': 'https://www.rakuten.co.jp/',
        'pointclub': 'https://point.rakuten.co.jp/campaign/',
        'card': 'https://www.rakuten-card.co.jp/campaign/'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    all_campaigns = []
    processed_urls = set()

    for name, url in urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                
                # 3. プレースホルダーの除去
                if '#' in href:
                    continue

                full_url = urljoin(url, href);

                if full_url in processed_urls:
                    continue

                title = (link.text.strip() or link.get('title', '') or (link.find('img') and link.find('img').get('alt', '')) or '').strip()
                
                if title and 'http' in full_url:
                    title_lower = title.lower()
                    href_lower = full_url.lower()

                    # --- 高度なフィルタリングロジック ---
                    is_valid = False
                    # A. URLパターンチェック
                    if any(pattern in href_lower for pattern in VALID_URL_PATTERNS):
                        is_valid = True
                    
                    # B. タイトルに「キャンペーン」が含まれていれば優先
                    if 'キャンペーン' in title:
                        is_valid = True

                    # C. NGワードが含まれていれば除外
                    if any(ex_key in href_lower for ex_key in EXCLUDE_KEYWORDS) or \
                       any(ex_key in title_lower for ex_key in EXCLUDE_KEYWORDS):
                        is_valid = False

                    # D. 汎用・短すぎるタイトルを除外
                    if title_lower in [gt.lower() for gt in GENERIC_TITLES] or len(title) < 10:
                        is_valid = False

                    if is_valid:
                        all_campaigns.append({
                            'source': name,
                            'title': title,
                            'url': full_url
                        })
                        processed_urls.add(full_url)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    if all_campaigns:
        df = pd.DataFrame(all_campaigns)
        df.drop_duplicates(subset=['url'], inplace=True)
        
        output_path = 'rakuten_campaigns.csv'
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Successfully scraped and hyper-filtered {len(df)} campaigns. Saved to {output_path}")
    else:
        print("No valid campaigns found after hyper-filtering.")

if __name__ == '__main__':
    scrape_rakuten_campaigns()
