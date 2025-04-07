import requests
from bs4 import BeautifulSoup
import re
import json
import random
import time
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import trafilatura
from trafilatura import extract
from scrape.models import Product, Seller, Platform
from django.core.exceptions import ValidationError
from tracking.models import ProductSnapshot
from django.utils.timezone import now
from django.db.utils import IntegrityError
import logging
from tracking import keyword_extraction, nlp_utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/85.0",
]

# def get_random_proxy():
#     """Select a random proxy from the list"""
#     return {"http": random.choice(PROXIES), "https": random.choice(PROXIES)}

def scrape_amazon_product(url):
    """
    Function to scrape product details from an Amazon product URL.
    
    Args:
        url (str): The Amazon product URL to scrape
        
    Returns:
        dict: Dictionary containing product name, price, rating, review count and seller info
    """
    # Updated user agents including Brave, Opera, and DuckDuckGo browsers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Brave/1.43.114',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Brave/1.43.114',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Brave/1.43.114',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 OPR/87.0.4390.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 OPR/87.0.4390.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 OPR/87.0.4390.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 DuckDuckGo/5',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 DuckDuckGo/5'
    ]

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    # proxy = get_random_proxy()

    # Determine the correct domain based on the URL
    amazon_domain = "www.amazon.com"
    if "amazon.in" in url:
        amazon_domain = "www.amazon.in"
    elif "amazon.co.uk" in url:
        amazon_domain = "www.amazon.co.uk"
    # Add more Amazon domains as needed
    
    # Add headers to simulate a browser request
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'sec-ch-ua': '"Brave";v="101", "Chromium";v="101", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-GPC': '1',  # Brave specific header for Global Privacy Control
        'Cache-Control': 'max-age=0',
        'Referer': f"https://{amazon_domain}/",
    }
    
    # Add a small delay to be more respectful of Amazon's servers
    time.sleep(random.uniform(1, 3))
    
    try:
        # Make request to the Amazon URL
        print(f"Fetching data from: {url}")
        session = requests.Session()
        
        # First visit the homepage to get cookies
        homepage_url = f"https://{amazon_domain}/"
        session.get(homepage_url, headers=headers, timeout=15, verify = False)
        
        # Now visit the product page
        response = session.get(url, headers=headers, timeout=15, verify=False)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response content: {response.text[:500]}...")  # Print the first 500 chars for debugging
            return None
            
        # Verify we received some content
        if not response.content:
            print("Error: Empty response received")
            return None
        
        extracted_text = extract(response.content)
        product_name, price, rating, reviews_count, seller = None, None, None, None, None
    
        if extracted_text:
            lines = extracted_text.split('\n')  # Splitting text into lines for easier parsing
            for line in lines:
                if "₹" in line:  # Searching for price
                    price = line.strip()
                elif "out of 5 stars" in line:  # Searching for rating
                    rating = line.split()[0]
                elif "ratings" in line or "reviews" in line:  # Searching for reviews count
                    reviews_count = line.split()[0]
                elif "by" in line:  # Searching for seller information
                    seller = line.strip()

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug: Check if we got a captcha page
        if "captcha" in response.text.lower() or "robot check" in response.text.lower():
            print("Error: Amazon returned a CAPTCHA or robot check page")
            return None
            
        # Extract product information
        product_data = {}
        product_data['url'] = url
        # Debug: Check if we can find basic elements to confirm it's a product page

        product_title = soup.select_one('#productTitle')
        
        if not product_title:
            # Try alternative selectors for the product title
            alt_title_selectors = [
                '.product-title-word-break',
                '.a-size-large.product-title-word-break',
                '.product-title',
            ]
            
            for selector in alt_title_selectors:
                product_title = soup.select_one(selector)
                if product_title:
                    break
                    
            if not product_title:
                print("Error: Product title element not found, this might not be a valid product page")
                # Save the HTML for debugging (optional)
                with open('amazon_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return None

        # Get product name
        product_data['name'] = product_title.get_text().strip()

        # Get product price
        # Try multiple price selectors for different Amazon layouts
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text_content = trafilatura.extract(downloaded)
            if text_content:
                # print(f"\nDebug - First 200 chars of extracted content:\n{text_content[:200]}")

                    # Look for price patterns in the extracted text
                price_patterns = [
                    r'₹\s*[\d,]+\.?\d{0,2}',  # ₹XX.XX or ₹XX format
                    r'Rs\.?\s*[\d,]+\.?\d{0,2}',  # Rs. XX.XX format
                    r'INR\s*[\d,]+\.?\d{0,2}',  # INR XX.XX format
                    r'Price:\s*₹\s*[\d,]+\.?\d{0,2}',  # Price: ₹XX.XX format
                ]

                for pattern in price_patterns:
                    matches = re.findall(pattern, text_content)
                    if matches:
                        # Take the first price found
                        price_str = matches[0].replace('₹', '').replace('Rs.', '').replace('INR', '').replace(',', '').strip()
                        # try:
                        #     price = float(price_str)
                        #     if price > 0:  # Validate price is positive
                        #         product_data['price'] = price
                        # except (ValueError, AttributeError):
                        #     continue
                        try:
                            price = float(price_str)  # ***** Convert to Decimal here instead of float to avoid later errors *****
                            if price > 0:
                                product_data['price'] = price
                        except (ValueError, AttributeError):
                            continue

        price_selectors = [
            '.a-price .a-offscreen',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-color-price',
            '.a-price-whole',
            '.a-price',
            '#price',
            '.priceToPay .a-offscreen',
            '#corePrice_feature_div .a-offscreen',
            '#corePriceDisplay_desktop_feature_div .a-offscreen'
        ]
        
        
        for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    # print(f"Debug - Found price element: {price_text}")

                    # Extract numbers from price text
                    price_numbers = re.findall(r'[\d,.]+', price_text)
                    if price_numbers:
                        price_str = price_numbers[0].replace(',', '')
                        # try:
                        #     price = float(price_str)
                        #     if price > 0:
                        #         product_data['price'] = price
                        # except ValueError:
                        #     continue
                        try:
                            price = float(price_str)  # ***** Use Decimal instead of float to match database expectations *****
                            if price > 0:
                                product_data['price'] = price
                        except ValueError:
                            continue
                    
        # Get rating
        rating_selectors = [
            'span[data-hook="rating-out-of-text"]', 
            '.a-icon-alt',
            '#acrPopover',
            '.a-icon-star'
        ]
        
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text().strip()
                # Extract the rating number (e.g., "4.5 out of 5" -> "4.5")
                rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                if rating_match:
                    product_data['rating'] = rating_match.group(1)
                    break
                
        if 'rating' not in product_data:
            product_data['rating'] = 'Rating not found'
        
        # Get number of reviews
        review_selectors = [
            '#acrCustomerReviewText', 
            '[data-hook="total-review-count"]',
            '.a-size-base.a-color-secondary'
        ]
        
        for selector in review_selectors:
            reviews_elem = soup.select_one(selector)
            if reviews_elem:
                reviews_text = reviews_elem.get_text().strip()
                # Extract the number (e.g., "1,234 ratings" -> "1234")
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    reviews = reviews_match.group(1).replace(',', '')
                    product_data['reviews_count'] = reviews
                    break
                    
        if 'reviews_count' not in product_data:
            product_data['reviews_count'] = 'Reviews count not found'
        
        # Extract seller information based on the provided HTML structure
        byline_info = soup.select_one('#bylineInfo')
        if byline_info:
            # Extract seller name
            seller_text = byline_info.get_text().strip()
            if 'Visit the' in seller_text:
                seller_name = seller_text.replace('Visit the', '').replace('Store', '').strip()
            elif 'Brand:' in seller_text:
                seller_name = seller_text.replace('Brand:', '').strip()
            else:
                seller_name = seller_text.strip()
            
            product_data['seller_name'] = seller_name
            
            # Extract seller URL
            href = byline_info.get('href')
            if href:
                # Format the URL correctly
                if href.startswith('/'):
                    seller_url = f"https://{amazon_domain}{href}"
                else:
                    seller_url = href
                    
                product_data['seller_page'] = seller_url
        
        # Fallback options if the primary method fails
        if 'seller_name' not in product_data:
            # Try alternative selectors
            alt_selectors = [
                'a.a-link-normal[href*="/stores/"]',
                '.product-by-line a',
                '#merchant-info a',
                '.a-row.a-size-base a[href*="/stores/"]',
                '.a-section a[href*="/stores/"]'
            ]
            
            for selector in alt_selectors:
                seller_elem = soup.select_one(selector)
                if seller_elem:
                    text = seller_elem.get_text().strip()
                    href = seller_elem.get('href', '')
                    
                    if text:
                        product_data['seller_name'] = text.replace('Visit the', '').replace('Store', '').replace('Brand:', '').strip()
                    
                    if href:
                        if href.startswith('/'):
                            product_data['seller_page'] = f"https://{amazon_domain}{href}"
                        else:
                            product_data['seller_page'] = href
                    
                    break
        
        # If still no seller found, set a default
        if 'seller_name' not in product_data:
            product_data['seller_name'] = "Couldn't get"
            product_data['seller_page'] = "couldn't get"
        
        save_seller(product_data['seller_name'], product_data['seller_page'])

        save_product_data(product_data)

        return product_data

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())  # Print full stack trace
        return None


