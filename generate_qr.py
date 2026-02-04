import pandas as pd
import qrcode
import uuid
import os
import re

RENDER_URL ="https://wedding-qr-system-1.onrender.com"

#Read guest from CSV file 
guests= pd.read_csv("guests.csv")

#Create folder for QR codes 
os.makedirs("qr_codes", exist_ok=True)

#Add unique_id to each guest 
guests["unique_id"] =[str(uuid.uuid4()) for _ in range(len(guests))]

guests["checked_in"]="NO"

#Generate QR codes 
for _, row in guests.iterrows():
   name=row['name']
   uid=row['unique_id']

#QR data
   data = f"{RENDER_URL}/checkin?id={uid}"
   img = qrcode.make(data)

#Sanitize filename
   safe_name= re.sub(r'[^\w]','_',name).strip()
   filename=f"qr_codes/{safe_name}.png"

#Save QR image
   img.save(filename)
   print(f"Generated QR for {name}")
    
#Save updated guest list with unique IDs 
guests.to_csv("guests_with_ids.csv",index=False)
    
print("✅QR codes stored on folder 'qr_codes'")
print(f"Total guests:{len(guests)}")
print(f"Done! All QR Codes Generated ")