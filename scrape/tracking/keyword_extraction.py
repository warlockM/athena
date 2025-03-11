from pytrends.request import TrendReq
import requests

def get_google_trends_keywords(keyword, geo="US"):
    """
    Fetches related trending keywords from Google Trends.
    :param keyword: The main keyword to search trends for.
    :param geo: The geographical location (default is US).
    :return: A list of top related queries if available, otherwise an empty list.
    """
    pytrends = TrendReq()
    pytrends.build_payload([keyword], cat=0, timeframe="now 7-d", geo=geo, gprop="")
    trends = pytrends.related_queries().get(keyword, {}).get("top")
    return list(trends["query"].values) if trends is not None else []

def get_amazon_suggested_keywords(keyword):
    """
    Fetches Amazon auto-suggested keywords based on user input.
    :param keyword: The seed keyword for which suggestions are fetched.
    :return: A list of suggested keywords if successful, otherwise an empty list.
    """
    url = f"https://completion.amazon.com/api/2017/suggestions?session-id=123-4567890-1234567&customer-id=A1B2C3D4E5F6G7H8I9J0&request-id=12345678-1234-1234-1234-123456789012&q={keyword}&search-alias=aps"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("suggestions", [])  # Extract suggested keywords list
    return []
