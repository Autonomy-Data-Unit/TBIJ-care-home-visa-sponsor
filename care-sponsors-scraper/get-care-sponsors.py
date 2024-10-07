import csv
import os
import sys
import pandas as pd

# Check if an argument was provided
if len(sys.argv) > 1:
    sponsor_status = sys.argv[1] # 'current' or 'all'
else:
    print("Please provide a sponsor status.")
    sys.exit(1)

# OLD
# Set before running file, do you want "current" or "all" sponsors
#sponsor_status = "current"



# Check if and org is a skilled care worker sponsor
# @params org_data: dict
def is_a_skilled_care_worker_sponsor(org_data):
    if org_data["Organisation Name"] in care_services and "skilled" in org_data["Route"].lower():
        return True

def is_a_skilled_care_worker_sponso2r(org_data):
    if org_data["Organisation Name"] in care_services and "skilled" in org_data["Route"].lower():
        return True

# *** GET CARE SERVICES ***
# Blank set to group all home care services
care_services = dict()
care_services_data = dict()
# Get the lists of home care services csvs
care_services_csvs = [file for file in os.listdir("data-in/care-data") if file.endswith(".csv")]
# Loop through all the care providers csvs
for csv_file in care_services_csvs:
    filepath = "data-in/care-data/{}".format(csv_file)

    with open(filepath) as infile:
        reader = csv.DictReader(infile)
        care_orgs = [row for row in reader]
    # Add loop through the orgs from the file
    for org in care_orgs:
        # Add wheter the org is "Active" or "Archived"
        if "active" in csv_file:
            org["Status"] = "Active"
        elif "archived" in csv_file:
            org["Status"] = "Archived"
        # Add the service/orgs and providers from the file 
        if org["Name"] not in care_services:
            care_services[org["Name"]] = org["Status"]
        
        # Edited: These lines adds whole care providers, so im removing it
        #if org["Provider name"] not in care_services:
        #    care_services[org["Provider name"]] = org["Status"]
            
        if org["Status"] == "Active":
            care_services_data[org["Name"]] = org

# *** GET SPONSORS ***
# Select sponsor csv depending on status
if sponsor_status == "current":
    sponsors_csv = [file for file in os.listdir("sponsors-lists/csv") if file.endswith(".csv")]
    sponsors_csv.sort()
    sponsors_csv = "sponsors-lists/csv/{}".format(sponsors_csv[-1])
elif sponsor_status == "all":
    sponsors_csv = "data-out/all-skilled-sponsors.csv"
else:
    print("[!] Unexpected sponsor status")
    exit()
    
# Open the sponsors csv
with open("data-out/all-skilled-sponsors.csv") as infile:
    reader = csv.DictReader(infile)
    header = reader.fieldnames
    sponsors_data = [row for row in reader]
# If "current" status keep only sponsors that were on the last list
if sponsor_status == "current":
    sponsors_csv = [file for file in os.listdir("sponsors-lists/csv") if file.endswith(".csv")]
    sponsors_csv.sort()
    last_file_date = sponsors_csv[-1][:10]
    sponsors_data = [org for org in sponsors_data if org["Last appeared"] == last_file_date]



# *** GET CARE SPONSORS ***
# Get care sponsors

sponsor_list = {org["Organisation Name"] : org for org in sponsors_data}

care_sponsors = [org for org in sponsors_data if is_a_skilled_care_worker_sponsor(org)]
# Add the CQC status of each care sponsors
for sponsor in care_sponsors:
    sponsor["Status"] = care_services[sponsor["Organisation Name"]]



care_sponsors_list = []

c = 0
sponsor_list_lower = {s.lower() : sponsor_list[s] for s in sponsor_list}

for care_org_name, care_org_data in care_services_data.items():
    sponsor_data = None
    if care_org_data["Name"] in sponsor_list: sponsor_data = sponsor_list[care_org_data["Name"]]
    elif care_org_data["Provider name"] in sponsor_list: sponsor_data = sponsor_list[care_org_data["Provider name"]]
    elif care_org_data["Name"].lower() in sponsor_list_lower: sponsor_data = sponsor_list_lower[care_org_data["Name"].lower()]
    elif care_org_data["Provider name"].lower() in sponsor_list_lower: sponsor_data = sponsor_list_lower[care_org_data["Provider name"].lower()]
    
    is_sponsor = sponsor_data is not None
    is_skilled = "skilled" in sponsor_data["Route"].lower() if is_sponsor else False
    
    if is_sponsor and is_skilled:
        care_sponsors_list.append({
            'Organisation Name' : care_org_data['Name'],
            'Address 1' : care_org_data['Address 1'],
            'Address 2' : care_org_data['Address 2'],
            'Postcode' : care_org_data['Postcode'],
            'Website' : care_org_data['Website'],
            'CQC_URL' : care_org_data['URL'],
            'Town/City' : care_org_data['Town/City'],
            'County' : care_org_data['County'],
            'Type & Rating' : sponsor_data['Type & Rating'],
            'Route' : sponsor_data['Route'],
            'First appeared' : sponsor_data['First appeared'],
            'Last appeared' : sponsor_data['Last appeared'],
            'Provider name' : care_org_data['Provider name'],
            'Status' : care_org_data['Status'],
        })

print(f"Found {len(care_sponsors_list)} care homes that sponsor visas")

outfile_name = sponsor_status + "-skilled-home-care-sponsors.csv"
outfile_path = "data-out/" + outfile_name

df = pd.DataFrame(data=care_sponsors_list)
df.to_csv(outfile_path, index=False)

"""
# Add the new datafield name to the header
header.append("Status")
# Write the output_file

outfile_name = sponsor_status + "-skilled-home-care-sponsors.csv"
outfile_path = "data-out/" + outfile_name
with open(outfile_path, "w") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=header)
    writer.writeheader()
    writer.writerows(care_sponsors)
"""

print("[*] Task completed!")