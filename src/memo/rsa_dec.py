from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables

PUBLIC_FILE = os.getenv("PUBLIC_FILE")
PRIVATE_FILE = os.getenv("PRIVATE_FILE")


# 2. 公钥加密
def rsa_encrypt(message, public_key):
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # print("密文：", ciphertext)
    return ciphertext

def rsa_decrypt(ciphertext: str, private_key):
    # 3. 私钥解密
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # print("解密结果：", plaintext.decode())
    return plaintext.decode()


    
# password = b''
def save_pem(public_key,private_key,password = None):
    # 4. 可选：保存密钥为 PEM 格式
    if password == None:
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
            # encryption_algorithm=serialization.BestAvailableEncryption(password)
        )  
    else:      
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(PRIVATE_FILE, "wb") as f: f.write(pem_private)
    with open(PUBLIC_FILE, "wb") as f: f.write(pem_public)

def key_maker(password = None):
    # 1. 生成 RSA 密钥对
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    save_pem(public_key,private_key,password)
    
def load_public(public_file=PUBLIC_FILE):
    with open(public_file, "rb") as f:
        public_pem_data = f.read()
    public_key = serialization.load_pem_public_key(public_pem_data)
    return public_key

def load_private(private_file = PRIVATE_FILE,password = None):
    # 读取 PEM 文件
    with open(private_file, "rb") as f:
        pem_data = f.read()
    # 如果私钥没有加密（无密码保护）
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=password,
    )
    return private_key


# message = b"HELLO123321"
# ciphertext = rsa_encrypt(message)
# rsa_decrypt(ciphertext)
# save_pem()

# public_key = load_public()
# private_key = load_private()

# @app.route("/encrypt", methods=["POST"])
# def encrypt():
#     message = request.form.get("message").encode("utf-8")
#     ciphertext = rsa_encrypt(message,public_key)
#     return ciphertext

import os
import getpass
def make_key():
    public_file=PUBLIC_FILE
    if not os.path.exists(public_file):
        password = getpass.getpass("输入私钥密码：").strip()
        if password == '':
            key_maker(password=None)
        else:
            key_maker(password.encode())
    else:
        print('已经存在，无需生成')


# app.run(debug=True)
# a = input('输入私钥密码：')

# message = b"HELLO123321"

# public_key = load_public()
# private_key = load_private(password=b'123456')
# ciphertext = rsa_encrypt(message,public_key)
# rsa_decrypt(ciphertext,private_key)

