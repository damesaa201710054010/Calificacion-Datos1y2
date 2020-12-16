#!/usr/bin/env python3

""" 
Python module that reads a csv file containing the grades of students.
It then connects to a google drive spreadsheet and updates the grades of every student on the csv file.

It uses the SPREADSHEET API V4 provided by google.

Make sure you enable the api and have the credentials.json file in your working directory.
#TODO: I STILL DON'T KNOW HOW YOU CAN ENABLE THE API, I JUST USE THE QUICKSTART TUTORIAL TO DO IT. FIND HOW TO DO IT.

Usage: python3 update_grades.py {ed1|ed2} {01|02|03} {1|2|..|12}.

Author: Rafael Villegas.
"""

import sys
import csv
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle first.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# If you need to add more sheets or change the current ones, do it here.
SPREADSHEETS_ID_LIST = {
    "ED1": {
        "33": "1IysGtSTbxJQtDelem-NCo1zDBSAQvl83OVgHr9dJtP0",  # Cambiar
        "32": "",
        "01": "",
        "02": "1GEv_Ke5DpgN_GAIV8VFkX73NyCuvjxaqLQUpwkL0-Cw",   # Cambiar
        "03": "1dgEK5Of6D_tQgzQ8h3Ygjvq3zRB173VZMeDVSoNN0RA"   # Cambiar
    },
    "ED2": {
        "33": "",
        "32": "",
        "01": "",
        "02": "",
        "03": ""
    }  
}

# Each array position represents the columnn range corresponding to each activity number
# e.g. activity 1 corresponds to column C of the sheet
SPREADSHEET_RANGES = [None, "C4:C", "D4:D", "E4:E", "F4:F",
                      "G4:G", "H4:H", "I4:I", "J4:J", "K4:K", "L4:L", "M4:M", "N4:N"]
SPREADSHEET_RANGES_Project = [None, "E4:E", "F4:F"]
SPREADSHEET_RANGES_Labs = [None, "C4:C", "D4:D",
                           "F4:F", "G4:G", "H4:H"]


def main(argv):

    if len(argv) < 4:
        bad_usage()
    p = False
    course = argv[1].upper()
    group = argv[2]
    activity_number = argv[3]
    if (activity_number == "p01" or activity_number == "p02" or
    activity_number == "l1" or activity_number == "l2" or activity_number == "l3" or activity_number == "l4" or 
    activity_number == "l5"):
        activity_number = argv[3]
        #print("I'm here")
        p = True
    else:
        activity_number = int(argv[3])
        p=False

    if course != "ED1" and course != "ED2":
        bad_usage()
    elif p==False:
        if activity_number < 1 or activity_number > 13:
            bad_usage()

    creds = None
    creds = verify_credentials(creds)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API and choose the correct sheet
    sheet = service.spreadsheets()
    sheet_id = choose_sheet(course, group)

    # Get the grades and pre-process it 
    if activity_number == "p01":   #es proyecto?
        students = get_students_from_csv(
            course, group, "Proyecto/proyecto-1.csv")
    elif activity_number == "p02":
        students = get_students_from_csv(
            course, group, "Proyecto/proyecto-2.csv")
    elif activity_number == 'l1':
        students = get_students_from_csv(course, group, "Labs/lab1.csv")  #lab1?
    elif activity_number == 'l2':
        students = get_students_from_csv(course, group, "Labs/lab2.csv") #lab2?
    elif activity_number == 'l3':
        students = get_students_from_csv(course, group, "Labs/lab3.csv")   #lab3?
    elif activity_number == 'l4':
        students = get_students_from_csv(course, group, "Labs/lab4.csv")   #lab5?
    elif activity_number == 'l5':
        students = get_students_from_csv(course, group, "Labs/lab5.csv")   #lab6?
    else:
        students = get_students_from_csv(course, group, "talleres.csv")   #talleres?

    if activity_number == 'l1' or activity_number ==  'l2' or activity_number ==  'l3' or activity_number ==  'l4' or activity_number ==  'l5':
        labsupdate(students, sheet_id, activity_number, sheet) #actualiza las notas del lab en la hoja de calculo
    else:
        #actualiza para el proyecto o para los talleres
        grades = get_grades(students, activity_number)
        ids = get_ids_from_sheet(sheet, sheet_id, p, False, False, False, False, False, activity_number)
        sorted_grades = sort_grades(grades, ids)
        sheet_range = choose_range(activity_number)
        # Values to be added to the google sheet
        values = [
            sorted_grades
        ]
        # Body of the request, according to the sheets v4 api
        body = {
            "majorDimension": "COLUMNS",
            "values": values
        }
        # Update the values on the sheet
        result = sheet.values().update(spreadsheetId=sheet_id, range=sheet_range,
                                       valueInputOption="RAW", body=body).execute()
        print(f"{result.get('updatedCells')} cells updated")

