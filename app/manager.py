# This program does all he heavy lifting for the actual server in main.py (and for command.py)

import mariadb
import hashlib
import os

# set by other programs
PASSWORD = ""

# sets up a connection to the db
def getconn():
	connection = mariadb.connect(user="root", host="mariadb", password=PASSWORD, autocommit=True)
	cur = connection.cursor()
	cur.execute("USE TLIS;")
	cur.close()
	return connection

# executes query with data substituting ?s and then returns (if ret true)
def query(squery, qdata=None, ret=True):
	if not qdata:
		pass
	elif type(qdata) == type([]) or type(qdata) == type(("i", "tuple")):
		qdata = tuple(qdata)
	else:
		qdata = (qdata,)

	connection = getconn()

	print(squery)

	with connection:

		cur = connection.cursor()

		if qdata:
			cur.execute(squery, qdata)
		else:
			cur.execute(squery)

		rows = []

		if ret:
			rows = cur.fetchall()

		cur.close()

		return(rows)

# object with all them types
types = {
	"Asset":
		{
		"db":"assets",
		"template":{"id": 0, "asset_type": 0, "asset_number": ""},
		"create":"INSERT INTO assets (type, number) VALUES (?, ?) RETURNING id;",
		"update": "UPDATE assets SET type = ?, number = ? WHERE id = ?;",
		"get": "SELECT id, type, number FROM assets;"
		},
	"Customer":
		{
		"db":"customers",
		"template":{"id": 0, "number": "", "first_name": "", "last_name": "", "email": "", "grade": 0, "staff": 0},
		"create":"INSERT INTO customers (number, first_name, last_name, email, grade, staff) VALUES (?, ?, ?, ?, ?, ?) RETURNING id;",
		"update": "UPDATE customers SET number = ?, first_name = ?, last_name = ?, email = ?, grade = ?, staff = ? WHERE id = ?",
		"get": "SELECT id, number, first_name, last_name, email, grade, staff FROM customers;"
		},
	"Tech":
		{
		"db":"techs",
		"template":{"id": 0, "customer_id": 0, "username":""},
		"create":"INSERT INTO techs (customer_id, username, permission, password, salt) VALUES (?, ?, ?, ?, ?) RETURNING id;",
		"update": "UPDATE techs SET customer_id = ?, username = ?, permission = ?, password = ?, salt = ? WHERE id = ?;",
		"get": "SELECT id, customer_id, username FROM techs;",
		"perms": ["tlis_sysadmin", "tlis_manager", "tlis_tech"]
		},
	"AssetType":
		{
		"db":"asset_types",
		"template":{"id": 0, "name": "", "prefix": "", "default_duration": 0, "description": ""},
		"create":"INSERT INTO asset_types (name, prefix, max_time_out, description) VALUES (?, ?, ?, ?) RETURNING id;",
		"update": "UPDATE asset_types SET name = ?, prefix = ?, max_time_out = ?, description = ? WHERE id = ?;",
		"get": "SELECT id, name, prefix, max_time_out, description FROM asset_types;"
		},
	"TransactionType":
		{
		"db":"transaction_types",
		"template":{"id": 0, "name": "", "description": ""},
		"create":"INSERT INTO transaction_types (name, description) VALUES (?, ?) RETURNING id;",
		"update": "UPDATE transaction_types SET name = ?, description = ? WHERE id = ?;",
		"get": "SELECT id, name, description FROM transaction_types;"
		},
	"Checkout":
		{
		"db":"transactions_out",
		"template":{"id":0, "asset_id":0, "customer_id":0, "tech_id":0, "transaction_type":0, "time":0, "time_due":0, "notes":""},
		"create":"INSERT INTO transactions_out (asset_id, customer_id, tech_id, type, time_now, time_due, notes) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id;",
		"update": "UPDATE transactions_out SET asset_id = ?, customer_id = ?, tech_id = ?, type = ?, time_now = ?, time_due = ?, notes = ? WHERE id = ?",
		"get": "SELECT id, asset_id, customer_id, tech_id, type, time_now, time_due, notes FROM transactions_out;"
		},
	"Checkin":
		{
		"db":"transactions_in",
		"template":{"id":0, "transaction_type":0, "tech_id":0, "time":0, "notes":""},
		"create":"INSERT INTO transactions_in (id, type, tech_id, time_now, notes) VALUES (?, ?, ?, ?, ?) RETURNING id;",
		"update": "UPDATE transactions_in SET type = ?, tech_id = ?, time_now = ?, notes = ? WHERE id = ?;",
		"get": "SELECT id, type, tech_id, time_now, notes FROM transactions_in;"
		},
}

# function that runs when a normal request is sent
def run(data):

	if data["action"] == "ADD":

		if(data["type"] == "Tech"):
			ppassword = data["password"]
			data["salt"] = os.urandom(32)
			data["password"] = hashlib.pbkdf2_hmac('sha256', data["password"].encode('utf-8'), salt, 100000)
			query(f"CREATE USER ? INDENTIFIED BY '?'", (data['username'], ppassword), ret=False)
			query(f"GRANT ? TO ?", (types['Tech']['perms'][data['permission']], data['username']), ret=False)

		print(data.values())
		data["id"] = query(types[data["type"]]["create"], list(data.values())[2:])[0][0]

	elif data["action"] == "UPDATE":

		id = data["id"]
		del data["id"]
		query(types[data["type"]]["update"], list(data.values())[2:] + [id], False)
		data["id"] = id

		if(data["type"] == "Tech"):
			for role in types["Tech"]["perms"]:
				users = query(f"SELECT user FROM mysql.user WHERE is_role='?'", (role))[0]
				if(data["username"] in users):
					query(f"REVOKE ? FROM ?", (role, username), ret=False)
			query(f"GRANT ? TO ?", (types['Tech']['perms'][data['permission']], data['username']), ret=False)

	elif data["action"] == "DELETE":

		if(data["type"] == "Tech"):
			username = query(f"SELECT username FROM techs WHERE id = ?", (data['id']))[0][0]
			query(f"DROP USER ?", (username), ret=False)

		query(f"DELETE FROM ? WHERE id = ?", (types[data['type']]['db'], data['id']), ret=False)

	else:
		data = {"type":"Error", "error_type":"TOM", "reason":"no action given"}

	return data

# where user is authed on login
def auth(data):

	print("auth has begun")

	result = query("SELECT password, salt, permission FROM techs WHERE username = ?;", data["username"])[0]

	key = result[0]
	salt = result[1]
	permission = result[2]
	password_to_check = data["password"]
	print(password_to_check)

	new_key = hashlib.pbkdf2_hmac(
		'sha256',
		password_to_check.encode('utf-8'),
		salt,
		100000
	)

	key = key[:32]

	print("auth has completed")

	if new_key == key:

		return True, permission

	else:

		return False, permission

# gets all record in db and sends to users
def login():

	data = []

	for obj in types:

		result = query(types[obj]["get"])

		for row in result:

			final = types[obj]["template"].copy()
			i = 0
			for key in final.keys():
				final[key] = row[i]
				i += 1

			data.append(final)

	return data
