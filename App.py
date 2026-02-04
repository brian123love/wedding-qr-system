from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# Load guest list
guests = pd.read_csv("guests_with_ids.csv")
if 'checked_in' not in guests.columns:
    guests['checked_in']='NO'

@app.route('/')
def scanner_page(): 
    return render_template('scanner.html')
    
@app.route('/checkin',methods=['POST'])
def checkin():
    global guests
    data = request.get_json()
    
    if not data:
       return jsonify({"status":"error","message":"No JSON received"}),400 
   
    scanned_id = data.get("id")
    if not scanned_id:
       return jsonify({"status":"error","message":"No ID in JSON"}),400    

    guest = guests[guests["unique_id"] == scanned_id]

    if guest.empty:
        return jsonify({"status": "error","message":"Guest not found"})

    index=guest.index[0]
    if guests.at[index, "checked_in"] == "YES":
        return jsonify({"status": "already", "name":guest.at[index,"name"]})

    # Mark as checked in
    guests.at[index, "checked_in"] = "YES"
    guests.to_csv("guests_with_ids.csv", index=False)

    return jsonify({
        "status": "success",
        "name": guest.at[index, "name"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)