import json
import csv
import os

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
    headers = ['Username', 'Team Voted', 'Vote Timestamp']
    
    # Process each vote
    for vote in data['votes']:
        username = vote['user']['username']
        team_voted = answer_map[vote['answerId']]
        timestamp = vote['createdAt']
        
        csv_rows.append({
            'Username': username,
            'Team Voted': team_voted,
            'Vote Timestamp': timestamp
        })
    
    # Sort rows by timestamp
    csv_rows.sort(key=lambda x: x['Vote Timestamp'])
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"CSV file has been created: {output_file}")

def main():
    # Define paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))  # /IPL/script
    input_dir = os.path.join(script_dir, '..', 'input')      # /IPL/input
    output_dir = os.path.join(script_dir, '..', 'output')    # /IPL/output
    
    # Example: Process a single file named 'poll.json' in input folder
    input_file = os.path.join(input_dir, '0326_RR vs KKR.json')
    output_file = os.path.join(output_dir, 'poll_results.csv')
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return
    
    # Read and process the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    process_poll_to_csv(json_data, output_file)

    # If you have multiple files, you could uncomment and modify this:
    # for filename in os.listdir(input_dir):
    #     if filename.endswith('.json'):
    #         input_file = os.path.join(input_dir, filename)
    #         output_file = os.path.join(output_dir, f"{filename[:-5]}_results.csv")
    #         with open(input_file, 'r') as f:
    #             json_data = json.load(f)
    #         process_poll_to_csv(json_data, output_file)

if __name__ == "__main__":
    main()