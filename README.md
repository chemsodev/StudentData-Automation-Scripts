# Google Sheets Scraper and MySQL Data Inserter

This Python script automates the process of scraping student data from Google Sheets URLs, processing the data, and inserting it into a MySQL database. It extracts Google Sheets URLs from a specified webpage, retrieves specific fields, checks for existing entries in the database, and inserts new student data into the appropriate tables.

## Features

- **Web Scraping**: Automatically retrieves Google Sheets URLs from a specified webpage.
- **Google Sheets API Integration**: Authenticates and accesses Google Sheets to extract student data.
- **MySQL Database Integration**: Inserts the scraped data into a MySQL database while avoiding duplicate entries for specialities and sections.
- **Batch Processing**: Processes sheets in batches with a delay to prevent API rate limiting.

## Requirements

- **Python 3.x**: The script is written in Python and requires Python 3.x to run.
- **Google Sheets API Credentials**: Service account credentials in JSON format are required to access the Google Sheets API.
- **MySQL Server**: The script connects to a MySQL database to store the extracted data.
- **Optional SSL for MySQL**: SSL configuration can be used to securely connect to the database.

### Required Python Libraries

- `requests`
- `beautifulsoup4`
- `gspread`
- `oauth2client`
- `mysql-connector-python`

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/chemsodev/StudentData-Automation-Scripts.git
    ```

2. **Navigate to the project directory**:
    ```bash
    cd StudentData-Automation-Scripts
    ```

3. **Install dependencies**:
    Install the required Python libraries by running:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your environment**:
    - **Google Sheets API**: Add your Google Service Account credentials in JSON format to the project folder.
    - **MySQL Configuration**: Configure MySQL connection details (host, user, password, database, etc.) in `config.py`.

5. **Database Setup**:
    Create the necessary MySQL tables by running the following SQL commands:

    ```sql
    CREATE TABLE specialities (
        id INT AUTO_INCREMENT PRIMARY KEY,
        palier VARCHAR(255),
        specialite VARCHAR(255)
    );

    CREATE TABLE sections (
        id INT AUTO_INCREMENT PRIMARY KEY,
        section_name VARCHAR(255)
    );

    CREATE TABLE students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        matricule VARCHAR(255),
        nom VARCHAR(255),
        prenom VARCHAR(255),
        etat VARCHAR(255),
        groupe_td VARCHAR(255),
        speciality_id INT,
        section_id INT,
        number VARCHAR(255),
        FOREIGN KEY (speciality_id) REFERENCES specialities(id),
        FOREIGN KEY (section_id) REFERENCES sections(id)
    );
    ```

## Usage

1. **Run the script**:
    Use the following command to run the script:
    ```bash
    python main.py
    ```

2. The script will:
    - Scrape the Google Sheets URLs from the specified webpage.
    - Extract student data from the Sheets.
    - Insert the data into the MySQL database, ensuring no duplicate entries for sections and specialities.

## Configuration

- **Batch Size**: You can adjust the number of Google Sheets processed per batch by modifying the `batch_size` variable in `config.py`.
- **Delay Between Batches**: Control the delay between batch processing with the `delay_between_batches` variable to avoid API rate limiting.

## Planned Improvements

- Add support for scraping student data from different sources (e.g., CSVs, APIs).
- Enhance logging for better tracking, debugging, and error handling.
- Automatically detect schema changes in Google Sheets to handle updates dynamically.

## Contribution

Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a pull request once your changes are ready.

Feel free to open issues or discussions for any ideas or improvements.

## License

This project is licensed under the MIT License.
