from django.contrib import admin
from .models import CaseImage, DataForImageCase, CasesList, WarehouseFile, WarehouseData, Location, InventoryUpload, StackNumber

# Register your models here.

admin.site.register(CaseImage)
admin.site.register(DataForImageCase)
admin.site.register(CasesList)
admin.site.register(WarehouseFile)
admin.site.register(WarehouseData)
admin.site.register(Location)
admin.site.register(InventoryUpload)
admin.site.register(StackNumber)