# views.py
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator

import pandas as pd

from backend.forms import CaseImageForm, DataForImageCaseForm, InventoryUploadForm, WarehouseFileForm, ReceivingFilterForm
from backend.models import CasesList, WarehouseData, DataForImageCase, CaseImage, WarehouseFile, WarehouseData, Location, StackNumber

from django.db import transaction

from django.utils import timezone
from datetime import datetime

def index(request):
    return render(request, 'frontend/index.html')


from django.core.paginator import Paginator

def receiving_search(request):
    form = ReceivingFilterForm(request.GET or None)
    cases = DataForImageCase.objects.all().order_by('-created_at')
    paginator = Paginator(cases, 10)  # Show 10 cases per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count = cases.count()

    if form.is_valid():
        if form.cleaned_data['from_date']:
            cases = cases.filter(created_at__gte=form.cleaned_data['from_date'])
        if form.cleaned_data['to_date']:
            cases = cases.filter(created_at__lte=form.cleaned_data['to_date'])
        if form.cleaned_data['trip_number']:
            cases = cases.filter(trip_num__icontains=form.cleaned_data['trip_number'])
        if form.cleaned_data['invoice_number']:
            cases = cases.filter(invoice_num__icontains=form.cleaned_data['invoice_number'])
        if form.cleaned_data['container_number']:
            cases = cases.filter(container_num__icontains=form.cleaned_data['container_number'])  # Corrected typo
        if form.cleaned_data['plate_number']:
            cases = cases.filter(plate_num__icontains=form.cleaned_data['plate_number'])  # Corrected typo
        if form.cleaned_data['location']:
            cases = cases.filter(location__location__icontains=form.cleaned_data['location'])
        if form.cleaned_data['stack_number']:
            cases = cases.filter(stack_num__stack_number__icontains=form.cleaned_data['stack_number'])  # Corrected typo
        
        paginator = Paginator(cases, 10)
        page_obj = paginator.get_page(page_number)
        count = cases.count()

    context = {
        'form': form,
        'page_obj': page_obj,
        'count': count,
        'columns': request.GET.getlist('columns[]') if request.GET.get('columns[]') else [],  # Adjust as per how you pass column names
    }
    return render(request, 'frontend/receiving_search.html', context)


def receiving(request):
    
    location_lists = Location.objects.values_list('location', flat=True).distinct()
    stack_num_lists = StackNumber.objects.values_list('stack_number', flat=True).distinct()

    if request.method == 'POST':
        selected_location = request.POST.get('location')
        selected_stack_number = request.POST.get('stack_number')
        inputed_trip_number = request.POST.get('trip_number')
        inputed_container_num = request.POST.get('container_num')
        inputed_invoice_num = request.POST.get('invoice_num')
        inputed_plate_number = request.POST.get('plate_num')
        
        # Store data in session
        request.session['selected_location'] = selected_location
        request.session['selected_stack_number'] = selected_stack_number
        request.session['inputed_trip_number'] = inputed_trip_number
        request.session['inputed_container_num'] = inputed_container_num
        request.session['inputed_invoice_num'] = inputed_invoice_num
        request.session['inputed_plate_number'] = inputed_plate_number
        
        messages.success(request, f'Step 1 Data Has Been Set.')
        return redirect('frontend:receiving_image')
    selected_location = request.session.get('selected_location')
    selected_stack_number = request.session.get('selected_stack_number')
    inputed_trip_number = request.session.get('inputed_trip_number')
    inputed_container_num = request.session.get('inputed_container_num')
    inputed_invoice_num = request.session.get('inputed_invoice_num')
    inputed_plate_number = request.session.get('inputed_plate_number')
    context = {
        'selected_location':selected_location,
        'selected_stack_number':selected_stack_number,
        'inputed_trip_number':inputed_trip_number,
        'inputed_container_num':inputed_container_num,
        'inputed_invoice_num':inputed_invoice_num,
        'inputed_plate_number':inputed_plate_number,
        'location_lists': location_lists,
        'stack_num_lists': stack_num_lists,
    }
    return render(request, 'frontend/receiving_intro.html', context)


