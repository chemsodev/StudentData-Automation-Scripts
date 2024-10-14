import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import time
import json

# Load configuration from config.json
def load_config():
    with open('config.json') as config_file:
        return json.load(config_file)

# Function to fetch Google Sheets URLs
def fetch_sheet_urls(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [link['href'] for link in soup.find_all('a', href=True) if "docs.google.com/spreadsheets" in link['href']]

# Function to authenticate Google Sheets
def authenticate_google_sheets(json_keyfile_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scope)
    return gspread.authorize(creds)

# Function to connect to the MySQL database
def connect_to_database(mysql_config):
    return mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"],
        port=mysql_config.get("port", 3306),  # Default to 3306 if not specified
        ssl_ca=mysql_config.get("ssl_ca"),  # SSL certificate path, if provided
        ssl_disabled=mysql_config.get("ssl_disabled", False)  # Disable SSL if specified in config
    )

# Function to insert speciality data if it doesn't already exist
def insert_or_get_speciality_id(cursor, palier, specialite):
    select_query = "SELECT id FROM specialities WHERE palier = %s AND specialite = %s"
    cursor.execute(select_query, (palier, specialite))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return the existing id

    # Insert new speciality if not found
    insert_query = "INSERT INTO specialities (palier, specialite) VALUES (%s, %s)"
    cursor.execute(insert_query, (palier, specialite))
    return cursor.lastrowid  # Return the newly inserted id

# Function to insert section data if it doesn't already exist
def insert_or_get_section_id(cursor, section_name):
    select_query = "SELECT id FROM sections WHERE section_name = %s"
    cursor.execute(select_query, (section_name,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Return the existing id

    # Insert new section if not found
    insert_query = "INSERT INTO sections (section_name) VALUES (%s)"
    cursor.execute(insert_query, (section_name,))
    return cursor.lastrowid  # Return the newly inserted id

# Function to insert student data into the database
def insert_student(cursor, student, speciality_id, section_id):
    insert_query = """
    INSERT INTO students (matricule, nom, prenom, etat, groupe_td, speciality_id, section_id, number)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        student['Matricule'],
        student['Nom'],
        student['Prénom'],
        student['Etat'],
        student['Groupe TD'],
        speciality_id,
        section_id,
        student['N°'],
    ))

# Function to process sheets and insert data
def process_sheets(sheet_urls, required_columns, batch_size, delay_between_batches, google_credentials, mysql_config):
    client = authenticate_google_sheets(google_credentials)
    db_connection = connect_to_database(mysql_config)
    cursor = db_connection.cursor()

    for i in range(0, len(sheet_urls), batch_size):
        for url in sheet_urls[i:i + batch_size]:
            try:
                spreadsheet = client.open_by_url(url)
                sheet = spreadsheet.get_worksheet(0)
                headers = [header.strip() for header in sheet.row_values(9) if header.strip()]

                filtered_data = []
                for row in sheet.get_all_values()[9:]:
                    filtered_record = {header: row[index] if index < len(row) else None for index, header in
                                       enumerate(headers) if index < len(required_columns)}

                    if all(col in filtered_record for col in required_columns):
                        filtered_data.append(filtered_record)

                print(f"\nData from {url}:")
                for index, student in enumerate(filtered_data):
                    # Insert specialities and sections first, then get their IDs
                    speciality_id = insert_or_get_speciality_id(cursor, student['Palier'], student['Spécialité'])
                    section_id = insert_or_get_section_id(cursor, student['Section'])

                    # Insert student data
                    insert_student(cursor, student, speciality_id, section_id)

                    print(f"Record {index + 1}: {student}")

                # Commit the transaction after processing each URL
                db_connection.commit()

            except gspread.exceptions.APIError as e:
                print(f"API Error accessing sheet {url}: {str(e)}")
            except Exception as e:
                print(f"Error accessing sheet {url}: {str(e)}")

        print(f"Delaying for {delay_between_batches} seconds before the next batch...")
        time.sleep(delay_between_batches)

    # Close the cursor and database connection
    cursor.close()
    db_connection.close()

if __name__ == "__main__":
    # Load configuration
    config = load_config()

    page_url = config["page_url"]
    required_columns = config["required_columns"]
    batch_size = config["batch_size"]
    delay_between_batches = config["delay_between_batches"]
    google_credentials = config["google_sheets_credentials"]
    mysql_config = config["mysql"]

    sheet_urls = fetch_sheet_urls(page_url)
    process_sheets(sheet_urls, required_columns, batch_size, delay_between_batches, google_credentials, mysql_config)
