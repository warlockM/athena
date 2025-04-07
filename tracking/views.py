from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ProductSnapshot

# Create your views here.

def tracker_list(request):
    """Return all tracking data from the ProductSnapshot table."""
    snapshots = ProductSnapshot.objects.all().values()
    print(snapshots)
    return JsonResponse(list(snapshots), safe=False)

def tracker_detail(request, product_id):
    """Return tracking data for a specific product."""
    snapshots = ProductSnapshot.objects.filter(product__id=product_id).values()
    if not snapshots:
        return JsonResponse({'error': 'No tracking data found for this product'}, status=404)
    return JsonResponse(list(snapshots), safe=False)