def process_image_with_ai(image_path):

    print(image_path)

    ai_results = [
        {
        'base_color': 'Red',
        'edge_color': 'Black',
        'case_model': 'R7F3T',
        'case_model_count': '5',
        'case_code': 'CODE1231',
        },
        {
        'base_color': 'Green',
        'edge_color': 'Gray',
        'case_model': 'R8F4T',
        'case_model_count': '4',
        'case_code': 'CODE123',
        },
        {
        'base_color': 'Green',
        'edge_color': 'Gray',
        'case_model': 'R9F5T',
        'case_model_count': '8',
        'case_code': 'CODE12',
        },
        {
        'base_color': 'Green',
        'edge_color': 'Gray',
        'case_model': 'R0F6T',
        'case_model_count': '9',
        'case_code': 'CODE1',
        },               
                  ]

    return ai_results


import base64
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

def receiving_image(request):
    # Retrieve data from session
    selected_location = request.session.get('selected_location')
    selected_stack_number = request.session.get('selected_stack_number')
    inputed_trip_number = request.session.get('inputed_trip_number')
    inputed_container_num = request.session.get('inputed_container_num')
    inputed_invoice_num = request.session.get('inputed_invoice_num')
    inputed_plate_number = request.session.get('inputed_plate_number')
    
    selected_image_data = request.session.get('selected_image_data', '')
    selected_image_filename = request.session.get('selected_image_filename', '')
    today = timezone.now().date()
    time = datetime.now()

    now = time.strftime("%I:%M %p")
    if request.method == 'POST':
        if 'save_data' in request.POST and selected_image_data:
            case_image = CaseImage.objects.create(
                user=request.user  # Assuming user is authenticated
            )
            locations_Location = Location.objects.values_list('location', 'id')
                    #Preparing for remapping (To change from location to id)
            location_mapping = {location: id for location, id in locations_Location}
            location_name = selected_location  # Get location name from Excel Row 24 from eachcolumn
            location_id = location_mapping.get(location_name, None) #Getting Location name and compare with mapping
            
            
            stacknumber_StackNumber = StackNumber.objects.values_list('stack_number', 'id')
                    #Preparing for remapping (To change from location to id)
            stacknumber_mapping = {stack: id for stack, id in stacknumber_StackNumber}
            stacknumber_name = selected_stack_number  # Get location name from Excel Row 24 from eachcolumn
            stacknumber_id = stacknumber_mapping.get(stacknumber_name, None) #Getting Location name and compare with mapping
            
            
            if location_id and stacknumber_id is not None:
                image_data = base64.b64decode(selected_image_data)
                image_file = InMemoryUploadedFile(
                    BytesIO(image_data), 
                    None, 
                    selected_image_filename, 
                    'image/jpeg',  # Adjust MIME type as needed
                    len(image_data), 
                    None
                )
                data_case = DataForImageCase.objects.create(
                    case_image=case_image,
                    image=image_file,
                    location_id=location_id,
                    stack_num_id=stacknumber_id,
                    trip_num=inputed_trip_number,
                    container_num=inputed_container_num,
                    plate_num=inputed_plate_number,
                    invoice_num=inputed_invoice_num,
                )
                ai_results = process_image_with_ai(data_case.image)
                for result in ai_results:
                    CasesList.objects.create(
                        base_color=result['base_color'],
                        edge_color=result['edge_color'],
                        case_model=result['case_model'],
                        case_model_count=result['case_model_count'],
                        case_code=result['case_code'],
                        data_for_imagecase_image=data_case,
                        user=request.user,
                    )
                request.session.pop('selected_image_data', None)  
                request.session.pop('selected_stack_number', None)
                
                messages.success(request, f'Successfully save the AI Data ID - {data_case.id} @ { today } { now }')  
                return redirect('frontend:receiving_search')
                # print(ai_results, selected_image_data, selected_image_filename, selected_location, selected_stack_number,
                #     inputed_trip_number,inputed_container_num,inputed_invoice_num,inputed_plate_number)
        
        elif 'imageFile' in request.FILES:
            selected_image = request.FILES['imageFile']
            image_data = selected_image.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')
            image_filename = selected_image.name
            
            image_file = InMemoryUploadedFile(
                BytesIO(image_data),
                None,
                image_filename,
                'image/jpeg',  # Adjust MIME type as needed
                len(image_data),
                None
            )
            
            ai_results = process_image_with_ai(image_file)  # Use image_file here
            # Store image data and filename in session for later use
            request.session['selected_image_data'] = encoded_image_data
            request.session['selected_image_filename'] = image_filename
            request.session['selected_ai_result'] = ai_results
            
            context = {
                'today': today,
                'now': now,
                'selected_location': selected_location,
                'selected_stack_number': selected_stack_number,
                'inputed_trip_number': inputed_trip_number,
                'inputed_container_num': inputed_container_num,
                'inputed_invoice_num': inputed_invoice_num,
                'inputed_plate_number': inputed_plate_number,
                'ai_results': ai_results,
                'selected_image_filename': image_filename,  # Update context with the new image filename
            }
            messages.success(request, f'Step 2 "{image_filename}" has been Set.')
            # Handle saving data here
            return render(request, 'frontend/receiving_image.html', context)
    context = {
        'today':today,
        'now':now,
        'selected_location': selected_location,
        'selected_stack_number': selected_stack_number,
        'inputed_trip_number': inputed_trip_number,
        'inputed_container_num': inputed_container_num,
        'inputed_invoice_num': inputed_invoice_num,
        'inputed_plate_number': inputed_plate_number,        
        'selected_image_filename': selected_image_filename,
        'selected_image_data':selected_image_data,
        
    }
    
    return render(request, 'frontend/receiving_image.html', context)


