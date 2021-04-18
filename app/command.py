# Welcome to the tlis_server import script!
# This thing allows for importation into the tlis database through csvs
# If you need a refresher on the actual command just run tlis_server
# If you plan to mess with the code, good luck
# This code was written by Tyler Geist
# (also this needs to be run as root)

import argparse
import manager
import csv
import os
import hashlib

# get dbs from the manager file
dbs = manager.types
finaldbs = list(dbs)

description = '''
Helper script for the TLIS server
'''

# parser is what allows for auto command line input
parser = argparse.ArgumentParser(prog='tlis-server', description=description)

parser.add_argument('database_name',
                    help='Name of database you are inserting data into',
					choices=finaldbs)

parser.add_argument('csv_path', type=open,
                    help='Path to the csv file')

parser.add_argument('-c', '--clear', action='store_true',
                    help='Clears the database')

parser.add_argument('-n', '--no-header', action='store_true',
                    help='Acts like the csv file has no header', dest="no_header")

# get args
args = parser.parse_args()

csv_file = args.csv_path

rows = []

csv_reader = csv.reader(csv_file, delimiter=',')

# process csv with or without headers
line_count = 0
for row in csv_reader:
    if line_count == 0 and not args.no_header:
        line_count += 1
    else:
        rows.append(row)
        line_count += 1

# get that password
manager.PASSWORD = os.getenv('DB_PASSWORD')

# put the thing (data) in the thing (database)
for row in rows:

	if args.database_name == "Tech":
		salt = os.urandom(32)
		print(salt)
		key = hashlib.pbkdf2_hmac('sha256', row[2].encode('utf-8'), salt, 100000)
		print(key)
		row[2] = key
		row.append(salt)

	if len(row) == len(dbs[args.database_name]["template"]) - 1 or args.database_name == "Tech":
		print(f"Wrote row {row} to database {args.database_name}")
		manager.query(dbs[args.database_name]["create"], row)
