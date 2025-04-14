import os
import csv
from collections import defaultdict

# Set the current week to process (e.g., "week1")
WEEK = "week3"

def calculate_ranks(leaderboard, points_key='Total_Points'):
    """
    Calculate ranks for the leaderboard.
    - Competitive Rank: Shared rank for tied points (1st, 2nd, 2nd, 3rd, ...).
    - Sequential Rank: Counts distinct point totals (1st, 2nd, 2nd, 3rd, ...).
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Total_Points').
    Returns:
        list: Updated leaderboard with 'Competitive Rank' and 'Sequential Rank' added.
    """
    if not leaderboard:
        return leaderboard
    
    result = []
    current_rank = 1
    sequential_rank = 1
    prev_points = None
    
    for i, entry in enumerate(leaderboard):
        points = entry[points_key]
        if prev_points is not None and points < prev_points:
            current_rank = i + 1
            sequential_rank += 1
        entry['Competitive Rank'] = current_rank
        entry['Sequential Rank'] = sequential_rank
        result.append(entry)
        prev_points = points
    
    return result

def combine_csv_files(directory, _):
    """
    Combine all CSV files for a given week into a single CSV, sorted by Total_Points.
    Only short team names are included; points are processed as floats to support custom values.
    Adds Sequential Rank and Competitive Rank columns at the beginning.
    
    Parameters:
        directory (str): Path to the directory containing weekly CSV files (e.g., ../output_csv/week3)
        _ (None): Unused parameter for compatibility (can be ignored)
    Returns:
        str: Path to the combined output CSV file
    """
    # Get base directory of this script
    base_dir = os.path.dirname(__file__)
    
    # Construct the input and output directories
    directory = os.path.abspath(os.path.join(base_dir, "../output_csv", WEEK))  # Input: e.g., ../output_csv/week3
    result_dir = os.path.abspath(os.path.join(base_dir, "../results/combined_csv"))  # Output directory: e.g., ../results/combined_csv
    output_file = os.path.join(result_dir, f"combined_{WEEK}.csv")          # Output file: e.g., ../results/combined_csv/combined_week3.csv

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

        match_number += 1  # Increment match number for the next file

    # Convert defaultdict to list for ranking
    leaderboard_list = []
    for username, data in user_data.items():
        entry = {'Username': username, **data}
        leaderboard_list.append(entry)

    # Sort by Total_Points descending, then Username ascending
    leaderboard_list.sort(key=lambda x: (-x['Total_Points'], x['Username']))

    # Calculate ranks
    leaderboard_list = calculate_ranks(leaderboard_list, 'Total_Points')

    # Dynamically generate column headers for all matches (short team names only)
    fieldnames = ['Sequential Rank', 'Competitive Rank', 'Username', 'Display Name'] + \
                 sum([[f'Match_{i}_Team_Short', f'Match_{i}_Points'] for i in range(1, match_number)], []) + \
                 ['Total_Points']

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the combined data to the output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard_list)

    print("Combined CSV file written successfully.")
    return output_file  # Return the path to the created file

# === Run the script ===
if __name__ == "__main__":
    # Construct the input directory path relative to the script: ../output_csv/weekX
    directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output_csv", WEEK))
    
    # Combine CSV files and get the output file path
    final_output = combine_csv_files(directory_path, None)

    # Print the location of the saved file
    if final_output:
        print(f"Combined CSV file saved as '{final_output}'")