def compare_cases_and_warehouse_view(request):
    # Fetch distinct case_image_ids from CaseImage
    case_image_file_ides = DataForImageCase.objects.values_list('id', flat=True).distinct().order_by('-created_at')

    # Fetch distinct warehouse_file_names from WarehouseFile
    warehouse_file_names = WarehouseFile.objects.values_list('filename', flat=True).distinct().order_by('-created_at')

    # Get selected case_image_ids and warehouse_file_name from request GET parameters
    case_image_file_ids = request.GET.getlist('case_image_file_ids')
    warehouse_file_name = request.GET.get('warehouse_file_name')

    # Initialize querysets
    cases_list = CasesList.objects.all()
    warehouse_data = WarehouseData.objects.all()
    images_list = DataForImageCase.objects.all()
    
    # Filter CasesList based on selected case_image_ids
    if case_image_file_ids:
        cases_list = cases_list.filter(data_for_imagecase_image__id__in=case_image_file_ids)
        images_list = images_list.filter(case_image__id__in=case_image_file_ids)
    
    # Filter WarehouseData based on selected warehouse_file_name
    if warehouse_file_name:
        warehouse_data = warehouse_data.filter(warehouse_file__filename=warehouse_file_name)

    # Initialize the dictionaries to hold the comparison data
    cases_list_data = {}
    for case in cases_list:
        key = (case.case_model, case.data_for_imagecase_image.location.location, case.data_for_imagecase_image.stack_num.stack_number)
        cases_list_data[key] = case

    warehouse_data_set = {}
    for data in warehouse_data:
        key = (data.case_model, data.location.location, data.stack_num)
        warehouse_data_set[key] = data 

    # Perform set operations to find differences
    only_in_cases_list_keys = cases_list_data.keys() - warehouse_data_set.keys()
    only_in_warehouse_data_keys = warehouse_data_set.keys() - cases_list_data.keys()
    in_both_keys = cases_list_data.keys() & warehouse_data_set.keys()

    # Retrieve original dictionaries based on the keys
    only_in_cases_list = [cases_list_data[key] for key in only_in_cases_list_keys]
    only_in_warehouse_data = [warehouse_data_set[key] for key in only_in_warehouse_data_keys]
    in_both = [(cases_list_data[key], warehouse_data_set[key]) for key in in_both_keys]

    images_with_names = [{'image': image, 'name': image.image.name.split('/')[-1]} for image in images_list]
    total_discrepancies = len(only_in_cases_list) + len(only_in_warehouse_data)
    
    cases_list_data_count = len(cases_list_data)
    warehouse_data_set_count = len(warehouse_data_set)
    context = {
        'case_image_file_ides': case_image_file_ides,
        'warehouse_file_names': warehouse_file_names,
        'only_in_cases_list': only_in_cases_list,
        'only_in_warehouse_data': only_in_warehouse_data,
        'in_both': in_both,
        'cases_list_data_count':cases_list_data_count,
        'warehouse_data_set_count':warehouse_data_set_count,
        'total_discrepancies': total_discrepancies,
        'selected_images_list': images_with_names,
        'selected_case_image_file_ids': case_image_file_ids,
        'selected_warehouse_file_name': warehouse_file_name,
    }

    return render(request, 'frontend/compare_results.html', context)


