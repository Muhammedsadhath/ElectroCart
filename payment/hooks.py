from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


@receiver(valid_ipn_received)
def paypal_payment_recieved(sender, **kwargs):
    #add 10 second delay for paypal to sent ipn data
    time.sleep(10)
    #grab the info the paypal sends
    paypal_obj = sender
    #grab the invoice
    my_invoice = str(paypal_obj.invoice)

    #match paypal invoice to the order invoice
    #look up the order
    my_Order = Order.objects.get(invoice=my_invoice)

    #record the order wa paid
    my_Order.paid = True
    #save the order
    my_Order.save()








    # print(paypal_obj)
    # print(f'amount paid: {paypal_obj.mc_gross}')