import feedparser

def get_google_news(keyword, num_results=3):
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_items = []
    for entry in feed.entries[:num_results]:
        news_items.append({
            'title': entry.title,
            'link': entry.link
        })
    return news_items

# 핵심 수정: 괄호 안에 'keywords'가 반드시 있어야 합니다! [cite: 2026-03-07]
def fetch_all_categories(keywords):
    results = {}
    # 비타님이 입력하신 키워드들을 하나씩 순회하며 뉴스를 찾습니다. [cite: 2026-03-07]
    for keyword in keywords:
        items = get_google_news(keyword.strip(), num_results=1)
        results[keyword.strip()] = items
    return results