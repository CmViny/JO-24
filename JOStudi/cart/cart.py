from offers.models import Offre
from accounts.models import Utilisateur

class Cart():
    def __init__(self, request):
        self.session = request.session 

        if 'cart_key' not in self.session:
            self.session['cart_key'] = {}
        self.cart = self.session['cart_key']

    
    def __len__(self):
        return len(self.cart)

    
    def add(self, product, quantity=1, type_billet='solo'):
        product_id = str(product.id)
        key = f"{product_id}_{type_billet}"  # clé unique pour chaque type

        if key in self.cart:
            self.cart[key]['quantity'] += int(quantity)
        else:
            self.cart[key] = {
                'price': str(product.get_prix(type_billet)),
                'quantity': int(quantity),
                'title' : str(product.titre),
                'type_billet': type_billet
            }
        self.session.modified = True
        # self.persistence()


    def delete(self, product: object):
        product_id = str(product.id)
        keys_to_remove = [key for key in self.cart if key.startswith(f"{product_id}_")]
        for key in keys_to_remove:
            del self.cart[key]

        self.session.modified = True

        # self.persistence() 


    def update(self, product: object, quantity: int, type_billet: str):
        offre_id = str(product.id)
        key = f"{offre_id}_{type_billet}"

        keys_to_remove = [k for k in self.cart.keys() if k.startswith(f"{offre_id}_")]
        for k in keys_to_remove:
            self.cart.pop(k, None)

        # Add the new entry with the updated quantity
        self.cart[key] = {
            "quantity": quantity,
            "type_billet": type_billet,
            "price": str(product.get_prix(type_billet))
        }

        self.session.modified = True
        # self.persistence() 


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
