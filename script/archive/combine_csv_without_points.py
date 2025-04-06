import os
import csv
from collections import defaultdict

def is_sorted(data):
    usernames = list(data.keys())
    return usernames == sorted(usernames)

def combine_csv_files(directory, output_file):
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output"))
    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../combined_output.csv"))
    
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    all_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    user_data = defaultdict(dict)
    match_number = 1
    
    for file in all_files:
        file_path = os.path.join(directory, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['Username']
                display_name = row['Display Name']
                team_short = row['Team Voted Short']
                team_full = row['Team Voted']
                
                user_data[username]['Display Name'] = display_name
                user_data[username][f'Match_{match_number}_Team_Short'] = team_short
                user_data[username][f'Match_{match_number}_Team'] = team_full
        
        match_number += 1
    
    fieldnames = ['Username', 'Display Name'] + [f'Match_{i}_Team_Short' for i in range(1, match_number)] + [f'Match_{i}_Team' for i in range(1, match_number)]
    
    if not is_sorted(user_data):
        user_data = dict(sorted(user_data.items()))
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for username, data in user_data.items():
            row = {'Username': username, **data}
            writer.writerow(row)

# Example usage
directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output"))  # CSV files are located in /IPL/output
output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../combined_output.csv"))  # Save in /IPL folder
combine_csv_files(directory_path, output_file)
print(f"Combined CSV file saved as '{output_file}'")