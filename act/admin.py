from django.contrib import admin

from .models import Customer, VirtualAccount, CustomerLotPayment, CustomerLot

admin.site.index_title = 'Аукцион'
admin.site.site_header = 'Аукцион'


admin.site.register(Customer)
admin.site.register(VirtualAccount)
admin.site.register(CustomerLot)
admin.site.register(CustomerLotPayment)
