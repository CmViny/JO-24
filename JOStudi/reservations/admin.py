from django.contrib import admin
from .models import Reservation, QRCode, Transaction

admin.site.register(Reservation)
admin.site.register(QRCode)
admin.site.register(Transaction)