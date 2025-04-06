import json
import csv
import os

# Set the current week to process (e.g., "week1")
WEEK = "week2"

# Dictionary mapping full team names to their short abbreviations
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
    """
    Convert a single JSON poll file to CSV format, assigning custom points based on match winner.
    
    Parameters:
        json_data (str or dict): JSON content as a string or pre-parsed dictionary
        output_file (str): Path where the resulting CSV file will be saved
    """
    # Parse JSON string to dictionary if provided as a string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Extract the winning team's abbreviation to determine point allocation
    winning_team = data.get("winner", "")
    # Get custom points for this match from JSON, defaulting to 1 if not specified
    match_points = float(data.get("points", 1))  # Supports decimal values like 2.5

    # Create a mapping of answer IDs to full team names from the poll answers
    answer_map = {answer['id']: answer['name'] for answer in data['answers']}
    
    # Initialize list to store CSV rows
    csv_rows = []
    # Define CSV column headers
    headers = ['Username', 'Display Name', 'Team Voted Short', 'Team Voted', 'Points']

    # Process each vote in the JSON data
    for vote in data['votes']:
        username = vote['user']['username']
        displayname = vote['user']['globalName']
        full_team_name = answer_map[vote['answerId']]
        # Convert full team name to short abbreviation, fallback to full name if not in abbreviations
        team_voted_short = abbreviations.get(full_team_name, full_team_name)
        # Award custom points if the voted team matches the winner, 0 otherwise
        points = match_points if team_voted_short == winning_team else 0

        # Append vote data to CSV rows
        csv_rows.append({
            'Username': username,
            'Display Name': displayname,
            'Team Voted Short': team_voted_short,
            'Team Voted': full_team_name,
            'Points': points
        })
    
    # Sort rows alphabetically by username for consistent output
    csv_rows.sort(key=lambda x: x['Username'])
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the processed data to a CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    # Print confirmation of CSV creation
    print(f"CSV file has been created: {output_file}")

def main():
    """
    Process all JSON poll files for the specified week, converting them to CSV files.
    Reads from the input_json directory and saves to the output_csv directory relative to the script.
    """
    # Determine base paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script location (e.g., ../script)
    input_dir = os.path.join(script_dir, '..', 'input_json', WEEK)  # Input directory (e.g., ../input_json/week1)
    output_dir = os.path.join(script_dir, '..', 'output_csv', WEEK)  # Output directory (e.g., ../output_csv/week1)

    # Iterate through all JSON files in the input_json directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(input_dir, filename)
            # Generate output CSV filename from JSON filename (e.g., poll1.json → poll1.csv)
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.csv")

            # Read JSON file and convert it to CSV
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            process_poll_to_csv(json_data, output_file)

# Run the script if executed directly
if __name__ == "__main__":
    main()