#code to save product data in DB

def save_product_data(product_data):
    """
    Saves the scraped product information into the database.
    
    Args:
        product_data (dict): Dictionary containing product details.
    
    Returns:
        Product instance if saved successfully, else None.
    """
    try:
        # Validate required fields
        required_fields = ["name", "url", "price"]
        missing_fields = [field for field in required_fields if not product_data.get(field)]
        
        if missing_fields:
            print(f"Error: Missing required product fields - {', '.join(missing_fields)}")
            return None

        # Ensure price is a valid number
        try:
            price = float(product_data["price"])
            if price < 0:
                print("Error: Price cannot be negative.")
                return None
        except ValueError:
            print("Error: Invalid price value.")
            return None

        # Set default values for optional fields
        rating = product_data.get("rating", "N/A")
        review_count = product_data.get("reviews_count", 0)

        # Create or update the product
        product, created = Product.objects.update_or_create(
            url=product_data["url"],  # Ensure uniqueness based on URL
            defaults={
                "name": product_data["name"],
                "price": price,
                "rating": rating,
                "review_count": review_count,
            }
        )

        if created:
            print(f"✅ Product saved: {product.name}")
        else:
            print(f"🔄 Product updated: {product.name}")

    #   Store a new ProductSnapshot whenever product data is updated

        save_product_snapshot(product, price, rating, review_count)
        
    #   SEO keyword extractor
        seo_keywords = nlp_utils.extract_keywords(product.name, product.id, product.url)

    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

    return None

