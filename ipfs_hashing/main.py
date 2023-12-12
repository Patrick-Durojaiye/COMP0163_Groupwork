import json
import requests
from eth_account import Account
import eth_abi
from web3 import Web3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()
JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJkM2I2NzdiZi05MzEzLTQwY2YtOTFmMi1mZWVkMDRiZWMwMGQiLCJlbWFpbCI6ImdlcmdlbHlzem9yYXRoQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJjMTllYjk3NTRlNDY0OWMxZjEzOCIsInNjb3BlZEtleVNlY3JldCI6IjJhMmQwY2EwNTczMWQ5MzExZmI3MDQwZTUxYWZkYjMxYzY4YjYyY2Y2Yzk1MGQ2ODM1OTM4MzM3ZWEzOTRiYmEiLCJpYXQiOjE3MDIzODYyMTd9.jPK7PZ355FvvaGCbAJjIFou903jr4GkLSjidhG8bkys'
private_key = os.getenv("PRIVATE_KEY")
address = os.getenv("ADDRESS")

# Blockchain RPC Connection
w3 = Web3(Web3.HTTPProvider("https://rpc.sepolia.org"))

# Contract address for patient data
PatientDataContractAddress = "0x9085FFe90E35f854149190d3b9Daa804a62525FD"

# Generate a key for encryption and decryption
# You should store this key securely
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    json_data = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(json_data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data)

# Function to add data to IPFS using Pinata API call
def pin_file_to_ipfs(file_data):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    # Prepare headers
    headers = {
        'Authorization': f'Bearer {JWT}'
    }


# Open the file in binary mode
    files = {
        'file': ('path', file_data)
    }

    # Add metadata and options
    pinata_metadata = {
        'name': 'File name'
    }
    pinata_options = {
        'cidVersion': 0
    }

    payload = {
        'pinataMetadata': json.dumps(pinata_metadata),
        'pinataOptions': json.dumps(pinata_options)
    }

    # Make the POST request
    try:
        response = requests.post(url, files=files, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

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

def run(address, private_key):
    # Load patient data from the JSON file
    with open('patient_data.json', 'r') as file:
        patient_data = json.load(file)
    
    # Encrypt the patient data
    encrypted_patient_data = encrypt_data(patient_data)

    metadata = {
        "Address": "0xxxxx",
        "EMR Data": encrypt_data,
        "Hospital": "London National Hospital"
    }

    # Add the encrypted patient data to IPFS
    ipfs_hash = "ipfs://" + str(pin_file_to_ipfs(encrypted_patient_data))
    acct = Account.from_key(private_key)
    mint_patient_data(acct=acct, address=address, ipfs_hash=ipfs_hash, private_key=private_key)

run(address=address,private_key=private_key)