import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os

# あなたの楽天アフィリエイトIDを設定してください
RAKUTEN_AFFILIATE_ID = '1fc07efc.c2f2c7d2.1fc07efd.9f17bb92'

def convert_to_affiliate_link(original_url):
    """
    楽天のURLをアフィリエイトリンクに変換する。
    """
    parsed_url = urlparse(original_url)
    
    # 楽天の主要ドメインかチェック
    if "rakuten.co.jp" in parsed_url.netloc or \
       "rakuten.com" in parsed_url.netloc or \
       "rebates.jp" in parsed_url.netloc or \
       "rakuten-card.co.jp" in parsed_url.netloc or \
       "rakuten-bank.co.jp" in parsed_url.netloc or \
       "rakuten-wallet.co.jp" in parsed_url.netloc or \
       "books.rakuten.co.jp" in parsed_url.netloc or \
       "travel.rakuten.co.jp" in parsed_url.netloc:

        # 既存のクエリパラメータを保持
        query_params = parse_qs(parsed_url.query)
        
        # アフィリエイトIDを追加または更新
        query_params['scid'] = [RAKUTEN_AFFILIATE_ID] # scidは楽天アフィリエイトのトラッキングID

        # 新しいクエリ文字列を生成
        new_query = urlencode(query_params, doseq=True)

        # 新しいURLを構築
        affiliate_url = urlunparse(parsed_url._replace(query=new_query))
        return affiliate_url
    else:
        return original_url # 楽天以外のURLはそのまま返す

def generate_blog_post():
    """
    rakuten_campaigns.csvからデータを読み込み、
    Jekyll形式のMarkdownブログ記事を生成する。
    """
    try:
        df = pd.read_csv('rakuten_campaigns.csv')
    except FileNotFoundError:
        print("Error: rakuten_campaigns.csvが見つかりません。")
        print("先にrakuten_campaign_scraper.pyを実行してください。")
        return

    # 今日の日付を取得
    today = datetime.now()
    today_str = today.strftime('%Y年%m月%d日')
    date_for_filename = today.strftime('%Y-%m-%d')
    
    # 記事のタイトル
    article_title = f"【{today_str}更新】楽天経済圏 今週のお得キャンペーン総まとめ！"

    # Jekyll Front Matter
    md_content = []
    md_content.append("---")
    md_content.append(f"layout: post")
    md_content.append(f"title: \"{article_title}\"")
    md_content.append(f"date: {today.strftime('%Y-%m-%d %H:%M:%S %z')}") # ISO 8601形式
    md_content.append("categories: [rakuten, campaign, point]") # カテゴリは適宜調整
    md_content.append("---")
    md_content.append("\n")

    md_content.append("こんにちは！AIアシスタントです。")
    md_content.append(f"今週も楽天経済圏で開催されているお得なキャンペーン情報を集めてきました。（{today_str}時点）")
    md_content.append("エントリーが必要なものも多いので、お見逃しなく！")
    md_content.append("\n")
    md_content.append("---")
    md_content.append("\n")
    md_content.append("## 注目のキャンペーン一覧")
    md_content.append("\n")

    for index, row in df.iterrows():
        if pd.notna(row['title']) and pd.notna(row['url']):
            title = str(row['title']).strip()
            original_url = str(row['url']).strip()
            
            affiliate_url = convert_to_affiliate_link(original_url)

            md_content.append(f"- [{title}]({affiliate_url})")

    md_content.append("\n")
    md_content.append("---")
    md_content.append("\n")
    md_content.append("## まとめ")
    md_content.append("今週もたくさんのキャンペーンが開催されていますね。")
    md_content.append("特に、大型のセールイベントは見逃せません。")
    md_content.append("この記事が、皆さんのポイ活の助けになれば幸いです。")
    md_content.append("\n")
    md_content.append("> ※本記事はAIによって自動生成されています。最新の情報は各キャンペーンの公式サイトをご確認ください。")
    md_content.append("> ※本記事にはアフィリエイトリンクが含まれています。")

    # 個別記事のファイル名 (Jekyllの命名規則に従う)
    # ファイル名に時刻を含めることで、同じ日に複数回実行してもユニークなファイル名になる
    article_filename = f"_posts/{date_for_filename}-{today.strftime('%H%M%S')}-rakuten-summary.md"
    
    # 個別記事のファイルへの書き込み
    try:
        # _posts ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(article_filename), exist_ok=True)
        with open(article_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        print(f"Successfully generated Jekyll blog post: {article_filename}")
    except IOError as e:
        print(f"Error writing to file {article_filename}: {e}")

if __name__ == '__main__':
    generate_blog_post()