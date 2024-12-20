from store.models import Product,Profile
from django.contrib import messages
class Cart():
    def __init__(self,request):
        self.session = request.session
        #get request
        self.request = request
        #get the current session key if it exists
        cart = self.session.get('session_key')

        #if the user is new-no session key,then create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        #make sure cart is avilable on all pages of site
        self.cart = cart

    def db_add(self,product,quantity):
        product_id = str(product)
        product_qty = str(quantity)

        #logic
        if product_id in self.cart:
            messages.success(self.request, "Item exists in the cart")

        else:
            #self.cart[product_id] = {'price' : str(product.price)}
            self.cart[product_id] = int(product_qty)
            # messages.success(self.request, "Product added to cart")

        self.session.modified = True   

        #deal with logged in user
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #convert {'3':1,'2':4} to {"3":1,"2":4}----python dict to json 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")  # ' to "
            #save the carty to the Profile model
            current_user.update(old_cart=carty)
    
    def add(self,product,quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        #logic
        if product_id in self.cart:
            messages.success(self.request, "Item exists in the cart")
        else:
            #self.cart[product_id] = {'price' : str(product.price)}
            self.cart[product_id] = int(product_qty)
            messages.success(self.request, "Product added to cart")

        self.session.modified = True   

        #deal with logged in user
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #convert {'3':1,'2':4} to {"3":1,"2":4}----python dict to json 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")  # ' to "
            #save the carty to the Profile model
            current_user.update(old_cart=carty)

    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        #get id's from cart
        product_ids = self.cart.keys()
        #use id's to look up products in db models
        products = Product.objects.filter(id__in = product_ids)
        #retuen those looked up products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self,product,quantity):
        product_id =str(product)
        product_qty =str(quantity)
        
        #get cart
        ourcart = self.cart
        #update dictionary/cart
        ourcart[product_id] = product_qty

        self.session.modified =True

        thing = self.cart

        #deal with logged in user
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #convert {'3':1,'2':4} to {"3":1,"2":4}----python dict to json 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")  # ' to "
            #save the carty to the Profile model
            current_user.update(old_cart=carty)

        return thing
    
        
    
    def delete(self,product):
        product_id = str(product)
        #delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        #deal with logged in user
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            #convert {'3':1,'2':4} to {"3":1,"2":4}----python dict to json 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")  # ' to "
            #save the carty to the Profile model
            current_user.update(old_cart=carty)
        

    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0

        for key, value in quantities.items():
            key = int(key)
            value = int(value)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total += product.sale_price * value
                    else:
                        total += product.price * value
        return total
