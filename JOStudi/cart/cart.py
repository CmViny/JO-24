from offers.models import Offre
from accounts.models import Utilisateur
import json 

class Cart():
    def __init__(self, request):
        self.session = request.session 
    
        # Get request
        self.request = request

        # Get the current session key if it exist 
        cart = self.session.get('session_key')

        # If the session key does not exist, create a new session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        # Cart available on all pages of site
        self.cart = cart

    def __len__(self):
        return len(self.cart)
    
    def persistence(self):
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get current user profile
            current_user = Utilisateur.objects.filter(user__id=self.request.user.id)

            # Convert cart dict to JSON
            carty = json.dumps(self.cart)

            # Update `old_cart` field in model
            current_user.update(old_cart=carty)

    def db_add(self, product: object, quantity: int, type_billet='solo'):
        product_id = str(product.id)
        key = f"{product_id}_{type_billet}"

        if key not in self.cart:
            self.cart[key] = {
                'id': product_id,
                'price': str(product.get_prix(type_billet)),
                'quantity': int(quantity),
                'title': str(product.titre),
                'type_billet': type_billet
            }

        self.session.modified = True
        self.persistence()

    
    def add(self, product, quantity=1, type_billet='solo'):
        product_id = str(product.id)
        key = f"{product_id}_{type_billet}"

        if key in self.cart:
            self.cart[key]['quantity'] += int(quantity)
        else:
            self.cart[key] = {
                'id': product_id,
                'price': str(product.get_prix(type_billet)),
                'quantity': int(quantity),
                'title': str(product.titre),
                'type_billet': type_billet
            }

        self.session.modified = True
        self.persistence()


    def delete(self, product: object):
        product_id = str(product.id)
        keys_to_remove = [key for key in self.cart if key.startswith(f"{product_id}_")]
        for key in keys_to_remove:
            del self.cart[key]

        self.session.modified = True

        self.persistence() 


    def update(self, product: object, quantity: int, type_billet: str):
        offre_id = str(product.id)
        key = f"{offre_id}_{type_billet}"

        keys_to_remove = [k for k in self.cart.keys() if k.startswith(f"{offre_id}_")]
        for k in keys_to_remove:
            self.cart.pop(k, None)

        self.cart[key] = {
            'id': offre_id,
            "quantity": quantity,
            "type_billet": type_billet,
            "price": str(product.get_prix(type_billet))
        }

        self.session.modified = True
        self.persistence() 


    def get_prods(self):
        items = []

        for key, item in self.cart.items():
            offre_id = key.split('_')[0]
            try:
                offre = Offre.objects.get(id=offre_id)
                items.append({
                    'offre': offre,
                    'quantity': item['quantity'],
                    'type_billet': item['type_billet'],
                    'price': item['price'],
                    'key': key
                })
            except Offre.DoesNotExist:
                continue

        return items
    
    def get_totals(self):
        total = 0
        # Parcours tous les éléments du panier et ajoute au total
        for item in self.cart.values():
            total += float(item['price']) * item['quantity']
        return total

    def clear(self):
        self.session['session_key'] = {}
        self.session.modified = True
