from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#create customer profile
class Profile(models.Model):
    user  = models.OneToOneField(User,on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User,auto_now=True)
    phone = models.CharField(max_length=10, blank=True)   #we made it char becuase soe ppl may type lik +91 765488383 etc or put spaces
    address1 = models.CharField(max_length=100, blank=True) 
    address2 = models.CharField(max_length=100, blank=True) 
    city = models.CharField(max_length=100, blank=True) 
    state = models.CharField(max_length=100, blank=True)     
    zipcode = models.CharField(max_length=100, blank=True)     
    country = models.CharField(max_length=100, blank=True)  
    old_cart = models.CharField(max_length=100, blank=True, null=True)  
   
    def __str__(self):
        return self.user.username
    
#create a user profile by default
def create_profile(sender,instance,created,**kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

#automate the profile thing
post_save.connect(create_profile, sender=User)




#category of products
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = 'categories'


#customer details
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

#All of the products
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def __str__(self):
        return self.name

#customer orders
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=50, default='',blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
#contact

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
