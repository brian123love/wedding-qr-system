import pandas as pd
import qrcode
import uuid
import os
import re

RENDER_URL = "https://wedding-qr-system-3.onrender.com"

# Create folder for QR codes 
os.makedirs("qr_codes", exist_ok=True)

# Load CSV
if os.path.exists("guests_with_ids.csv"):
    guests = pd.read_csv("guests_with_ids.csv")
else: 
    guests = pd.read_csv("guests.csv")

# Make sure unique_id column exists
if "unique_id" not in guests.columns:
    guests["unique_id"] = None

if "checked_in" not in guests.columns:
    guests["checked_in"] = "NO"

print("Select mode:")
print("1-Generate QR for ALL guests")
print("2-Add NEW guest and generate only their QR")

choice = input("ENTER 1 or 2: ").strip()

# =========================
# MODE 1: GENERATE ALL
# =========================
if choice == "1":
    for index, row in guests.iterrows():
        # Only generate new UUID if missing
        if pd.isna(row["unique_id"]) or row["unique_id"] == "":
            guests.at[index, "unique_id"] = str(uuid.uuid4())

        name = row["name"]
        uid = guests.at[index, "unique_id"]

        # QR data
        data = f"{RENDER_URL}/checkin?id={uid}"
        img = qrcode.make(data)

        # Sanitize filename
        safe_name = re.sub(r"[^\w]", "_", name).strip()
        filename = f"qr_codes/{safe_name}.png"

        # Save QR image
        img.save(filename)
        print(f"✅ QR generated for {name}")

    # Save updated guest list with unique IDs 
    guests.to_csv("guests_with_ids.csv", index=False)
    print("✅ All QR codes generated successfully!")


# =========================
# MODE 2: ADD SINGLE GUEST
# =========================
elif choice == "2":
    new_guest_name = input("Enter full name of new guest: ").strip()

    new_guest_email = input("Enter guest email: ").strip()
    
    if new_guest_name.lower() in guests["name"].str.lower().values:
        print("⚠️ Guest already exists.") 
    else:
        new_uid = str(uuid.uuid4())
        new_row = {
            "name": new_guest_name,
            "email": new_guest_email,
            "unique_id": new_uid,
            "checked_in": "NO"
        }
        guests = pd.concat([guests, pd.DataFrame([new_row])], ignore_index=True)

        # Generate QR
        data = f"{RENDER_URL}/checkin?id={new_uid}"
        img = qrcode.make(data)

        safe_name = re.sub(r"[^\w]", "_", new_guest_name).strip()
        filename = f"qr_codes/{safe_name}.png"
        img.save(filename)

        # Save updated CSV
        guests.to_csv("guests_with_ids.csv", index=False)
        print(f"✅ QR generated for {new_guest_name}")

else:
    print("❌ Invalid choice.")
