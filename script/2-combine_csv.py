import os
import csv
from collections import defaultdict

# Set the current week to process (e.g., "week1")
WEEK = "week1"

def combine_csv_files(directory, _):
    """
    Combine all CSV files for a given week into a single CSV, sorted by Total_Points.
    Only short team names are included; points are processed as floats to support custom values.
    
    Parameters:
        directory (str): Path to the directory containing weekly CSV files (e.g., ../output_csv/week1)
        _ (None): Unused parameter for compatibility (can be ignored)
    Returns:
        str: Path to the combined output CSV file
    """
    # Get base directory of this script
    base_dir = os.path.dirname(__file__)
    
    # Construct the input and output directories
    directory = os.path.abspath(os.path.join(base_dir, "../output_csv", WEEK))  # Input: e.g., ../output_csv/week1
    result_dir = os.path.abspath(os.path.join(base_dir, "../results/combined_csv"))  # Output directory: e.g., ../results/combined_csv
    output_file = os.path.join(result_dir, f"combined_{WEEK}.csv")          # Output file: e.g., ../results/combined_csv/combined_week1.csv

    # Check if the input directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # Get all CSV files in the directory and sort them alphabetically
    all_files = sorted([f for f in os.listdir(directory) if f.endswith('.csv')])

    # Dictionary to store user data with default Total_Points of 0.0 (float)
    user_data = defaultdict(lambda: {'Total_Points': 0.0})

    match_number = 1  # Track the current match number
    all_usernames = set()  # Set to keep track of all unique usernames

    # Process each CSV file (each representing a match)
    for file in all_files:
        file_path = os.path.join(directory, file)
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            match_users = set()  # Track users who participated in this match

            # Process each row in the CSV
            for row in reader:
                username = row['Username']
                display_name = row['Display Name']
                team_short = row.get('Team Voted Short', '---')  # Short team name, default '---' if missing
                # Commented out: Full team name processing
                # team_full = row.get('Team Voted', '---')       # Full team name, default '---' if missing
                points = row.get('Points', '0')                  # Points earned, default '0' if missing

                # Convert points to float to handle custom values (e.g., 2.5), default to 0.0 if conversion fails
                try:
                    points = float(points)
                except ValueError:
                    points = 0.0

                # Update user data with match-specific info (short team names only)
                user_data[username]['Display Name'] = display_name
                user_data[username][f'Match_{match_number}_Team_Short'] = team_short
                user_data[username][f'Match_{match_number}_Points'] = points
                # Commented out: Storing full team name
                # user_data[username][f'Match_{match_number}_Team'] = team_full

                # Accumulate total points for the user as a float
                user_data[username]['Total_Points'] += points
                match_users.add(username)

            # Update the set of all usernames seen so far
            all_usernames.update(match_users)

            # Fill in default values for users who didn’t participate in this match
            for username in all_usernames:
                if f'Match_{match_number}_Team_Short' not in user_data[username]:
                    user_data[username][f'Match_{match_number}_Team_Short'] = '---'
                    user_data[username][f'Match_{match_number}_Points'] = 0.0  # Use float default
                    # Commented out: Default full team name
                    # user_data[username][f'Match_{match_number}_Team'] = '---'

        match_number += 1  # Increment match number for the next file

    # Dynamically generate column headers for all matches (short team names only)
    fieldnames = ['Username', 'Display Name'] + \
                 sum([[f'Match_{i}_Team_Short', f'Match_{i}_Points'] for i in range(1, match_number)], []) + \
                 ['Total_Points']  # Total_Points follows the match columns

    # Convert defaultdict to regular dict and sort by Total_Points in descending order
    user_data = dict(
        sorted(user_data.items(), key=lambda item: item[1]['Total_Points'], reverse=True)
    )

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the combined data to the output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write each user's data as a row
        for username, data in user_data.items():
            row = {'Username': username, **data}
            writer.writerow(row)

    print("Combined CSV file written successfully.")
    return output_file  # Return the path to the created file

# === Run the script ===
if __name__ == "__main__":
    # Construct the input directory path relative to the script: ../output_csv/weekX
    directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output_csv", WEEK))
    
    # Combine CSV files and get the output file path
    final_output = combine_csv_files(directory_path, None)

    # Print the location of the saved file
    print(f"Combined CSV file saved as '{final_output}'")