def add_new(request):
    # Create formsets to handle multiple instances of DataForImageCase with 5 extra blank forms
    DataForImageCaseFormSet = modelformset_factory(DataForImageCase, form=DataForImageCaseForm, min_num=1, extra=5)
    if request.method == 'POST':
        # Initialize the CaseImageForm and DataForImageCaseFormSet with POST data
        DataForImageCaseFormSet2 = DataForImageCaseFormSet(request.POST, request.FILES, prefix='form2')
        try:
            with transaction.atomic(): #**** Atomic Transaction Don't Allow Any Errors
                if DataForImageCaseFormSet2.is_valid():

                    # Create instances for DataForImageCase without saving them yet
                    data_for_image_instances = DataForImageCaseFormSet2.save(commit=False)
                    for data_for_image_instance in data_for_image_instances:
                        # Set user and link to the CaseImage instance
                        data_for_image_instance.user = request.user

                    # Save the CaseImage instance

                    # Save each DataForImageCase instance
                    for data_for_image_instance in data_for_image_instances:
                        data_for_image_instance.save()
                    # Dummy AI function returned data
                        ai_returned_data = [                       
                            {
                                'base_color': 'red',
                                'edge_color': 'green',
                                'case_model': 'R73T',
                                'case_model_count': '12',
                                'case_code': 'EFGH5678',
                                'data_for_imagecase_image_id': data_for_image_instance.id,  # ID of the related DataForImageCase instance
                                'user_id': request.user.id  # ID of the user who is associated with this case list
                            },
                            {
                                'base_color': 'pink',
                                'edge_color': 'purple',
                                'case_model': 'R7F3T',
                                'case_model_count': '15',
                                'case_code': 'EFGH5678',
                                'data_for_imagecase_image_id': data_for_image_instance.id,  # ID of the related DataForImageCase instance
                                'user_id': request.user.id  # ID of the user who is associated with this case list
                            },
                            {
                                'base_color': 'pink',
                                'edge_color': 'purple',
                                'case_model': 'R8F4T',
                                'case_model_count': '12',
                                'case_code': 'EFGH5678',
                                'data_for_imagecase_image_id': data_for_image_instance.id,  # ID of the related DataForImageCase instance
                                'user_id': request.user.id  # ID of the user who is associated with this case list
                            }
                        ]
                        # Process and save CasesList instances based on the AI data
                        for case_list_data in ai_returned_data:
                            CasesList.objects.create(
                                base_color=case_list_data['base_color'],
                                edge_color=case_list_data['edge_color'],
                                case_model=case_list_data['case_model'],
                                case_model_count=case_list_data['case_model_count'],
                                case_code=case_list_data['case_code'],
                                data_for_imagecase_image_id=case_list_data['data_for_imagecase_image_id'],
                                user_id=case_list_data['user_id']
                            )
                    messages.success(request, f'Record added successfully!')
                    compare_view_url = reverse('frontend:compare_view')
                    return redirect(compare_view_url)
        except Exception as e:
            # Rollback transaction on error
            # transaction.rollback()
            print(f"Error occurred: {e}")
            messages.error(request, 'Error occurred while saving Images and AI data.')    
    else:
        # If the request is GET, instantiate empty forms with the specified prefixes
        case_image_form1 = CaseImageForm(prefix='form1')
        DataForImageCaseFormSet2 = DataForImageCaseFormSet(queryset=DataForImageCase.objects.none(), prefix='form2')
        


    # Get today's date
    today = timezone.now().date()
    
    total_image_list = CaseImage.objects.filter(created_at__date=today).count()
    total_cases_list = CasesList.objects.filter(created_at__date=today).count()
    
    total_warehousefile_list = WarehouseFile.objects.filter(created_at__date=today).count()
    total_warehousedata_list = WarehouseData.objects.filter(created_at__date=today).count()
    
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (today.replace(month=today.month % 12 + 1, day=1) - timezone.timedelta(days=1))

    # Filter CaseImageForm objects by the current month
    image_month_count = CasesList.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lte=last_day_of_month
    ).count()
    
    inventory_month_count = WarehouseData.objects.filter(
        created_at__date__gte=first_day_of_month,
        created_at__date__lte=last_day_of_month
    ).count()
    
    # Context to be passed to the template
    context = {
        'today' : today,
        'total_image_list' : total_image_list,
        'total_cases_list': total_cases_list,
        'total_warehousefile_list' : total_warehousefile_list,
        'total_warehousedata_list': total_warehousedata_list,
        'image_month_count' : image_month_count,
        'inventory_month_count':inventory_month_count,
        'first_day_of_month':first_day_of_month,
        'last_day_of_month' : last_day_of_month,
        'case_image_form1': case_image_form1,
        'DataForImageCaseFormSet2': DataForImageCaseFormSet2
    }
    # Render the 'add_new' template with the context
    return render(request, 'frontend/add.html', context)


        # for i, row in df.iterrows():
        #     if pd.notna(row["sn1"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn1"]}')
        #         print(f'location is {df.loc[24,"sn1"]}')
        #         print('stack num is 1')
        #         print("---------------")
        #     if pd.notna(row["sn2"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn2"]}')
        #         print(f'location is {df.loc[24,"sn2"]}')
        #         print(f'stack num is 2')
        #         print("---------------")
        #     if pd.notna(row["sn3"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn3"]}')
        #         print(f'location is {df.loc[24,"sn3"]}')
        #         print(f'stack num is 3')
        #         print("---------------")
        #     if pd.notna(row["sn4"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn4"]}')
        #         print(f'location is {df.loc[24,"sn4"]}')
        #         print(f'stack num is 4')
        #         print("---------------")
        #     if pd.notna(row["sn5"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn5"]}')
        #         print(f'location is {df.loc[24,"sn5"]}')
        #         print(f'stack num is 5')
        #         print("---------------")
        #     if pd.notna(row["sn6"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn6"]}')
        #         print(f'location is {df.loc[24,"sn6"]}')
        #         print(f'stack num is 6')
        #         print("---------------")
        #     if pd.notna(row["sn7"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn7"]}')
        #         print(f'location is {df.loc[24,"sn7"]}')
        #         print(f'stack num is 7')
        #         print("---------------")
        #     if pd.notna(row["sn8"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
        #         print(f'case_model is {row["case_model"]}')
        #         print(f'case_model_count is {row["sn8"]}')
        #         print(f'location is {df.loc[24,"sn8"]}')
        #         print(f'stack num is 8')
        #         print("---------------")