#los laboratorios actualizan mas de una celda, este metodo puede ser mas optimizado (lo hice rapido por la presion (; ))
def labsupdate(students, sheet_id, activity_number, sheet): 
    """
    Gets each student's grade for the activity that you are evaluating.
    """
    if activity_number == 'l1':
        activity_number = 1
    elif activity_number == 'l2':
        activity_number = 2
    elif activity_number == 'l3':
        activity_number = 3
    elif activity_number == 'l4':
        activity_number = 4
    elif activity_number == 'l5':
        activity_number = 5
    j = 2
    
    for i in [1,2,3,4,5]:
        grades = []
        for student in students:
            # Tuple of student ID and grade
            entry = (student[j], float(student[activity_number+4]))
            grades.append(entry)
        if  i== 1:
            ids = get_ids_from_sheet(sheet, sheet_id, False, True, False, False, False, False, activity_number)
        elif i == 2:
            ids = get_ids_from_sheet(sheet, sheet_id, False, False, True, False, False, False, activity_number)
        elif i == 3:
            ids = get_ids_from_sheet(sheet, sheet_id, False, False, False, True, False, False, activity_number)
        elif i == 4:
            ids = get_ids_from_sheet(sheet, sheet_id, False, False, False, False, True, False, activity_number)
        elif i == 5:
            ids = get_ids_from_sheet(sheet, sheet_id, False, False, False, False, False, True, activity_number)
        sorted_grades = sort_grades(grades, ids)
        sheet_range = getlabs(i, activity_number)

        # Values to be added to the google sheet
        values = [
            sorted_grades
        ]
        # Body of the request, according to the sheets v4 api
        body = {
            "majorDimension": "COLUMNS",
            "values": values
        }

        # Update the values on the sheet
        result = sheet.values().update(spreadsheetId=sheet_id, range=sheet_range,
                                        valueInputOption="RAW", body=body).execute()
        print(f"{result.get('updatedCells')} cells updated")


#este metodo tambien puede ser mejorado, escoge cual es el rango de cada uno de los punto de cada lab
def getlabs(i, activity_number):
    if i == 1 and activity_number == 1:
        return f"Laboratorio 1!{SPREADSHEET_RANGES_Labs[2]}"
    elif i == 2 and activity_number ==1:
        return f"Laboratorio 1!{SPREADSHEET_RANGES_Labs[1]}"
    elif i == 3 and activity_number == 1:
        return  f"Laboratorio 1!{SPREADSHEET_RANGES_Labs[3]}"
    elif i == 4 and activity_number == 1:
        return f"Laboratorio 1!{SPREADSHEET_RANGES_Labs[4]}"
    elif i== 5 and activity_number == 1:
        return f"Laboratorio 1!{SPREADSHEET_RANGES_Labs[5]}"
    elif i == 1 and activity_number == 2:
        return f"Laboratorio 2!{SPREADSHEET_RANGES_Labs[2]}"
    elif i == 2 and activity_number == 2:
        return f"Laboratorio 2!{SPREADSHEET_RANGES_Labs[1]}"
    elif i == 3 and activity_number == 2:
        return  f"Laboratorio 2!{SPREADSHEET_RANGES_Labs[3]}"
    elif i == 4 and activity_number == 2:
        return f"Laboratorio 2!{SPREADSHEET_RANGES_Labs[4]}"
    elif i== 5 and activity_number == 2:
        return f"Laboratorio 2!{SPREADSHEET_RANGES_Labs[5]}"
    elif i == 1 and activity_number == 3:
        return f"Laboratorio 3!{SPREADSHEET_RANGES_Labs[2]}"
    elif i == 2 and activity_number == 3:
        return f"Laboratorio 3!{SPREADSHEET_RANGES_Labs[1]}"
    elif i == 3 and activity_number == 3:
        return  f"Laboratorio 3!{SPREADSHEET_RANGES_Labs[3]}"
    elif i == 4 and activity_number == 3:
        return f"Laboratorio 3!{SPREADSHEET_RANGES_Labs[4]}"
    elif i== 5 and activity_number == 3:
        return f"Laboratorio 3!{SPREADSHEET_RANGES_Labs[5]}"
    elif i == 1 and activity_number==4:
        return f"Laboratorio 4!{SPREADSHEET_RANGES_Labs[2]}"
    elif i == 2 and activity_number == 4:
        return f"Laboratorio 4!{SPREADSHEET_RANGES_Labs[1]}"
    elif i == 3 and activity_number == 4:
        return  f"Laboratorio 4!{SPREADSHEET_RANGES_Labs[3]}"
    elif i == 4 and activity_number == 4:
        return f"Laboratorio 4!{SPREADSHEET_RANGES_Labs[4]}"
    elif i== 5 and activity_number == 4:
        return f"Laboratorio 4!{SPREADSHEET_RANGES_Labs[5]}"
    elif i == 1 and activity_number == 5:
        return f"Laboratorio 5!{SPREADSHEET_RANGES_Labs[2]}"
    elif i == 2 and activity_number == 5:
        return f"Laboratorio 5!{SPREADSHEET_RANGES_Labs[1]}"
    elif i == 3 and activity_number == 5:
        return  f"Laboratorio 5!{SPREADSHEET_RANGES_Labs[3]}"
    elif i == 4 and activity_number == 5:
        return f"Laboratorio 5!{SPREADSHEET_RANGES_Labs[4]}"
    else:
        return f"Laboratorio 5!{SPREADSHEET_RANGES_Labs[5]}"
    


