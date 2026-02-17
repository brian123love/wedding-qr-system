import pandas as pd
import qrcode
import uuid
import os
import re

RENDER_URL ="https://wedding-qr-system-2.onrender.com"

#Create folder for QR codes 
os.makedirs("qr_codes", exist_ok=True)

if os.path.exists("guests_with_ids.csv"):
   guests= pd.read_csv("guests_with_ids.csv")
else: 
   guests= pd.read_csv("guests.csv")
#Add unique_id to each guest 
guests["unique_id"] =None
guests["checked_in"]="NO"

print("Select mode:")
print("1-Generate QR for ALL guests")
print("2-Add NEW guest and generate only their QR")

choice=input("ENTER 1 or 2:").strip()

   #=========================
   #MODE 1:GENERATE ALL
   #=========================
if choice=="1":
   for index.row in guests.iterrows():
      if pd.isna(row["unique_id"])or row["unique_id"]=="":
         guests.at[index,"unique_id"]=str(uuid.uuid4())

      name=row["name"]
      uid=guests.at[index,"unique_id"]

      #QR data
      data = f"{RENDER_URL}/checkin?id={uid}"
      img = qrcode.make(data)

      #Sanitize filename
      safe_name= re.sub(r"[^\w]","_",name).strip()
      filename=f"qr_codes/{safe_name}.png"

      #Save QR image
      img.save(filename)
      print(f"QR generated for {name}")

      #Save updated guest list with unique IDs 
      guests.to_csv("guests_with_ids.csv",index=False)

      print("✅All QR codes generated successfully!")

  #=========================
  #MODE 2:ADD SINGLE GUEST
  #=========================
elif choice=="2":
     new_guest_name=input("Enter full name of new guest:").strip()
if new_guest_name.lower()in guests["name"].str.lower().values:
    print("⚠️Guest already exist.") 
else:
      new_uid=str(uuid.uuid4())

      new_row={
         "name":new_guest_name,
         "unique_id":new_uid,
         "checked_in":"NO"
      }

      guests=pd.concat([guests,pd.DataFrame([new_row])],ignore_index=True)

      data=f"{RENDER_URL}/checkin?id={new_uid}"
      img=qrcode.make(data)

      safe_name=re.sub(r"[^\w]","_",new_guest_name).strip()
      filename=f"qr_codes/{safe_name}.png"
      img.save(filename)
      guests.to_csv("guests_with_ids.csv",index=False)

    
      print("✅QR genenrated for{new_guest_name}")
      print("Invalid choice.")
