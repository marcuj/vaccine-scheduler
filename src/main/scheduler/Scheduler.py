import os
import sys

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    print_start()


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)
    print_start()


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient
    print_start()


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver
    print_start()


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    date = tokens[1]
    date_tokens = date.split("-")
    if len(date_tokens) != 3:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[0]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[1]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[2]) != 4:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    find_availabilities = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username asc"
    get_vaccines = "SELECT Name, Doses FROM Vaccines WHERE Doses > 0"
    try:
        cursor1 = conn.cursor(as_dict=True)
        d = datetime.datetime(year, month, day)
        cursor1.execute(find_availabilities, d)
        count = 0
        for row in cursor1:
            if count == 0:
                print("Available caregivers for "+str(date)+":", end=" ")
                print(str(row['Username']), end=" ")
            else:
                print(", "+str(row['Username']), end=" ")
            count += 1
        if count == 0:
            print("Sorry, there are no appointments available for this date.")
            print_start()
            return
        else:
            print()
        cursor2 = conn.cursor(as_dict=True)
        cursor2.execute(get_vaccines)
        count = 0
        for row in cursor2:
            if count == 0:
                print("Vaccines available:", end=" ")
                print(str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
            else:
                print(", "+str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
            count += 1
        if count == 0:
            print("No vaccines available.")
        else:
            print()
    except pymssql.Error as e:
        print("Search Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when searching for availability")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print_start()


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    if current_patient is None:
        print("Please login as a patient first!")
        return

    if len(tokens) != 3:
        print("Invalid input. Please enter in the form <mm-dd-yyyy> <vaccine>.")
        return

    # add to appointments, remove from availabilities
    cm = ConnectionManager()
    conn = cm.create_connection()

    date = tokens[1]
    date_tokens = date.split("-")
    if len(date_tokens) != 3:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[0]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[1]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[2]) != 4:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)
    vaccine_name = tokens[2]

    if vaccine_name is '':
        print("Invalid input. Please enter in the form <mm-dd-yyyy> <vaccine>.")
        return

    get_appointments = "SELECT id_num, User_caregiver FROM Appointments WHERE User_patient = %s"
    find_caregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY Username asc"
    get_vaccines = "SELECT Name, Doses FROM Vaccines WHERE Doses > 0"
    add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
    remove_availability = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_appointments, current_patient.get_username())
        if cursor.fetchone() is not None:
            print("You already have a vaccination appointment reserved. To create a new one, please cancel your current appointment.")
            return
        vaccine = Vaccine(vaccine_name, 0).get()
        if vaccine is None:
            print("The "+str(vaccine_name)+" vaccine is not administered here.")
            cursor2 = conn.cursor(as_dict=True)
            cursor2.execute(get_vaccines)
            count = 0
            for row in cursor2:
                if count == 0:
                    print("Vaccines available:", end=" ")
                    print(str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
                else:
                    print(", "+str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
                count += 1
            if count == 0:
                print("No other vaccines available.")
            else:
                print()
            return
        if vaccine.get_available_doses() > 0:
            cursor1 = conn.cursor(as_dict=True)
            cursor1.execute(find_caregiver, d)
            row = cursor1.fetchone()
            if row is None:
                print("Sorry, no caregiver is available for this date. Use the search_caregiver_schedule function to find availabilities.")
                return
            else:
                caregiver = str(row['Username'])
                cursor1.execute(remove_availability, (d, caregiver))
                cursor1.execute(add_appointment, (d, caregiver, current_patient.get_username(), vaccine_name))
                vaccine.decrease_available_doses(1)

                cursor2 = conn.cursor(as_dict=True)
                cursor2.execute(get_appointments, current_patient.get_username())
                row = cursor2.fetchone()
                print("Appointment created!")
                print("Appointment ID: "+str(row['id_num'])+", Caregiver username: "+str(row['User_caregiver']))
                conn.commit()
        else:
            print("The "+str(vaccine_name)+" vaccine is out of stock.")
            cursor2 = conn.cursor(as_dict=True)
            cursor2.execute(get_vaccines)
            count = 0
            for row in cursor2:
                if count == 0:
                    print("Vaccines available:", end=" ")
                    print(str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
                else:
                    print(", "+str(row['Name'])+" ("+str(row['Doses'])+" left)", end=" ")
                count += 1
            if count == 0:
                print("No other vaccines available.")
            else:
                print()
    except pymssql.Error as e:
        print("Reserve Appointment Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when reserving appointment")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print_start()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    if len(date_tokens) != 3:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[0]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[1]) != 2:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    if len(date_tokens[2]) != 4:
        print("Invalid date. Please enter in the form mm-dd-yyyy.")
        return
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        get_appointments = "SELECT * FROM Appointments WHERE User_caregiver = %s AND Time = %s"
        get_availability = "SELECT * FROM Availabilities WHERE Username = %s AND Time = %s"
        d = datetime.datetime(year, month, day)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_appointments, (current_caregiver.get_username(), d))
        guy = cursor.fetchone()
        cursor.execute(get_availability, (current_caregiver.get_username(), d))
        guy2 = cursor.fetchone()
        if guy is not None:
            print("Invalid date. You have an appointment on this date.")
            return
        elif guy2 is not None:
            print("Invalid date. You've already uploaded an availability for this date.")
            return
        else:
            current_caregiver.upload_availability(d)
            print("Availability uploaded!")
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print_start()


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    global current_caregiver
    # Remove appointment, add availability, add vaccine dose
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 2:
        print("Invalid ID. Enter an integer.")
        return

    id_num = tokens[1]
    try:
        id_num = int(id_num)
    except ValueError:
        print("Invalid ID. Enter an integer.")
        return

    get_appointments = ""
    username = ""
    if current_caregiver is not None:
        get_appointments = "SELECT * FROM Appointments WHERE User_caregiver = %s AND id_num = %s"
        username = current_caregiver.get_username()
    elif current_patient is not None:
        get_appointments = "SELECT * FROM Appointments WHERE User_patient = %s AND id_num = %s"
        username = current_patient.get_username()
    remove_appointment = "DELETE FROM Appointments WHERE id_num = %s"
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_appointments, (username, id_num))
        row = cursor.fetchone()
        if row is None:
            print("Invalid ID. You do not have an appointment with the given ID. Type show_appointments to see your appointments.")
            return
        else:
            d = row['Time']
            v = str(row['Vaccine'])
            c = str(row['User_caregiver'])
            caregiver = Caregiver(c)
            cursor.execute(remove_appointment, id_num)
            caregiver.upload_availability(d)
            old_stdout = sys.stdout  # backup current stdout
            sys.stdout = open(os.devnull, "w")
            if current_caregiver is None:
                current_caregiver = caregiver
                add_doses([None, v, 1])
                current_caregiver = None
            else:
                add_doses([None, v, 1])
            sys.stdout = old_stdout  # reset old stdout
            print("The appointment (ID: "+str(id_num)+") has been cancelled.")
            conn.commit()
    except pymssql.Error as e:
        print("Appointment Cancel Failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when cancelling appointment")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print_start()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    try:
        doses = int(tokens[2])
    except ValueError:
        print("Invalid number. Enter an integer.")
        return
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")
    print_start()


