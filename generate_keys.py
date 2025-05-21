from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import base64
import datetime
from dateutil.relativedelta import relativedelta # For easy month iteration

# --- Konfiguration ---
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem" # Optional: Zum Speichern des öffentlichen Schlüssels
NUMBER_OF_MONTHS_TO_GENERATE = 3 # Current + next 2 months

# --- Funktionen ---
def load_private_key(filename):
    """Lädt den privaten Schlüssel aus einer PEM-Datei."""
    try:
        with open(filename, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None # Set password if the key is encrypted
            )
        return private_key
    except FileNotFoundError:
        print(f"Fehler: Private Schlüsseldatei nicht gefunden: {filename}")
        print("Bitte stellen Sie sicher, dass die Datei existiert und das Skript im richtigen Verzeichnis ausgeführt wird.")
        exit(1)
    except Exception as e:
        print(f"Fehler beim Laden des privaten Schlüssels: {e}")
        exit(1)

def sign_data(private_key, data_bytes):
    """Signiert die gegebenen Bytes mit dem privaten Schlüssel."""
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

# --- Hauptlogik ---
if __name__ == "__main__":
    print(f"Lade privaten Schlüssel aus {PRIVATE_KEY_FILE}...")
    private_key = load_private_key(PRIVATE_KEY_FILE)
    print("Privater Schlüssel geladen.")

    today = datetime.date.today()
    print(f"\nGeneriere Lizenzschlüssel für den aktuellen und die nächsten {NUMBER_OF_MONTHS_TO_GENERATE - 1} Monate (Basis: {today.strftime('%Y-%m-%d')}):")
    print("-" * 70)

    current_month_start = datetime.date(today.year, today.month, 1)

    for i in range(NUMBER_OF_MONTHS_TO_GENERATE):
        target_date = current_month_start + relativedelta(months=i)
        month_str = target_date.strftime("%Y-%m")
        data_to_sign = month_str.encode('utf-8')

        license_key = sign_data(private_key, data_to_sign)

        print(f"Monat: {month_str}  | Lizenzschlüssel: {license_key}")

    print("-" * 70)
    print("Generierung abgeschlossen.")

# --- Veralteter Code zum Generieren --- 
# (Der alte Code zum Generieren und Speichern wird entfernt)
# KEY_SIZE = 2048
# PUBLIC_EXPONENT = 65537
# LICENSE_DATA = b"2025-04" # Die Daten, die signiert werden (aktueller Monat)
# ... (Rest des alten Codes hier entfernt) ...

# 1. Schlüsselpaar generieren
# private_key = rsa.generate_private_key(
#     public_exponent=PUBLIC_EXPONENT,
#     key_size=KEY_SIZE
# )
# public_key = private_key.public_key()

# 2. Privaten Schlüssel speichern (PEM Format, verschlüsselt empfohlen, hier unverschlüsselt zur Einfachheit)
# pem_private = private_key.private_bytes(
#    encoding=serialization.Encoding.PEM,
#    format=serialization.PrivateFormat.PKCS8,
#    encryption_algorithm=serialization.NoEncryption() # In Produktion: serialization.BestAvailableEncryption(b'dein_passwort')
# )
# with open(PRIVATE_KEY_FILE, "wb") as f:
#     f.write(pem_private)
# print(f"Privater Schlüssel gespeichert in: {PRIVATE_KEY_FILE} (SICHER AUFBEWAHREN!)")

# 3. Öffentlichen Schlüssel ausgeben (PEM Format)
# pem_public = public_key.public_bytes(
#    encoding=serialization.Encoding.PEM,
#    format=serialization.PublicFormat.SubjectPublicKeyInfo
# )
# Optional: Öffentlichen Schlüssel auch in Datei schreiben
# with open(PUBLIC_KEY_FILE, "wb") as f:
#    f.write(pem_public)
# print(f"Öffentlicher Schlüssel gespeichert in: {PUBLIC_KEY_FILE}")

# print("\n----- Öffentlicher Schlüssel (für main.py) -----")
# print(pem_public.decode('utf-8'))
# print("----- Ende Öffentlicher Schlüssel -----")


# 4. Lizenzschlüssel für den Monat generieren (Signatur)
# signature = private_key.sign(
#     LICENSE_DATA,
#     padding.PSS(
#         mgf=padding.MGF1(hashes.SHA256()),
#         salt_length=padding.PSS.MAX_LENGTH
#     ),
#     hashes.SHA256()
# )

# Signatur in Base64 kodieren für einfachere Weitergabe/Eingabe
# license_key = base64.b64encode(signature).decode('utf-8')

# print(f"\n----- Lizenzschlüssel für {LICENSE_DATA.decode('utf-8')} -----")
# print(license_key)
# print("----- Ende Lizenzschlüssel -----") 