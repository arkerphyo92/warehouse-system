import pandas as pd
from backend.models import WarehouseData

def process_inventory_file(excel_file, warehouse_file_instance, user):
    df = pd.read_excel(excel_file)
    warehouse_data_instances = []
    for index, row in df.iterrows():       
        warehouse_data_instances.append(WarehouseData(
            base_color="red",
            edge_color="red",
            case_model=row['case_model'],
            case_model_count=row['case_model_count'],
            case_code=row['case_code'],
            warehouse_file=warehouse_file_instance,
            location=row['location'],
            stack_num=row['stack_num'],
            user=user,
        ))
    WarehouseData.objects.bulk_create(warehouse_data_instances)