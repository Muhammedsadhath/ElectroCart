from django.shortcuts import render,redirect
from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForm
from payment.models import ShippingAddress,Order,OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product,Profile
import datetime


#some paympal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #unique user id for duplicate orders

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






def billing_info(request):
    if request.method == "POST":  # Restrict to POST requests
        # Retrieve cart details
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Capture and validate shipping information from POST data
        my_shipping = request.POST
        if not my_shipping or not all(key in my_shipping for key in [
            'shipping_full_name', 'shipping_email', 'shipping_address1', 
            'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country'
        ]):
            messages.error(request, "Incomplete shipping information.")
            return redirect('checkout')

        # Store shipping information in session
        request.session['my_shipping'] = my_shipping

        # Create a unique invoice number
        my_invoice = str(uuid.uuid4())

        # Create PayPal form data
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECIEVER_EMAIL,
            'amount': totals,
            'item_name': 'book order',
            'no_shipping': '2',
            'invoice': my_invoice,
            'currency_code': 'USD',
            'notify_url': f'https://{host}{reverse("paypal-ipn")}',
            'return_url': f'https://{host}{reverse("payment_success")}',
            'cancel_url': f'https://{host}{reverse("payment_failed")}',
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Process order creation
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = "\n".join([
            my_shipping['shipping_address1'],
            my_shipping.get('shipping_address2', ''),
            my_shipping['shipping_city'],
            my_shipping['shipping_state'],
            my_shipping['shipping_zipcode'],
            my_shipping['shipping_country']
        ])

        # Check if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_pay=totals, invoice=my_invoice)
            create_order.save()
            order_id = create_order.pk

            # Create order items
            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                quantity = quantities.get(str(product.id), 0)
                OrderItem.objects.create(
                    order_id=order_id, product_id=product.id, user=user,
                    quantity=quantity, price=price
                )

            # Clear the user's cart
            Profile.objects.filter(user__id=user.id).update(old_cart="")

        else:  # Guest user
            create_order = Order(full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_pay=totals, invoice=my_invoice)
            create_order.save()
            order_id = create_order.pk

            # Create order items
            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                quantity = quantities.get(str(product.id), 0)
                OrderItem.objects.create(
                    order_id=order_id, product_id=product.id,
                    quantity=quantity, price=price
                )

        # Render billing form for guest users
        billing_form = PaymentForm()
        return render(request, "billing_info.html", {
            'paypal_form': paypal_form,
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_info': my_shipping,
            'billing_form': billing_form
        })
    else:
        messages.error(request, "Access denied")
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
    #delete the browser cart
    #first get the cart
    #delete our cart after checkout
    for key in list(request.session.keys()):
        if key == "session_key":
        #delete the key
            del request.session[key]
    return render(request,'payment_success.html')

def payment_failed(request):
    return render(request,'payment_failed.html')
