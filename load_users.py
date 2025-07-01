from tinydb import TinyDB
import json

# Load your user data from sample_interests.json
with open('sample_interests.json', 'r') as f:
    data = json.load(f)

# Open (or create) db.json, your TinyDB database
db = TinyDB('db.json')
db.truncate()  # Clears all current data from the DB

# Insert all users from your JSON file into TinyDB
db.insert_multiple(data['users'])

print("Users loaded into TinyDB!")
# You can now use the db object to query or manipulate your user data  