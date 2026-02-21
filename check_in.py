import psycopg2
from psycopg2.extras import RealDictCursor
from pyzbar.pyzbar import decode
from PIL import Image
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
# Make sure you have DATABASE_URL set in your environment
DATABASE_URL = os.environ.get("DATABASE_URL")  # e.g., from Render env

# Path to QR image you want to scan
QR_IMAGE_PATH = "qr_codes/Ana_Said.png"  # Change this to the actual file

# -----------------------------
# LOAD AND DECODE QR
# -----------------------------
img = Image.open(QR_IMAGE_PATH)
result = decode(img)

if not result:
    print("⚠️ QR code not read.")
    exit()

# Extract unique_id from scanned URL
scanned_data = result[0].data.decode("utf-8")
# Assuming QR contains: https://wedding-qr-system-2.onrender.com/checkin?id=<unique_id>
if "id=" not in scanned_data:
    print("❌ QR code format invalid.")
    exit()

scanned_id = scanned_data.split("id=")[-1].strip()

# -----------------------------
# CONNECT TO DATABASE
# -----------------------------
try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
except Exception as e:
    print(f"❌ Could not connect to database: {e}")
    exit()

cursor = conn.cursor()
cursor.execute("SELECT name, checked_in FROM guests WHERE unique_id = %s", (scanned_id,))
guest = cursor.fetchone()
conn.close()

# -----------------------------
# CHECK-IN LOGIC
# -----------------------------
if not guest:
    print("❌ Guest not found in the database.")
else:
    name = guest["name"]
    if guest["checked_in"]:
        print(f"⚠️ {name} already checked-in.")
    else:
        print(f"✅ {name} Access granted. (Not yet checked-in)")
