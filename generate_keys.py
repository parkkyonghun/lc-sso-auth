from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os

def generate_rsa_key_pair():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

if __name__ == "__main__":
    # Create keys directory if it doesn't exist
    os.makedirs("keys", exist_ok=True)
    
    # Generate keys
    private_key, public_key = generate_rsa_key_pair()
    
    # Write private key
    with open("keys/private_key.pem", "w") as f:
        f.write(private_key)
    
    # Write public key
    with open("keys/public_key.pem", "w") as f:
        f.write(public_key)
    
    print("RSA key pair generated successfully in the 'keys' directory.")
    print("Private key: keys/private_key.pem")
    print("Public key:  keys/public_key.pem")
