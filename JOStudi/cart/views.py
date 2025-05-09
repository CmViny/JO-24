from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .cart import Cart
from offers.models import Offre
from uuid import UUID
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

def cart_summary(request):
    cart = Cart(request)
    cart_offres = cart.get_prods()
    return render(request, 'cart_summary.html', {'cart_offres': cart_offres})

def cart_add(request):
    cart = Cart(request)
    
    if request.method == "POST" and request.POST.get('action') == 'post':
        offre_id = request.POST.get("offre_id")
        type_billet = request.POST.get("type_billet")
        quantity = int(request.POST.get("quantity", 1))

        if offre_id and type_billet:
            cart_product = get_object_or_404(Offre, id=offre_id)
            cart.add(product=cart_product,quantity=quantity, type_billet=type_billet)

            cart_quantity = len(cart)

            messages.success(request, 'Produit ajouté au panier...')
            return JsonResponse({"qty": cart_quantity})
        
    return JsonResponse({"error": "Requête invalide"}, status=400)

def cart_update(request):
    cart = Cart(request)

    if request.method == "POST" and request.POST.get("action") == "post":
        key = request.POST.get("key")
        quantity = int(request.POST.get("quantity", 1))
        type_billet = request.POST.get("type_billet")

        if key and type_billet:
            offre_id = key.split('_')[0]
            product = get_object_or_404(Offre, id=offre_id)

            cart.update(product=product, quantity=quantity, type_billet=type_billet)

            updated_price = product.get_prix(type_billet)
            total_price = float(updated_price) * quantity

            return JsonResponse({
                "message": "Cart updated",
                "updated_price": f"{updated_price:.2f}",
                "total_price": f"{total_price:.2f}",
                "key": f"{offre_id}_{type_billet}"
            })

    return JsonResponse({"error": "Invalid request"}, status=400)


def cart_delete(request):
    cart = Cart(request)

    if request.method == "POST" and request.POST.get("action") == "delete":
        full_key = request.POST.get("offre_id")

        if full_key:
            raw_uuid = full_key.split('_')[0]

            try:
                offre_uuid = UUID(raw_uuid)
                product = get_object_or_404(Offre, id=offre_uuid)

                # Delete the product in the cart
                cart.delete(product=product)
                return JsonResponse({"message": "Item deleted", "cart_quantity": len(cart)})
            
            except (ValueError, ValidationError):
                return JsonResponse({"error": "Invalid UUID format"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)