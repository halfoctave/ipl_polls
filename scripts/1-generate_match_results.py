import json
import csv
import os

# Set the current week to process (e.g., "week1")
WEEK = "week3"

# Dictionary mapping full team names to their short abbreviations
SHORT_NAMES = {
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
    
    Args:
        json_data (dict): Parsed JSON content
        output_file (str): Path where the resulting CSV file will be saved
    Raises:
        ValueError: If JSON data is missing required keys
    """
    if not isinstance(json_data, dict):
        raise ValueError("JSON data must be a dictionary")
    
    if "winner" not in json_data or "answers" not in json_data or "votes" not in json_data:
        raise ValueError("JSON missing required keys: 'winner', 'answers', 'votes'")

    # Extract the winning team's abbreviation
    winning_team = json_data.get("winner", "")
    # Get custom points for this match, defaulting to 1
    match_points = float(json_data.get("points", 1))

    # Create a mapping of answer IDs to full team names
    answer_map = {answer['id']: answer['name'] for answer in json_data['answers']}
    
    # Initialize list to store CSV rows
    csv_rows = []
    headers = ['Username', 'Display Name', 'Team Voted Short', 'Team Voted', 'Points']

    # Process each vote
    for vote in json_data['votes']:
        user = vote.get('user', {})
        username = user.get('username', 'Unknown')
        display_name = user.get('globalName', username)
        full_team_name = answer_map.get(vote.get('answerId'), "Unknown")
        team_voted_short = SHORT_NAMES.get(full_team_name, full_team_name)
        points = match_points if team_voted_short == winning_team else 0

        csv_rows.append({
            'Username': username,
            'Display Name': display_name,
            'Team Voted Short': team_voted_short,
            'Team Voted': full_team_name,
            'Points': points
        })
    
    # Sort rows by username
    csv_rows.sort(key=lambda x: x['Username'])
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Created CSV: {output_file}")

def main():
    """
    Process all JSON poll files for the specified week, converting them to CSV files.
    Reads from data/raw/weekX and saves to data/processed/weekX.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, '..', 'data', 'raw', WEEK)
    output_dir = os.path.join(script_dir, '..', 'data', 'processed', WEEK)

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    if not json_files:
        print(f"Error: No JSON files found in '{input_dir}'")
        return

    for filename in json_files:
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.csv")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            process_poll_to_csv(json_data, output_file)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{input_file}'")
        except ValueError as e:
            print(f"Error processing '{input_file}': {e}")
        except Exception as e:
            print(f"Unexpected error processing '{input_file}': {e}")

    print(f"Processed {len(json_files)} JSON files for {WEEK}")

if __name__ == "__main__":
    main()