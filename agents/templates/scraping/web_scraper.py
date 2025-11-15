"""Webスクレイピングテンプレート"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
from urllib.parse import urljoin, urlparse
import re

class WebScraper:
    def __init__(self, delay=1):
        self.session = requests.Session()
        self.delay = delay  # リクエスト間隔（秒）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self, url, params=None):
        """ページ取得"""
        print(f"🌐 ページ取得: {url}")
        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)  # 丁寧なクローリング
            return response.text
        except requests.RequestException as e:
            print(f"❌ ページ取得エラー: {e}")
            return None
    
    def parse_html(self, html, parser='html.parser'):
        """HTML解析"""
        return BeautifulSoup(html, parser) if html else None
    
    def extract_links(self, soup, base_url, pattern=None):
        """リンク抽出"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if pattern:
                if re.search(pattern, full_url):
                    links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True)
                    })
            else:
                links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })
        
        return links
    
    def extract_articles(self, soup, title_selector, content_selector):
        """記事コンテンツ抽出"""
        articles = []
        
        titles = soup.select(title_selector)
        contents = soup.select(content_selector)
        
        for title, content in zip(titles, contents):
            articles.append({
                'title': title.get_text(strip=True),
                'content': content.get_text(strip=True),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return articles
    
    def save_data(self, data, filename, format='json'):
        """データ保存"""
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        if format == 'json':
            with open(f'{filepath}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                df.to_csv(f'{filepath}.csv', index=False, encoding='utf-8')
        
        print(f"💾 データ保存: {filepath}.{format}")
    
    def crawl_site(self, start_url, max_pages=10, link_pattern=None):
        """サイトクローリング"""
        visited = set()
        to_visit = [start_url]
        all_data = []
        
        page_count = 0
        
        while to_visit and page_count < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            print(f"🔍 クローリング: {current_url}")
            html = self.fetch_page(current_url)
            
            if html:
                soup = self.parse_html(html)
                
                # データ抽出（例: ニュース記事）
                articles = self.extract_articles(
                    soup, 
                    title_selector='h1, h2, .title, .headline',
                    content_selector='p, .content, .article'
                )
                
                all_data.extend(articles)
                
                # リンク抽出
                new_links = self.extract_links(soup, current_url, link_pattern)
                for link in new_links:
                    if link['url'] not in visited and link['url'] not in to_visit:
                        to_visit.append(link['url'])
                
                visited.add(current_url)
                page_count += 1
        
        return all_data

def main():
    """メイン実行関数"""
    print("🚀 Webスクレイピング開始")
    
    scraper = WebScraper(delay=1)
    
    try:
        # サンプルスクレイピング（実際のサイトに置き換えて使用）
        print("📝 サンプルスクレイピング実行中...")
        
        # 代わりにテストデータを生成
        sample_data = [
            {
                'title': 'サンプル記事1',
                'content': 'これはサンプル記事の内容です。',
                'timestamp': '2024-01-01 10:00:00',
                'url': 'https://example.com/article1'
            },
            {
                'title': 'サンプル記事2', 
                'content': '別のサンプル記事内容です。',
                'timestamp': '2024-01-01 11:00:00',
                'url': 'https://example.com/article2'
            }
        ]
        
        # データ保存
        scraper.save_data(sample_data, 'scraped_articles', 'json')
        scraper.save_data(sample_data, 'scraped_articles', 'csv')
        
        print(f"✅ スクレイピング完了 - {len(sample_data)}件のデータ取得")
        
    except Exception as e:
        print(f"❌ スクレイピングエラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
