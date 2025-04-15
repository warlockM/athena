# shopify_integration/services.py
import shopify
from django.conf import settings


def activate_shopify_session():
    shop_url = f"https://{settings.SHOPIFY_STORE_DOMAIN}/admin"
    shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)
    session = shopify.Session(settings.SHOPIFY_STORE_DOMAIN, "2023-04", settings.SHOPIFY_ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


def get_products():
    activate_shopify_session()
    return shopify.Product.find()


def update_product_price(product_id, new_price):
    activate_shopify_session()
    product = shopify.Product.find(product_id)
    if product.variants:
        product.variants[0].price = new_price
        product.save()
        print(f"✅ Price updated for product {product_id} to {new_price}")
    else:
        print(f"⚠️ No variants found for product {product_id}")

