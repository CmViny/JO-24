from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .cart import Cart
from offers.models import Offre


def cart_summary(request):
    return render(request, 'cart_summary.html', {})

def cart_add(request):
    cart = Cart(request)
    
    if request.method == "POST" and request.POST.get('action') == 'post':
        offre_id = request.POST.get("offre_id")
        type_billet = request.POST.get("type_billet")

        if offre_id and type_billet:
            cart_product = get_object_or_404(Offre, id=offre_id)
            cart.add(product=cart_product, type_billet=type_billet)

            cart_quantity = len(cart)

            messages.success(request, 'Product Added To Cart...')
            return JsonResponse({"qty": cart_quantity})
        
    return JsonResponse({"error": "Requête invalide"}, status=400)

def cart_delete(request):
    pass

def cart_update(request):
    pass