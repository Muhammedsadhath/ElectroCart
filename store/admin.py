from django.contrib import admin
from .models import Category,Customer,Product,Order,Profile,Contact
from django.contrib.auth.models import User


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)


#mix profile info and uer info
class ProfileInline(admin.StackedInline):
    model = Profile

#extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username","first_name","last_name","email"]
    inlines = [ProfileInline]

#unregister the old way
admin.site.unregister(User)

#re-register the new way
admin.site.register(User, UserAdmin)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'submitted_at')  