def get_students_from_csv(course, group, file_name):
    """
    Reads a csv file containing the students grades and returns a list of students.
    """
    students = []
    with open(file_name, newline='') as csv_file:
        reader = csv.reader(csv_file)
        students = [row for row in reader if row[0]
                    == course and row[1] == group]
    return students


def get_grades(students, activity_number):
    """
    Gets each student's grade for the activity that you are evaluating.
    """
    ind = False
    if activity_number == "p01":
        i = 2
        activity_number = 1
        ind = True
    elif activity_number == "p02":
        activity_number = 2
        i = 2
        ind  = True
    else:
        i = 2
    
    grades = []
    
    for student in students:
        # Tuple of student ID and grade
        entry = (student[i], float(student[activity_number+5]))
        entry1 = (student[i+2], float(student[activity_number+5]))
        grades.append(entry)
        grades.append(entry1)
    
    return grades


def choose_sheet(course, group):
    """
    Chooses a google sheet depending on the course and group.
    """
    return SPREADSHEETS_ID_LIST[course][group]


def choose_range(activity_number):
    """
    Chooses a range depending on the specified activity.
    """
    if activity_number == "p01":
        return f"Proyecto!{SPREADSHEET_RANGES_Project[1]}"
    elif activity_number == "p02":
        return f"Proyecto!{SPREADSHEET_RANGES_Project[2]}"
        

    # For now, this means that it only works with one type of activity.
    return f"Talleres en Sala!{SPREADSHEET_RANGES[activity_number]}"


def get_ids_from_sheet(sheet, sheet_id, p, p1, p2, p3, p4, p5, activity_number):
    """
    Get the student ids from a sheet.
    """
    # For now, this means that it only works with one type of activity.
    if p == True:
        
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range="Proyecto!C4:C41").execute()
    if p2 == True:
        result = sheet.values().get(spreadsheetId=sheet_id, range="Laboratorio" +
                                    " "+str(activity_number)+"!A4:A41").execute()
    if p1 == True:
        result = sheet.values().get(spreadsheetId=sheet_id, range="Laboratorio" +
                                    " "+str(activity_number)+"!A4:A41").execute()
    if p3 == True:
        result = sheet.values().get(spreadsheetId=sheet_id, range="Laboratorio" +
                                    " "+str(activity_number)+"!A4:A41").execute()
    if p4 == True:
        result = sheet.values().get(spreadsheetId=sheet_id, range="Laboratorio" +
                                    " "+str(activity_number)+"!A4:A41").execute()
    if p5 == True:
        result = sheet.values().get(spreadsheetId=sheet_id, range="Laboratorio" +
                                    " "+str(activity_number)+"!A4:A41").execute()
    if p == False:
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range="Talleres en Sala!A4:A41").execute()
    
    values = result.get("values", [])

    ids = []
    if not values:
        print("ERROR!: No ID data found in the google sheet")
        exit(1)
    else:
        ids = [row[0] for row in values]

    return ids


def sort_grades(grades, ids):
    """
    Sort the grades so that they are in the same order in which the students ids appear in the google sheet.
    """
    # TODO: Look for a way to optimize this process!!.
    sorted_grades = []
    for student_id in ids:
        found_id = False
        for entry in grades:
          
            if entry[0] == student_id:
                sorted_grades.append(entry[1])
                found_id = True
                # Go to the next student id
                break
        if not found_id:
            sorted_grades.append("NaN")

    return sorted_grades


def verify_credentials(creds):
    """
    Verifies that a token.pickle file with valid credentials exists in the current working directory.
    If it does, it's credentials are loaded into the creds variable,
    else, it tries to create one.
    """
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def bad_usage():
    """
    Prints a Usage message and exits with error code 1.
    """
    print("Usage: python3 update_grades.py {ed1|ed2} {01|02|03} {1|2|..|12}")
    exit(1)


if __name__ == '__main__':
    main(sys.argv)
