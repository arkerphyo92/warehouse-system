# Generated by Django 5.0.6 on 2024-06-28 08:30

import backend.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DataForImageCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=backend.models.get_image_upload_path)),
                ('trip_num', models.CharField(max_length=50)),
                ('container_num', models.CharField(max_length=50)),
                ('invoice_num', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_cases', to='backend.caseimage')),
            ],
        ),
        migrations.CreateModel(
            name='CasesList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_color', models.CharField(max_length=255)),
                ('edge_color', models.CharField(max_length=255)),
                ('case_model', models.CharField(max_length=255)),
                ('case_model_count', models.CharField(max_length=255)),
                ('case_code', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('data_for_imagecase_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cases_list', to='backend.dataforimagecase')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dataforimagecase',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location'),
        ),
        migrations.CreateModel(
            name='StackNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stack_number', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='dataforimagecase',
            name='stack_num',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.stacknumber'),
        ),
        migrations.CreateModel(
            name='WarehouseFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WarehouseData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_color', models.CharField(max_length=255)),
                ('edge_color', models.CharField(max_length=255)),
                ('case_model', models.CharField(max_length=255)),
                ('case_model_count', models.CharField(max_length=255)),
                ('case_code', models.CharField(max_length=255)),
                ('stack_num', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.warehousefile')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excel_file', models.FileField(upload_to=backend.models.get_excel_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('filename', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.warehousefile')),
            ],
        ),
    ]
