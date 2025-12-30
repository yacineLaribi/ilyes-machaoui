from django.shortcuts import render

# Create your views here.
def index1(request):
    return render(request,'core/index1.html')

def index(request):
    return render(request,'core/index.html')


from django.http import JsonResponse
from restaurant.models import Order
#!Polling for the order admin
def latest_order_meta(request):
    last = Order.objects.order_by('-id').first()
    return JsonResponse({
        "last_id": last.id if last else 0,
        "count": Order.objects.count()
    })