#code to save seller data in DB

def save_seller(seller_name, seller_url):

    """
    Function to save seller details in the Seller model.

    Args:
        seller_name (str): Name of the seller
        seller_url (str): URL of the seller page
    
    Returns:
        Seller: The created or retrieved Seller instance
    """
    if not seller_name or not seller_url:
        print("Error: Missing required seller fields")
        return None

    # Get or create the seller record
    seller, created = Seller.objects.get_or_create(
        name=seller_name.strip(),
        defaults={'url': seller_url.strip()}
    )

    if created:
        print(f"✅ New seller saved: {seller_name}")
    else:
        print(f"ℹ️ Seller already exists: {seller_name}")

    return seller

#code to save product snapshot in DB

def save_product_snapshot(product, price, rating, reviews_count):
    try:
        # print("🔍 Debugging product_data:", json.dumps({
        #     "price": price,
        #     "rating": rating,
        #     "reviews_count": reviews_count  # * Added to verify extraction
        # }, indent=2, default=float))

        # * Ensure proper type conversion before saving
        price = float(price) if price is not None else 0.0  # * Handles None values
        rating = float(rating) if rating is not None else 0.0  # * Handles None values
        review_count = int(reviews_count) if reviews_count is not None else 0  # * Ensures proper conversion

        # Get the last snapshot for this product
        last_snapshot = ProductSnapshot.objects.filter(product=product).order_by('-captured_at').first()

        # Calculate deltas (default to None if no previous snapshot)
        price_delta = None
        rating_delta = None
        review_count_delta = None

        if last_snapshot:
            if last_snapshot.price is not None and price is not None:
                price_delta = price - last_snapshot.price

            if last_snapshot.rating is not None and rating is not None:
                rating_delta = rating - last_snapshot.rating

            if last_snapshot.reviews_count is not None and review_count is not None:
                review_count_delta = review_count - last_snapshot.reviews_count

        # print("✅ Final Values - Price:", price, "Rating:", rating, "Reviews Count:", review_count)  # * Debug log before saving

        ProductSnapshot.objects.create(
            product=product,
            price=price,
            rating=rating,
            reviews_count=review_count,  # * Ensured correct variable
            delta_price=price_delta,
            delta_rating=rating_delta,
            delta_review_count=review_count_delta,
            captured_at=now()
        )
        print(f"✅ Product snapshot saved for: {product.name}")
    except Exception as e:
        logger.error(f"⚠️ Unexpected error while saving product snapshot: {e}")
