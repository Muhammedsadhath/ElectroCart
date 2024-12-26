from django.contrib import admin
from .models import ShippingAddress,Order,OrderItem
from django.contrib.auth.models import User

#register the model on admin section 
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)


#create an order item inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0  #delete the extra empty columns appearing in admin site

#extend our order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]            #show raed only fields which cannot be edited in admin site
    #we explicitly mentioned the column we want below in fields
    fields = ["user","full_name","email","shipping_address","date_ordered","amount_pay","shipped","date_shipped","invoice","paid"] 
    inlines = [OrderItemInline]

#unregister order model
admin.site.unregister(Order)

#re register the order model and orderadmin
admin.site.register(Order, OrderAdmin)


