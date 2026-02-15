from django.shortcuts import render, redirect

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



#! FeedBack 


from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Feedback

@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback form submission"""
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        rating = request.POST.get('rating')
        message_text = request.POST.get('message', '').strip()
        
        # Validate required fields
        if not all([name, email, rating, message_text]):
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect('core:home')
        
        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Évaluation invalide.")
            return redirect('core:home')
        
        # Create feedback
        feedback = Feedback.objects.create(
            name=name,
            email=email,
            rating=rating,
            message=message_text
        )
        
        # Success message
        messages.success(
            request, 
            f"Merci {name}! Votre feedback a été envoyé avec succès. Nous apprécions votre retour!"
        )
        
        # Redirect to home with success anchor
        return redirect('core:home')
        
    except Exception as e:
        messages.error(
            request, 
            "Une erreur s'est produite lors de l'envoi de votre feedback. Veuillez réessayer."
        )
        return redirect('core:home')