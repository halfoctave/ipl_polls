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
    
    all_files = sorted([f for f in os.listdir(directory) if f.endswith('.csv')])  # Sort files to ensure correct match order
    user_data = defaultdict(lambda: {'Total_Points': 0})  # Default structure with total points
    
    match_number = 1
    all_usernames = set()

    for file in all_files:
        file_path = os.path.join(directory, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            match_users = set()
            
            for row in reader:
                username = row['Username']
                display_name = row['Display Name']
                team_short = row.get('Team Voted Short', '---')  # Default to '---' if no vote
                team_full = row.get('Team Voted', '---')  # Default to '---' if no vote
                points = row.get('Points', '0')
                
                try:
                    points = int(points)
                except ValueError:
                    points = 0
                
                user_data[username]['Display Name'] = display_name
                user_data[username][f'Match_{match_number}_Team_Short'] = team_short
                user_data[username][f'Match_{match_number}_Points'] = points
                user_data[username][f'Match_{match_number}_Team'] = team_full
                
                user_data[username]['Total_Points'] += points
                match_users.add(username)
            
            all_usernames.update(match_users)

            # Fill missing users with defaults for this match
            for username in all_usernames:
                if f'Match_{match_number}_Team_Short' not in user_data[username]:
                    user_data[username][f'Match_{match_number}_Team_Short'] = '---'
                    user_data[username][f'Match_{match_number}_Points'] = 0
                    user_data[username][f'Match_{match_number}_Team'] = '---'
        
        match_number += 1
    
    # Generate fieldnames dynamically
    fieldnames = ['Username', 'Display Name'] + \
                 sum([[f'Match_{i}_Team_Short', f'Match_{i}_Points'] for i in range(1, match_number)], []) + \
                 [f'Match_{i}_Team' for i in range(1, match_number)] + ['Total_Points']
    
    # Ensure data is sorted by username
    if not is_sorted(user_data):
        user_data = dict(sorted(user_data.items()))

    # Write the combined CSV
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