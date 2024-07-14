from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

def get_image_upload_path(instance, filename):
    today = datetime.today()
    return f'images/{today.year}/{today.month}/{today.day}/{filename}'

def get_excel_upload_path(instance, filename):
    today = datetime.today()
    return f'excel/{today.year}/{today.month}/{today.day}/{filename}'

class Location(models.Model):
    location = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.location}"

class StackNumber(models.Model):
    stack_number = models.CharField(max_length=255, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.stack_number}"

class WarehouseFile(models.Model):
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.filename}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on new objects
            original_filename = self.filename
            counter = 1
            while WarehouseFile.objects.filter(user=self.user, filename=self.filename).exists():
                self.filename = f"{original_filename} - {counter}"
                counter += 1
        super().save(*args, **kwargs)

class InventoryUpload(models.Model):
    filename = models.ForeignKey(WarehouseFile, on_delete=models.CASCADE)
    excel_file = models.FileField(upload_to=get_excel_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Upload: {self.filename.filename} at {self.uploaded_at}"
    
    


class CaseImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"
    

class DataForImageCase(models.Model):
    case_image = models.ForeignKey(CaseImage, on_delete=models.CASCADE, related_name='data_cases')
    image = models.ImageField(upload_to=get_image_upload_path, blank=False, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False)
    stack_num = models.ForeignKey(StackNumber, on_delete=models.CASCADE, blank=False, null=False)  # Assuming stack_num is varchar
    trip_num = models.CharField(max_length=50, blank=False, null=False)
    container_num = models.CharField(max_length=50, blank=False, null=False)
    plate_num = models.CharField(max_length=50, blank=False, null=False)
    invoice_num = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.case_image} - {self.location.location} - Stack {self.stack_num}"

class CasesList(models.Model):
    base_color = models.CharField(max_length=255)
    edge_color = models.CharField(max_length=255)
    case_model = models.CharField(max_length=255, blank=False, null=False)
    case_model_count = models.CharField(max_length=255, blank=False, null=False)
    case_code = models.CharField(max_length=255)
    data_for_imagecase_image = models.ForeignKey(DataForImageCase, on_delete=models.CASCADE, related_name='cases_list')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.case_model}"

class WarehouseData(models.Model):
    base_color = models.CharField(max_length=255)
    edge_color = models.CharField(max_length=255)
    case_model = models.CharField(max_length=255, blank=False, null=False)
    case_model_count = models.CharField(max_length=255, blank=False, null=False)
    case_code = models.CharField(max_length=255)
    warehouse_file = models.ForeignKey(WarehouseFile, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False)
    stack_num = models.CharField(max_length=50, blank=False, null=False)  # Assuming stack_num is varchar
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.case_model} - {self.warehouse_file} - {self.location.location} - {self.stack_num}"
