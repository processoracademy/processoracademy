#!/usr/bin/env python3
import os
import re
import random
import string
import sys
import json

id_file = "./.github/ids.json"
id_pattern = re.compile(r"^<!-- ID: ([a-zA-Z0-9]{1,}) -->$")
new_id_size = 6
ids = {}
found_ids = {}
gen_id_queue = []

def generate_id(max_attempts=5):
    for _ in range(max_attempts):
        new_id = "".join(random.choices(string.ascii_letters + string.digits, k=new_id_size))
        if new_id not in ids:
            return new_id
    print(f"ERROR: Failed to generate a unique ID after {max_attempts} attempts")
    sys.exit(1)

def add_id_to_file(file_path, file_id):
    with open(file_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(f"<!-- ID: {file_id} -->\n{content}")

# Load existing IDs from JSON file
os.makedirs(os.path.dirname(id_file), exist_ok=True)
if os.path.exists(id_file):
    with open(id_file, "r") as f:
        ids = json.load(f)
else:
    print(f"WARN: {id_file} not found. Creating new ID file...")

# Load IDs from markdown files, if no ID is found, add it to the queue for generation
for root, _, files in os.walk("."):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, ".")
            with open(file_path, "r") as f:
                first_line = f.readline().strip()
            match = id_pattern.match(first_line)
            if match:
                found_ids[match.group(1)] = rel_path
            else:
                gen_id_queue.append(file_path)

# Check for path changes and duplicates
for token, path in ids.items():
    if token in found_ids:
        if path != found_ids[token]:
            print(f"Updating rel path for ID {token} from {path} to {found_ids[token]}")
            ids[token] = found_ids[token]
    else:
        print(f"ERROR: ID {token} not found in any files")
        sys.exit(1)

# Add untracked IDs to the list
for token, path in found_ids.items():
    if token not in ids:
        print(f"WARN: Adding untracked ID {token} from {path}")
        ids[token] = path

# Generate new IDs for files without them
for file_path in gen_id_queue:
    file_id = generate_id()
    rel_path = os.path.relpath(file_path, ".")
    print(f"Adding new ID {file_id} to {rel_path}")
    add_id_to_file(file_path, file_id)
    ids[file_id] = rel_path

# Write updated IDs to the JSON file
with open(id_file, "w") as f:
    json.dump(ids, f, indent=2)

print("Successfully validated/updated all IDs")