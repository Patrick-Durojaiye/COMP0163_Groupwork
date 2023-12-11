import hashlib
import json
import requests

# Function to hash metadata
def hash_metadata(metadata):
    # Convert the metadata dictionary to a JSON string
    metadata_json = json.dumps(metadata, sort_keys=True)
    # Create a SHA-256 hash of the JSON string
    return hashlib.sha256(metadata_json.encode()).hexdigest()

# Load patient data from the JSON file
with open('patient_data.json', 'r') as file:
    patient_data = json.load(file)

# Hash the metadata
hashed_metadata = hash_metadata(patient_data)

# Function to add data to IPFS using direct API call
def add_to_ipfs(data):
    response = requests.post('http://127.0.0.1:5001/api/v0/add', files={'file': ('metadata.json', data)})
    if response.status_code != 200:
        raise Exception(f"IPFS add failed: {response.text}")
    return response.json()['Hash']

# Add the hashed metadata to IPFS
ipfs_hash = add_to_ipfs(hashed_metadata.encode())

# Output the IPFS hash
print(f"IPFS Hash: {ipfs_hash}")

# The IPFS hash can be used as the token URI in the smart contract
token_uri = f"ipfs://{ipfs_hash}"
