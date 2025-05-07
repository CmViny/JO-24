class Cart():
    def __init__(self, request):
        self.session = request.session 

        #Get the current session key
        cart = self.session.get('cart_key')

        #If the session key does not exist, create a new one
        if 'cart_key' not in request.session:
            cart = self.session['cart_key'] = {}
        
        self.cart = cart