import requests
from bs4 import BeautifulSoup
import re
import json
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from . import scrappers

def scrape_amazon_product(request):
    url = request.GET.get('url')
    product_data = {}
    if not url or not url.startswith('https://www.amazon'):
        print("Error: Invalid URL. Please provide a valid Amazon product URL.")
        return None
    
    product_data = scrappers.scrape_amazon_product(url)
    print(product_data)
    # Print the results to console
    if product_data is None:
        return JsonResponse({"error": "Failed to retrieve product data."}, status=500)
    
    # return JsonResponse(product_data)
    return HttpResponse("Success")

def hello(request):
    return HttpResponse("hey")


