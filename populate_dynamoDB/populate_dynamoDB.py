import csv
import boto3

TABLE_NAME = 'AccountTable-DEVELOPMENT-aa276e65-APVM'
EXPORT_FILE = 'dynamodb_export.csv'

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

tabela = dynamodb.Table(TABLE_NAME)

with open(EXPORT_FILE, mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if not row['AccountId'].strip():
            continue
        if not row['Enum'].strip():
            row['Enum'] = "Dummy_value"
        tabela.put_item(Item=row)