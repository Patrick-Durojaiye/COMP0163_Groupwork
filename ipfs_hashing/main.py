import hashlib
import json
import requests
from eth_account import Account
import eth_abi
from web3 import Web3

# Blockchain RPC Connection
w3 = Web3(Web3.HTTPProvider("https://rpc.sepolia.org"))

# Contract address for patient data
PatientDataContractAddress = "0x9085FFe90E35f854149190d3b9Daa804a62525FD"

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

# Builds the transaction data to mint the token
def build_mint_data(address, ipfs_hash):
    partial_calldata = eth_abi.encode_abi(["address", "string"], [address, ipfs_hash]).hex()
    return "0xd0def521"+partial_calldata

# Gets the transaction data of the mint and submits it to the blockchain
def mint_patient_data(acct:Account, address, ipfs_hash, private_key):
    data = build_mint_data(address=address, ipfs_hash=ipfs_hash)
    tx = {
        "from": w3.toChecksumAddress(acct.address),
        "to": w3.toChecksumAddress(address),
        "value" : w3.toWei(0,'ether'),
        "data": data,
        "chainId" : 11155111,
        "gas": 28363240,
        "gasPrice": w3.toWei("800","gwei"),
        "nonce": w3.eth.get_transaction_count(acct.address)
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_mint = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    try:
        w3.eth.wait_for_transaction_receipt(tx_mint, timeout=60)
    except:
        print("Tx lost in mempool")

