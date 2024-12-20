from .cart import Cart

# create context processors so our cart work on all pages

def cart(request):
    return {'cart':Cart(request)}