class Cart():
    def __init__(self, request):
        self.session = request.session 

        #Get the current session key
        cart = self.session.get('cart_key')

        #If the session key does not exist, create a new one
        if 'cart_key' not in request.session:
            cart = self.session['cart_key'] = {}
        
        self.cart = cart
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

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