import os
import requests
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

load_dotenv()  # Load environment variables from .env

class ShopifyProductListView(APIView):
    def get(self, request):
        shop_name = os.getenv("SHOPIFY_STORE_DOMAIN")
        api_key = os.getenv("SHOPIFY_API_KEY")
        password = os.getenv("SHOPIFY_ACCESS_TOKEN")

        if not all([shop_name, api_key, password]):
            return Response({"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST)

        url = f"https://{api_key}:{password}@{shop_name}/admin/api/2023-10/products.json"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                products = response.json().get("products", [])
                return Response(products, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch products", "details": response.text}, status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
