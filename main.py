import requests
import json
from collections import namedtuple
import csv
import datetime

from prefect import task, Flow
from prefect.schedules import IntervalSchedule


#Setup
def create_document():
    file = open('complaints.csv','w')
    file.close()
    return (file)


#Extraer
@task(max_retries=10, retry_delay=datetime.timedelta(seconds=30))
def get_complaint_data():
    r = requests.get("https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/", params={'size':10})
    response_json = json.loads(r.text)
    return response_json['hits']['hits']

#Modificar
@task
def parse_complaint_data(raw):
    complaints = []
    Complaint = namedtuple('Complaint', ['data_received', 'state', 'product', 'company', 'complaint_what_happened'])
    for row in raw:
        source = row.get('_source')
        this_complaint = Complaint(
            data_received=source.get('date_recieved'),
            state=source.get('state'),
            product=source.get('product'),
            company=source.get('company'),
            complaint_what_happened=source.get('complaint_what_happened')
        )
        complaints.append(this_complaint)
    return complaints

#Cargar
@task
def store_complaints(modificados):
    file = open('complaints.csv','w')
    csv_writer = csv.writer(file)
    title = ('State, Product, Company',)
    csv_writer.writerow(title)
    for complain in modificados:
        csv_writer.writerow(complain[1:-1])
    file.close()
    return

schedule = IntervalSchedule(interval=datetime.timedelta(minutes=1))

with Flow("etl flow",schedule) as f:
    doc = create_document()
    raw = get_complaint_data()
    modificados = parse_complaint_data(raw)
    populated_table = store_complaints(modificados)
    populated_table.set_upstream(doc)

f.run()

