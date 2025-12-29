from django.shortcuts import render

# Create your views here.
def index1(request):
    return render(request,'core/index1.html')

def index(request):
    return render(request,'core/index.html')