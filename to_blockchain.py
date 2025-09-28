from web3 import Web3
import hashlib
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet




load_dotenv()  # take environment variables

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = os.getenv("ACCOUNT")
PROVIDER_URL = os.getenv("PROVIDER_URL")
KEY_FILE = os.getenv("KEY_FILE")
ENC_FULL_OR_NOT = os.getenv("ENC_FULL_OR_NOT") == "True"

# -------------------------------
# 读取密钥
# -------------------------------
def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

# -------------------------------
# 3) 加解密
# -------------------------------
def encrypt_text(plaintext: str, fernet: Fernet) -> str:
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

def decrypt_text(token: str, fernet: Fernet) -> str:
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")

def enc_full_or_not(title,content):
    if  ENC_FULL_OR_NOT:
        #全加密
        key = load_key()
        cipher = Fernet(key)
        title_enc = encrypt_text(title,cipher)
        content_enc = encrypt_text(content,cipher)
        return title_enc,content_enc
    else:
        return title,content


contract_abi = [
	{
		"inputs": [],
		"name": "deleteUserInfo",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_content_hash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_content",
				"type": "string"
			}
		],
		"name": "setUserMemo",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_content_hash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_title",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_content",
				"type": "string"
			}
		],
		"name": "updateUserMemo",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAllUsers",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "userAddress",
				"type": "address"
			}
		],
		"name": "getUserMemo",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "content_hash",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "title",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "content",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct SimpleDatabase.UserInfo[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
contract_address = CONTRACT_ADDRESS  # 合约地址
private_key = PRIVATE_KEY
account = ACCOUNT

web3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def set_user_memo(title, content):
    content_hash = sha256_hash(content)
    title_enc, content_enc = enc_full_or_not(title,content)
    account = web3.eth.account.from_key(private_key)
    
    transaction = contract.functions.setUserMemo(content_hash, title_enc, content_enc).build_transaction({
        'from': account.address,
        'gas': 2000000,
        'gasPrice': web3.to_wei('2', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account.address),
    })
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    print(f'Transaction sent: {tx_hash.hex()}')

def get_user_memo(user_address):
    user_info = contract.functions.getUserMemo(user_address).call()
    print(user_info)
    return user_info

def get_all_users():

	users_info = contract.functions.getAllUsers().call()
	print(users_info)
	return users_info


def sha256_hash(text):
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    print("SHA-256:", sha256_hash)
    return sha256_hash



# get_all_users()

# get_user_info(account)
# set_user_info('0xf39Fd6e51a', 'bbbbb南昌南昌')