def delivery_add_data(request):
    #Initiaate for Plane Form
    WarehouseFileFormSet = modelformset_factory(WarehouseFile, form=WarehouseFileForm)
    inventory_upload_form = InventoryUploadForm(prefix='form1')
    
    #Start This Process after click on submit
    if request.method == 'POST' and request.FILES.get('form1-excel_file'):
        #Receive Submit Data 
        WarehouseFileFormSet2 = WarehouseFileFormSet(request.POST, prefix='form2')
        inventory_upload_form = InventoryUploadForm(request.POST, request.FILES, prefix='form1')        
        excel_file = request.FILES['form1-excel_file'] #Excel Input Name
        sheet_name = "Sheet1" #May be Customer Need Sheet2
        
        try:
            with transaction.atomic(): #**** Atomic Transaction Don't Allow Any Errors
            # Get row and column definitions (replace with your chosen method)
                df = pd.read_excel(excel_file, skiprows=4, nrows=27, usecols=range(9), header=None, sheet_name=sheet_name)
                set_column_names = ["case_model", "sn1", "sn2", "sn3", "sn4", "sn5", "sn6", "sn7", "sn8"]
                df.columns = set_column_names # Define Column Name Manually
                df = df.dropna(subset=['case_model']) #Base only on CaseModel
                
                #Validate both Fomr
                if WarehouseFileFormSet2.is_valid() and inventory_upload_form.is_valid():
                    #Getting Instance First
                    warehouse_file_form_instances = WarehouseFileFormSet2.save(commit=False)
                    inventory_upload_instance = inventory_upload_form.save(commit=False)

                    #Mandatory for creating loops because of formset
                    #Warehouse File Save
                    for warehouse_file_form_instance_item in warehouse_file_form_instances:
                        warehouse_file_form_instance_item.user = request.user
                        warehouse_file_form_instance_item.save()
                        
                    #Inventory File Save
                    if warehouse_file_form_instances:
                        inventory_upload_instance.filename_id = warehouse_file_form_instances[0].id
                        inventory_upload_instance.save()
                    #Start Warehouse Data for Relevant Warehouse File
                    
                    warehouse_data_instances = []
                    
                    #Location can't assigne Directly
                    #So Get the location from DB (Need to assign First)
                    locations_Location = Location.objects.values_list('location', 'id')
                    #Preparing for remapping (To change from location to id)
                    location_mapping = {location: id for location, id in locations_Location}
                    
                    for i, row in df.iterrows():
                        #Data Base on Case Model and Neglect Total and Location in this column
                        if row["case_model"] != "Total" and row["case_model"] != "Location":
                                #     if pd.notna(row["sn1"]) and row["case_model"] != "Total" and row["case_model"] != "Location":
                                #         print(f'case_model is {row["case_model"]}')
                                #         print(f'case_model_count is {row["sn1"]}')
                                #         print(f'location is {df.loc[24,"sn1"]}')
                                #         print(f'stack num is 8')
                                #         print("---------------")
                            for idx, col in enumerate(set_column_names[1:], start=1):  # Iterate through 'sn1' to 'sn8'
                                if pd.notna(row[col]):
                                    location_name = df.loc[24, col]  # Get location name from Excel Row 24 from eachcolumn
                                    location_id = location_mapping.get(location_name, None) #Getting Location name and compare with mapping
                                    if location_id is not None: #If location is inside the mapping
                                        # Create WarehouseData instance with location as Location object
                                        warehouse_data_instance = WarehouseData(
                                            base_color="red",
                                            edge_color="red",
                                            case_model=row["case_model"],
                                            case_model_count=row[col],
                                            case_code="casecode",
                                            warehouse_file=warehouse_file_form_instances[0],  # Replace with actual value
                                            location_id=location_id,  # Assign location_id directly
                                            stack_num=idx,
                                            user=request.user  # Replace with actual value
                                        )
                                        warehouse_data_instances.append(warehouse_data_instance)
                    filename_instance = warehouse_data_instances[0].warehouse_file
                    # Bulk create WarehouseData instances
                    WarehouseData.objects.bulk_create(warehouse_data_instances)
                    messages.success(request, f"Delivery Plan '{filename_instance}' data saved successfully.")
                    context = {
                        'inventory_upload_form': inventory_upload_form,
                        'WarehouseFileFormSet2': WarehouseFileFormSet2,                        
                    }
                    return redirect('frontend:compare_view')
        except Exception as e:
            # Rollback transaction on error
            transaction.rollback()
            print(f"Error occurred: {e}")
            messages.error(request, 'Excel is not correctly formatted.')
       
    WarehouseFileFormSet2 = WarehouseFileFormSet(queryset=WarehouseFile.objects.none(), prefix='form2')
    context = {
        'inventory_upload_form': inventory_upload_form,
        'WarehouseFileFormSet2': WarehouseFileFormSet2
    }
    
    return render(request, 'frontend/delivery_add_data.html', context)


