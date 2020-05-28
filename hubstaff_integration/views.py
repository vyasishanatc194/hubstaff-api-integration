import csv
import datetime
from os import path
from django.views import View
from django.shortcuts import render
from miniproject import config, settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from hubstaff.client_v1 import HubstaffClient

# Render DashBoard Page
class DashBoardView(View):
    def get(self, request):
        return render(request, 'index.html', {})

# Check HubStaff Authentication
def hubStaffAuthentication():
    hubstaff = HubstaffClient(
                    app_token=config.HUBSTAFF_APP_TOKEN,
                    username=config.HUBSTAFF_USERNAME,
                    password=config.HUBSTAFF_PASSWORD
                )
    hubstaff.authenticate()
    return hubstaff

# Convert seconds to Hour, Minute and seconds format.
def convertTime(n): 
    return str(datetime.timedelta(seconds = n))

# Generate CSV
def generate_formatted_data(data):
    columns = []
    rows = []
    response_data = {}
    if data:
        columns = ["project"]
        user_data = data[0]['dates'][0]['users']
        for user in user_data:
            columns.append(user['name'])
            for project in user['projects']:
                record = {}
                record['project_id']  = project['id']
                record['project']  = project['name']
                record[user['name']] = convertTime(project['duration']) if project['duration'] else '00:00:00'
                rows.append(record)
    response_data['columns'] = columns
    response_data['rows'] = rows
    return response_data


# fetch HubStaff Employee Data
class HubStaffUsers(APIView):
    def get(self, request):
        response_data = []
        param = request.query_params.get('date', None)
        date_obj = datetime.datetime.strptime(param, '%Y-%m-%d')
        # hubstaff = hubStaffAuthentication()
        # org_list = hubstaff.get_organizations_list()
        # # Get Only Defined Organization whichis in config.py
        # organization = list(filter(lambda org: org['name'] == config.HUBSTAFF_ORGANIZATION, org_list))
        # if organization:
        #     response_data = hubstaff.get_custom_by_date_team_endpoint(
        #                 date_obj, date_obj,
        #                 [organization[0]['id']]
        #             )
        response_data = [
                    {
                        "id": 262026,
                        "name": "rt-bot-109",
                        "duration": 13868,
                        "dates": [
                            {
                                "date": "2020-05-27",
                                "duration": 13868,
                                "users": [
                                    {
                                        "id": 866822,
                                        "name": "Ishan Vyas",
                                        "duration": 13868,
                                        "projects": [
                                            {
                                                "id": 1043549,
                                                "name": "hubstaff bot109",
                                                "duration": 13868
                                            },
                                            {
                                                "id": 1043550,
                                                "name": "hubstaff bot510",
                                                "duration": 5000
                                            }
                                        ]
                                    },
                                    {
                                        "id": 866823,
                                        "name": "Test Vyas",
                                        "duration": 10868,
                                        "projects": [
                                            {
                                                "id": 1043552,
                                                "name": "TEst530",
                                                "duration": 12000
                                            },
                                            {
                                                "id": 1043549,
                                                "name": "hubstaff bot109",
                                                "duration": 10868
                                            }
                                        ]
                                    },
                                    {
                                        "id": 866824,
                                        "name": "New user",
                                        "duration": 15000,
                                        "projects": [
                                            {
                                                "id": 1043556,
                                                "name": "Hello123",
                                                "duration": 15000
                                            },
                                            {
                                                "id": 1043549,
                                                "name": "hubstaff bot109",
                                                "duration": 12500
                                            },
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
        # Generate response data in matrix form to display in CSV and HTML Table
        if response_data:
            response_data = [generate_formatted_data(response_data)]
            # Generate CSV and response to API
            with open(path.join(settings.BASE_DIR, \
                        'miniproject', 'static', \
                        'csv', 'output.csv'), 'w', newline='') as outcsv:
                cache = {}
                writer = csv.writer(outcsv)
                headers = response_data[0]['columns']
                writer.writerow(headers)
                total_rows = []
                for rIndex, row in enumerate(response_data[0]['rows']):
                    temp_row = []
                    project = row['project']
                    if project not in cache.keys():
                        cache[project] = True
                        temp_row.append(project)
                        total_rows.append(temp_row)
                    index = [total_rows.index(r) for r in total_rows if project in r]
                    for header in range(1, len(headers)):
                        if len(total_rows[index[0]]) < len(headers):
                            total_rows[index[0]].append('00:00:00')
                    if index:
                        for i, h in enumerate(headers):
                            if h in row.keys():
                                total_rows[index[0]][i] = row[h]
                for row in total_rows:
                    writer.writerow(row)
                response_data[0]['columns'] = headers
                response_data[0]['rows'] = total_rows
        return Response(response_data, status=status.HTTP_200_OK)


