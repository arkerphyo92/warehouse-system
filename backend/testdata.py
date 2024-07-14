from django.contrib.auth.models import User

user1 = User.objects.create_user(username='user1', password='password1')
user2 = User.objects.create_user(username='user2', password='password2')

from backend.models import WarehouseFile

# Create warehouse files
warehouse_file1 = WarehouseFile.objects.create(filename='file1.txt', user=user1)
warehouse_file2 = WarehouseFile.objects.create(filename='file2.txt', user=user2)


from backend.models import CaseImage

# Create case images
case_image1 = CaseImage.objects.create(warehouse_file=warehouse_file1, user=user1)
case_image2 = CaseImage.objects.create(warehouse_file=warehouse_file2, user=user2)

from backend.models import Image

# Create images for case_image1
Image.objects.create(case_image=case_image1, image='images/2024/6/20/image1.jpg')
Image.objects.create(case_image=case_image1, image='images/2024/6/20/image2.jpg')

# Create images for case_image2
Image.objects.create(case_image=case_image2, image='images/2024/6/20/image3.jpg')


from backend.models import Location

# Create locations
location1 = Location.objects.create(location='NX', user=user1)
location2 = Location.objects.create(location='ANI', user=user2)
location2 = Location.objects.create(location='WE2', user=user2)
location2 = Location.objects.create(location='PO', user=user1)

from backend.models import WarehouseData

# Create warehouse data entries
WarehouseData.objects.create(base_color='Red', edge_color='Black', case_model='ModelX1', case_model_count='10', case_info='Info about Model X', location=location1, warehouse_file=warehouse_file1, user=user1)
WarehouseData.objects.create(base_color='Blue', edge_color='White', case_model='ModelY1', case_model_count='20', case_info='Info about Model Y', location=location2, warehouse_file=warehouse_file2, user=user2)
WarehouseData.objects.create(base_color='Pink', edge_color='Purple', case_model='R7F2T', case_model_count='30', case_info='Info about R7F2T', location=location2, warehouse_file=warehouse_file2, user=user2)

from backend.models import CasesList

# Create case list entries
CasesList.objects.create(location=location1, base_color='Green', edge_color='Black', case_model='ModelX', case_model_count='10', case_info='Info about Model X', case_image=case_image1, user=user1)
CasesList.objects.create(location=location2, base_color='Blue', edge_color='White', case_model='ModelY', case_model_count='20', case_info='Info about Model Y', case_image=case_image2, user=user2)
CasesList.objects.create(location=location2, base_color='Pink', edge_color='Purple', case_model='R7F2T', case_model_count='33', case_info='Info about Model Y', case_image=case_image2, user=user2)