def delivering(request):
    location_lists = Location.objects.values_list('location', flat=True).distinct()
    stack_num_lists = StackNumber.objects.values_list('stack_number', flat=True).distinct()

    if request.method == 'POST':
        selected_location = request.POST.get('location')
        selected_stack_number = request.POST.get('stack_number')
        inputed_trip_number = request.POST.get('trip_number')
        inputed_container_num = request.POST.get('container_num')
        inputed_invoice_num = request.POST.get('invoice_num')
        inputed_plate_number = request.POST.get('plate_num')
        
        # Store data in session with "delivery_" prefix
        request.session['delivery_selected_location'] = selected_location
        request.session['delivery_selected_stack_number'] = selected_stack_number
        request.session['delivery_inputed_trip_number'] = inputed_trip_number
        request.session['delivery_inputed_container_num'] = inputed_container_num
        request.session['delivery_inputed_invoice_num'] = inputed_invoice_num
        request.session['delivery_inputed_plate_number'] = inputed_plate_number
        
        messages.success(request, 'All Data Has Been Set.')
        messages.warning(request, "Don't Forget to Upload Image!")
        return redirect('frontend:delivering_image')
    
    selected_location = request.session.get('delivery_selected_location')
    selected_stack_number = request.session.get('delivery_selected_stack_number')
    inputed_trip_number = request.session.get('delivery_inputed_trip_number')
    inputed_container_num = request.session.get('delivery_inputed_container_num')
    inputed_invoice_num = request.session.get('delivery_inputed_invoice_num')
    inputed_plate_number = request.session.get('delivery_inputed_plate_number')
    
    context = {
        'selected_location': selected_location,
        'selected_stack_number': selected_stack_number,
        'inputed_trip_number': inputed_trip_number,
        'inputed_container_num': inputed_container_num,
        'inputed_invoice_num': inputed_invoice_num,
        'inputed_plate_number': inputed_plate_number,
        'location_lists': location_lists,
        'stack_num_lists': stack_num_lists,
    }
    return render(request, 'frontend/delivering_intro.html', context)

