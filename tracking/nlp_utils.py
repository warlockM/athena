import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from tracking.models import SEOKeywordTracking
from tracking.keyword_extraction import get_amazon_suggested_keywords, get_google_trends_keywords
import json
from scrape.models import Product

# Download necessary resources
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

# Define function for extracting keywords
def extract_keywords(text, product, url, top_n=5):
    product = product
    name = text
    url = url
    if not text:
        return []
    
    # Preprocess text
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    words = nltk.word_tokenize(text)
    words = [word for word in words if word not in stopwords.words('english') and len(word) > 2]
    
    # Convert list of words back to a single string
    processed_text = ' '.join(words)
    
    # Use TF-IDF to extract important words
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_text])
    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()
    
    # Get top N keywords
    keywords = [feature_array[i] for i in tfidf_scores.argsort()[-top_n:][::-1]]

    save_seo_keywords(keywords, product, name, url)
    #get_google_trends_keywords(keywords)
    #get_amazon_suggested_keywords(keywords)

    return keywords

def save_seo_keywords(keywords, product, name, url):
    try:
        print("Passed value check for keyword : ", keywords)
        
        SEO, created = SEOKeywordTracking.objects.update_or_create(
            product_id=Product.objects.get(id=product),
            defaults={
                "product_name": name,
                "product_url": url,
                "top_seo_keywords": keywords  # ✅ Proper place to pass list
            }
        )

        if created:
            print(f"✅ Keywords saved : ", SEO.top_seo_keywords)
        else:
            print(f"🔄 Keywords updated : ", SEO.top_seo_keywords)

    except Exception as e:
        print("🚨 Error in save_seo_keywords:", e)
        return []
    
    return keywords
    
