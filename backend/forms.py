from django import forms
from django.forms import inlineformset_factory
from .models import CaseImage, DataForImageCase, CasesList, WarehouseFile, InventoryUpload, Location, StackNumber

from django import forms
from .models import CaseImage

class CaseImageForm(forms.ModelForm):
    class Meta:
        model = CaseImage
        fields = []
        

class IntroForm(forms.ModelForm):
    location = forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
    stack_num = forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
    trip_num = forms.CharField(required=True),
    container_num = forms.CharField(required=True),
    plate_num = forms.CharField(required=True),
    invoice_num = forms.CharField(required=True),

        
class DataForImageCaseForm(forms.ModelForm):
    class Meta:
        model = DataForImageCase
        fields = ['image']

        # Optionally, you can add widgets to customize the form fields
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'stack_num': forms.Select(attrs={'class': 'form-control'}),
            'trip_num': forms.TextInput(attrs={'class': 'form-control'}),
            'container_num': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_num': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CasesListForm(forms.ModelForm):
    class Meta:
        model = CasesList
        fields = ['base_color', 'edge_color', 'case_model', 'case_model_count', 'case_code']

        # Optionally, you can add widgets to customize the form fields
        widgets = {
            'base_color': forms.TextInput(attrs={'class': 'form-control'}),
            'edge_color': forms.TextInput(attrs={'class': 'form-control'}),
            'case_model': forms.TextInput(attrs={'class': 'form-control'}),
            'case_model_count': forms.TextInput(attrs={'class': 'form-control'}),
            'case_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class WarehouseFileForm(forms.ModelForm):
    class Meta:
        model = WarehouseFile
        fields = ['filename']

        # Optionally, you can add widgets to customize the form fields
        widgets = {
            'filename': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
        }
        
class InventoryUploadForm(forms.ModelForm):
    class Meta:
        model = InventoryUpload
        fields = ['excel_file']
        
        widgets = {
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'name':'imageFile'}),
        }

class ReceivingFilterForm(forms.Form):
    from_date = forms.DateTimeField(
        label='From Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        required=False
    )
    to_date = forms.DateTimeField(
        label='To Date',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    trip_number = forms.CharField(
        label='Trip',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False
        )
    invoice_number = forms.CharField(
        label='Invoice',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100, required=False
        )
    container_number = forms.CharField(
        label='Container',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False
        )
    plate_number = forms.CharField(
        label='License',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50, required=False
        )
    location = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Location.objects.all(), required=False
        )
    stack_number = forms.ModelChoiceField(
        label='Stack',
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=StackNumber.objects.all(), required=False
        )