def delivering_image(request):
    # Retrieve data from session with "delivery_" prefix
    selected_location = request.session.get('delivery_selected_location')
    selected_stack_number = request.session.get('delivery_selected_stack_number')
    inputed_trip_number = request.session.get('delivery_inputed_trip_number')
    inputed_container_num = request.session.get('delivery_inputed_container_num')
    inputed_invoice_num = request.session.get('delivery_inputed_invoice_num')
    inputed_plate_number = request.session.get('delivery_inputed_plate_number')
    
    selected_image_data = request.session.get('delivery_selected_image_data', '')
    selected_image_filename = request.session.get('delivery_selected_image_filename', '')
    
    if request.method == 'POST':
        if 'save_data' in request.POST and selected_image_data:
            case_image = CaseImage.objects.create(user=request.user)
            
            locations_Location = Location.objects.values_list('location', 'id')
            location_mapping = {location: id for location, id in locations_Location}
            location_name = selected_location
            location_id = location_mapping.get(location_name, None)
            
            stacknumber_StackNumber = StackNumber.objects.values_list('stack_number', 'id')
            stacknumber_mapping = {stack: id for stack, id in stacknumber_StackNumber}
            stacknumber_name = selected_stack_number
            stacknumber_id = stacknumber_mapping.get(stacknumber_name, None)
            
            if location_id and stacknumber_id is not None:
                image_data = base64.b64decode(selected_image_data)
                image_file = InMemoryUploadedFile(
                    BytesIO(image_data), 
                    None, 
                    selected_image_filename, 
                    'image/jpeg', 
                    len(image_data), 
                    None
                )
                data_case = DataForImageCase.objects.create(
                    case_image=case_image,
                    image=image_file,
                    location_id=location_id,
                    stack_num_id=stacknumber_id,
                    trip_num=inputed_trip_number,
                    container_num=inputed_container_num,
                    plate_num=inputed_plate_number,
                    invoice_num=inputed_invoice_num,
                )
                ai_results = process_image_with_ai(selected_image_data)
                for result in ai_results:
                    finaldata = CasesList.objects.create(
                        base_color=result['base_color'],
                        edge_color=result['edge_color'],
                        case_model=result['case_model'],
                        case_model_count=result['case_model_count'],
                        case_code=result['case_code'],
                        data_for_imagecase_image=data_case,
                        user=request.user,
                    )
            request.session.pop('delivery_selected_image_data', None)
            request.session.pop('delivery_selected_stack_number', None)
            created_time = finaldata.created_at
            formatted_time = created_time.strftime('%Y-%m-%d %H:%M:%S')
            messages.success(request, f'Successfully save the AI Data ID - {case_image.id} @ {formatted_time}')
            messages.error(request, "Update Time!")    
            return redirect('frontend:delivering')
        
        elif 'imageFile' in request.FILES:
            selected_image = request.FILES['imageFile']
            image_data = selected_image.read()
            encoded_image_data = base64.b64encode(image_data).decode('utf-8')
            image_filename = selected_image.name
            ai_results = process_image_with_ai(selected_image)
            
            # Store image data and filename in session with "delivery_" prefix
            request.session['delivery_selected_image_data'] = encoded_image_data
            request.session['delivery_selected_image_filename'] = image_filename
            request.session['delivery_selected_ai_result'] = ai_results
            
            context = {
                'selected_location': selected_location,
                'selected_stack_number': selected_stack_number,
                'inputed_trip_number': inputed_trip_number,
                'inputed_container_num': inputed_container_num,
                'inputed_invoice_num': inputed_invoice_num,
                'inputed_plate_number': inputed_plate_number,
                'ai_results': ai_results,
                'selected_image_filename': image_filename,
            }
            messages.success(request, f'Successfully uploaded the image - {image_filename}')
            return render(request, 'frontend/delivering_image.html', context)

    context = {
        'selected_location': selected_location,
        'selected_stack_number': selected_stack_number,
        'inputed_trip_number': inputed_trip_number,
        'inputed_container_num': inputed_container_num,
        'inputed_invoice_num': inputed_invoice_num,
        'inputed_plate_number': inputed_plate_number,        
        'selected_image_filename': selected_image_filename,
        'selected_image_data': selected_image_data,
    }
    
    return render(request, 'frontend/delivering_image.html', context)


