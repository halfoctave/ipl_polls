import json
import csv
import os

# Dictionary to map team names to abbreviations
abbreviations = {
    "Kolkata Knight Riders": "KKR",
    "Rajasthan Royals": "RR",
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
    "Gujarat Titans": "GT"
}

def process_poll_to_csv(json_data, output_file):
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Create a dictionary to map answer IDs to team names
    answer_map = {answer['id']: answer['name'] for answer in data['answers']}
    
    # Prepare CSV data
    csv_rows = []
    headers = ['Username', 'Display Name', 'Team Voted Short', 'Team Voted']
    
    # Process each vote
    for vote in data['votes']:
        username = vote['user']['username']
        displayname = vote['user']['globalName']
        full_team_name = answer_map[vote['answerId']]
        team_voted_short = abbreviations.get(full_team_name, full_team_name)  # Use abbreviation if found, else full name
        # timestamp = vote['createdAt']
        
        csv_rows.append({
            'Username': username,
            'Display Name': displayname,
            'Team Voted Short': team_voted_short,
            'Team Voted': full_team_name
        #    'Vote Timestamp': timestamp
        })
    
    # Sort rows by username
    csv_rows.sort(key=lambda x: x['Username'])
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"CSV file has been created: {output_file}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # /IPL/script
    input_dir = os.path.join(script_dir, '..', 'input')      # /IPL/input
    output_dir = os.path.join(script_dir, '..', 'output')    # /IPL/output

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.csv")
            
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            process_poll_to_csv(json_data, output_file)
    
if __name__ == "__main__":
    main()