def show_appointments(tokens):
    """
    TODO: Part 2
    """
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 1:
        print("Error: Do not enter anything after 'show_appointments'.")
        return

    get_appointments = ""
    user = ""
    con = ""
    if current_caregiver is not None:
        get_appointments = "SELECT id_num, Vaccine, Time, User_patient FROM Appointments WHERE User_caregiver = %s ORDER BY id_num asc"
        user = current_caregiver.get_username()
        con = "User_patient"
    elif current_patient is not None:
        get_appointments = "SELECT id_num, Vaccine, Time, User_caregiver FROM Appointments WHERE User_patient = %s ORDER BY id_num asc"
        user = current_patient.get_username()
        con = "User_caregiver"

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_appointments, user)
        count = 0
        for row in cursor:
            if count == 0:
                print("Your appointment(s):")
                count += 1
            print("ID: "+str(row['id_num'])+" | "+str(row['Time'])+", With: "+str(row[con])+", Vaccine: "+str(row['Vaccine']))
        if count == 0:
            print("You have no appointments.")
    except pymssql.Error as e:
        print("Show Appointment Failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when showing appointments")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    print_start()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    else:
        if len(tokens) != 1:
            print("Error: Do not enter anything after 'logout'.")
            return
        print("Successfully logged out!")
        current_caregiver = None
        current_patient = None
    print_start()


def print_start():
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()


def start():
    stop = False
    print_start()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
