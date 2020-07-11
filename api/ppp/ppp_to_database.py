from dotenv import load_dotenv
from pathlib import Path
import os
import time
import json
import psycopg2
import requests
import csv

load_dotenv()

PPP_DIRECTORY = r'C:\Users\Daniel Lee\Desktop\PPP\ppp_data\150k plus'

hostname = 'localhost'
username = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
database = os.environ.get("DB_NAME")

loans_dict = {
    "a $5-10 million": [5000000, 10000000],
    "b $2-5 million": [2000000, 5000000],
    "c $1-2 million": [1000000, 2000000],
    "d $350,000-1 million": [350000, 1000000],
    "e $150,000-350,000": [150000, 350000]
}

class DataImporter:

    def __init__(self):
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cursor = self.connection.cursor()

    def load_csvs(self, directory):
        path = Path(directory)

        for entity in path.iterdir():
            if entity.is_file():
                if ".csv" in str(entity):
                    self.process_csv(entity)
            else:
                self.load_csvs(entity)
        
    def process_csv(self, path):
        name = os.path.basename(path)
        print(f"Processing {name}")

        with open(path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                loan_amount, name, address, city, state, zip_code = row[0], row[1], row[2], row[3], row[4], row[5]
                naics_code, business_type = row[6], row[7]
                ethnicity, gender, veteran, nonprofit = row[8], row[9], row[10], row[11]
                jobs_retained, date_approved, lender = row[12], row[13], row[14]
          
                business_query =  "INSERT INTO ppp_business ( \
                    name, address, city, state, zip_code, naics_code, business_type, ethnicity, gender, veteran, nonprofit \
                ) VALUES ( \
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s \
                )"
                business_data = (name, address, city, state, zip_code, naics_code, business_type, ethnicity, gender, veteran, nonprofit)
                self.cursor.execute(business_query, business_data)
                business_id = self.cursor.fetchone()[0]

                lender_query = "INSERT INTO ppp_lender (name) VALUES (%s)"
                lender_data = (lender)
                self.cursor.execute(lender_query, lender_data)
                lender_id = self.cursor.fetchone()[0]

                loan_lower_bound, loan_upper_bound = loans_dict[loan_amount]
                loan_query = "INSERT INTO ppp_loan (jobs_retained, date_approved, business_id, lender_id, loan_lower_bound, loan_upper_bound \
                ) VALUES ( \
                    %s, %s, %s, %s, %s, %s\
                )"
                loan_data = (jobs_retained, date_approved, business_id, lender_id, loan_lower_bound, loan_upper_bound)
                self.cursor.execute(loan_query, loan_data)
                
        self.connection.commit()
        # businesses = self.cursor.fetchall()
        # for business in businesses:
        #     print(business)

    def close_connection(self):
        self.connection.close()

if __name__=='__main__':
    print("Start import")
    start = time.time()
    importer = DataImporter()
    importer.load_csvs(PPP_DIRECTORY)
    importer.close_connection()
    end = time.time()
    print("Finished import")
    print(f"{end - start} seconds elapsed.")