import csv
import os
from collections import defaultdict

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the directory containing weekly combined CSV files (e.g., ../results/combined_csv)
DIRECTORY = os.path.join(BASE_DIR, '..', 'results', 'combined_csv')

# Set the week up to which files will be processed (e.g., "week1")
WEEK = "week1"

# Extract the numeric week number from the WEEK string (e.g., "week1" → 1)
week_num = int(WEEK.replace("week", ""))

# Get all CSV files in the directory and sort them alphabetically
try:
    csv_files = [f for f in os.listdir(DIRECTORY) if f.startswith("combined_week") and f.endswith(".csv")]
    csv_files.sort()  # Sort to ensure week1 comes before week2, etc.
except FileNotFoundError:
    print(f"Directory not found: {DIRECTORY}")
    print("Please ensure the 'results/combined_csv' directory exists relative to the script location and contains the CSV files")
    exit()

# Filter files to include only those up to the specified week
week_files = []
for file in csv_files:
    file_week_num = int(file.replace("combined_week", "").replace(".csv", ""))
    if file_week_num <= week_num:
        week_files.append(os.path.join(DIRECTORY, file))
    else:
        break  # Stop once we exceed the target week

# Check if any files were found to process
if not week_files:
    print(f"No files found up to {WEEK} in {DIRECTORY}")
    exit()

# Dictionary to store combined user data with default values
combined_data = defaultdict(lambda: {
    'Display Name': '',        # User's display name
    'Matches': {},             # Dictionary of match data (team short name and points as floats)
    'Total_Points': 0.0        # Cumulative points across all matches as float
})

# Process each weekly CSV file with match number offsetting
current_match_offset = 0  # Tracks the starting match number for each week
for file in week_files:
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Determine the number of matches in this file by peeking at the first row
        sample_row = next(reader)
        match_count = sum(1 for key in sample_row if key.startswith('Match_') and 'Team_Short' in key)
        f.seek(0)  # Reset file pointer to start
        
        # Re-create reader after seeking back to start
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username']
            user_data = combined_data[username]
            
            # Set Display Name if not already set, using the first non-empty value encountered
            if not user_data['Display Name'] and row['Display Name']:
                user_data['Display Name'] = row['Display Name']
            
            # Process each match in the file with an offset to sequence across weeks
            for match_num in range(1, match_count + 1):
                global_match_num = current_match_offset + match_num  # Unique match number across weeks
                short_key = f'Match_{match_num}_Team_Short'
                points_key = f'Match_{match_num}_Points'
                
                # Store match data only if a valid team was voted for
                if short_key in row and row[short_key] and row[short_key] != '---':
                    user_data['Matches'][global_match_num] = {
                        'Team_Short': row[short_key],         # Short team name voted
                        'Points': float(row[points_key] or '0'),  # Points for this match as float, default 0.0
                    }
            
            # Add this week's total points to the user's cumulative total as float
            user_data['Total_Points'] += float(row['Total_Points'] or '0')
    
    # Update the offset for the next week's matches
    current_match_offset += match_count

# Determine the maximum number of matches across all processed weeks
max_matches = 0
for matches in combined_data.values():
    if matches['Matches']:  # Check if the user has any match data
        max_matches = max(max_matches, max(matches['Matches'].keys()))

# Prepare the output file path (e.g., ../results/combined_leaderboard/combined_upto_week1.csv)
output_dir = os.path.join(BASE_DIR, '..', 'results', 'combined_leaderboard')
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
output_file = os.path.join(output_dir, f'combined_upto_{WEEK}.csv')

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    # Create CSV header with columns for all matches (short team names only)
    headers = ['Username', 'Display Name']
    for i in range(1, max_matches + 1):
        headers.extend([
            f'Match_{i}_Team_Short',  # Short team name for each match
            f'Match_{i}_Points',      # Points for each match as float
        ])
    headers.append('Total_Points')  # Final column for cumulative points as float
    
    writer = csv.writer(f)
    writer.writerow(headers)
    
    # Sort data by Total_Points (descending) and then by username (ascending) for ties
    sorted_data = sorted(combined_data.items(), key=lambda x: (-x[1]['Total_Points'], x[0]))
    
    # Write sorted data to the CSV
    for username, data in sorted_data:
        row = [username, data['Display Name']]
        
        # Add match data for each position, filling with defaults if missing
        for i in range(1, max_matches + 1):
            match = data['Matches'].get(i, {
                'Team_Short': '---',  # Default for no vote
                'Points': 0.0,        # Default points as float
            })
            row.extend([
                match['Team_Short'],
                match['Points'],
            ])
        
        row.append(data['Total_Points'])  # Append the total points as float
        writer.writerow(row)

# Print confirmation and summary statistics
print(f"CSV files up to {WEEK} have been combined and saved as '{output_file}'")
print(f"Total users: {len(combined_data)}")
print(f"Processed files: {week_files}")
print(f"Total matches processed: {max_matches}")