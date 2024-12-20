from django.shortcuts import render,redirect
from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForm
from payment.models import ShippingAddress,Order,OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product,Profile
import datetime

#this is for admin page
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get the order
        order = Order.objects.get(id=pk)  #If the URL is /orders/18/, the pk will be 18....Django fetches the Order object where id=18.
        #get the order items
        items = OrderItem.objects.filter(order=pk) #If the URL is /orders/18/ and the he filter(order=18) query will return:python book (2x),php book (1x)

        if request.POST:
            status = request.POST.get('shipping_status')
            #check if true or false
            now = datetime.datetime.now()
            if status == "true":                            #if the order is marked as not shipped
                #get the order
                order = Order.objects.filter(id = pk)
                #once we get order update the status
                order.update(shipped = True, date_shipped = now)
            else:                                            #if order is marked as shipped
                #get the order
                order = Order.objects.filter(id = pk)
                #once we get order update the status
                order.update(shipped = False, date_shipped = now)
            messages.success(request,"shipping status updated")
            return redirect('home')

        return render(request,"orders.html",{'order':order,'items':items})
    else:
        messages.success(request,("Access denied"))
        return redirect('home')

#this is for admin page
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST.get('shipping_status')
            num = request.POST.get('num')
            #get the order
            order = Order.objects.filter(id = int(num))
            #grab date and time
            now = datetime.datetime.now()
            #update order
            order.update(shipped = True, date_shipped = now)
            messages.success(request,"shipping status updated")
            return redirect('home')
        return render(request, "not_shipped_dash.html",{'orders':orders})
    else:
        messages.success(request,("Access denied"))
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST.get('shipping_status')
            num = request.POST.get('num')
            order = Order.objects.filter(id=int(num))
            now = datetime.datetime.now()
            order.update(shipped=False, date_shipped=now)
            messages.success(request, "Shipping status updated")
            return redirect('home')

        return render(request, "shipped_dash.html", {'orders': orders})
    else:
        messages.error(request, "Access denied")
        return redirect('home')



def process_order(request):   
    if request.POST:                   #if you use this then you cant enter the page via typing in url,u have to click button or something
        cart = Cart(request)
        cart_products = cart.get_prods()  
        quantities = cart.get_quants()
        totals = cart.cart_total()

        #get the billing informaation
        payment_form = PaymentForm(request.POST or None)
        #get shipping session data
        my_shipping = request.session.get('my_shipping')
        
        #gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        #create shipping address from session info
        shipping_address = f"{ my_shipping['shipping_address1']}\n{ my_shipping['shipping_address2']}\n{ my_shipping['shipping_city']}\n{ my_shipping['shipping_state']}\n{ my_shipping['shipping_zipcode']}\n{ my_shipping['shipping_country']}"
        amount_paid = totals

        #create an order
        if request.user.is_authenticated:  #logged in
            user = request.user
            #create order
            create_order = Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,amount_pay=amount_paid)
            create_order.save()
            
            #add order items
            #get order id
            order_id = create_order.pk

            #get product info
            for product in cart_products:
                #get product id
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                #get quantity
                for key,value in quantities.items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItem(order_id= order_id, product_id=product_id,user=user,quantity=value ,price=price )
                        create_order_item.save()
            
            #delete our cart after checkout
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete the key
                    del request.session[key]
                
            #delete cart from databse (old_cart field in store-models-Profile)
            current_user = Profile.objects.filter(user__id=request.user.id)
            #delete the shopping cart in db called old_cart
            current_user.update(old_cart="")


            messages.success(request,("Order placed"))
            return redirect('home')

        
            
        else:   #not logged in 
                #create order
            create_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_pay=amount_paid)
            create_order.save()

            #add order items
            #get order id
            order_id = create_order.pk

            #get product info
            for product in cart_products:
                #get product id
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                #get quantity
                for key,value in quantities.items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItem(order_id= order_id, product_id=product_id,quantity=value ,price=price )
                        create_order_item.save()

            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete the key
                    del request.session[key]

            messages.success(request,("Order placed"))
            return redirect('home')

       
    else:
        messages.success(request,("access denied"))
        return redirect('home')


# def process_order(request):
#     if request.POST:
#         cart = Cart(request)
#         cart_products = cart.get_prods()  
#         quantities = cart.get_quants()
#         totals = cart.cart_total()

#         my_shipping = request.session.get('my_shipping')

#         # Gather order info
#         full_name = my_shipping['shipping_full_name']
#         email = my_shipping['shipping_email']
#         shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
#         amount_paid = totals

#         # Create an order
#         if request.user.is_authenticated:  # Logged in
#             user = request.user
#         else:  # Guest checkout
#             user = None

#         create_order = Order(
#             user=user,
#             full_name=full_name,
#             email=email,
#             shipping_address=shipping_address,
#             amount_pay=amount_paid
#         )
#         create_order.save()

#         # Add order items
#         for product in cart_products:
#             product_id = product.id
#             price = product.sale_price if product.is_sale else product.price
#             quantity = quantities.get(str(product_id), 0)  # Ensure product_id matches quantities keys
            
#             if quantity > 0:  # Avoid adding items with no quantity
#                 create_order_item = OrderItem(
#                     order=create_order,
#                     product=product,
#                     user=user,
#                     quantity=quantity,
#                     price=price
#                 )
#                 create_order_item.save()
        
#         # Clear cart after checkout
#         if 'cart' in request.session:
#             del request.session['cart']
#             request.session.modified = True

#         messages.success(request, "Order placed successfully.")
#         return redirect('home')
#     else:
#         messages.error(request, "Access denied.")
#         return redirect('home')




def billing_info(request):
    if request.POST: #if you use this then you cant enter the page via typing in url,u have to click button or something
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()  
        quantities = cart.get_quants()
        totals = cart.cart_total()

        #create a session with shipping info
        my_shipping =request.POST
        request.session['my_shipping'] = my_shipping

        billing_form = PaymentForm()
        #checking wheather the user is logged in
        if request.user.is_authenticated:
            #get the billing form
            
            return render(request, "billing_info.html", {'cart_products': cart_products,'quantities' : quantities,'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})

        else:
            return render(request, "billing_info.html", {'cart_products': cart_products,'quantities' : quantities,'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})


        shipping_form = request.POST
        return render(request, "billing_info.html", {'cart_products': cart_products,'quantities' : quantities,'totals':totals,'shipping_form':shipping_form})
    else:
        messages.success(request,("access denied"))
        return redirect('home')
      


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()  
    quantities = cart.get_quants()
    totals = cart.cart_total()
    if request.user.is_authenticated:
        #checkout as logged in user
        #shipping user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #shipping form
        shipping_form = ShippingForm(request.POST or None,instance=shipping_user)
        return render(request, "checkout.html", {'cart_products': cart_products,'quantities' : quantities,'totals':totals,'shipping_form':shipping_form})
    else:
        #checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "checkout.html", {'cart_products': cart_products,'quantities' : quantities,'totals':totals,'shipping_form':shipping_form})






def payment_success(request):
    return render(request,'payment_success.html')

