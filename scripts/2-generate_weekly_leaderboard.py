import os
import csv
from collections import defaultdict

# Set the current week to process (e.g., "week1")
WEEK = "week4"

def calculate_ranks(leaderboard, points_key='Total_Points'):
    """
    Calculate ranks for the leaderboard.
    - Standard Rank: Shared rank for tied points with skips (1, 2, 2, 4, ...).
    - Dense Rank: Shared rank for tied points without skips (1, 2, 2, 3, ...).
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Total_Points').
    Returns:
        list: Updated leaderboard with 'Standard Rank' and 'Dense Rank' added.
    """
    if not leaderboard:
        return leaderboard
    
    result = []
    current_rank = 1
    dense_rank = 1
    prev_points = None
    
    for i, entry in enumerate(leaderboard):
        points = entry[points_key]
        if prev_points is not None and points < prev_points:
            current_rank = i + 1
            dense_rank += 1
        entry['Standard Rank'] = current_rank
        entry['Dense Rank'] = dense_rank
        result.append(entry)
        prev_points = points
    
    return result

def combine_csv_files(input_dir):
    """
    Combine all CSV files for a given week into a single leaderboard CSV, sorted by Total_Points.
    Adds Dense Rank and Standard Rank columns.
    
    Args:
        input_dir (str): Path to the directory containing weekly CSV files
    Returns:
        str: Path to the combined output CSV file
    """
    base_dir = os.path.dirname(__file__)
    result_dir = os.path.abspath(os.path.join(base_dir, "../results/weekly"))
    output_file = os.path.join(result_dir, f"{WEEK}.csv")

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return None

    all_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.csv')])
    if not all_files:
        print(f"Error: No CSV files found in '{input_dir}'")
        return None

    user_data = defaultdict(lambda: {'Total_Points': 0.0})
    match_number = 1
    all_usernames = set()
    required_headers = {'Username', 'Display Name', 'Team Voted Short', 'Points'}

    for file in all_files:
        file_path = os.path.join(input_dir, file)
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                if not required_headers.issubset(reader.fieldnames):
                    print(f"Error: Missing required headers in '{file}'")
                    continue

                match_users = set()
                for row in reader:
                    username = row['Username']
                    display_name = row.get('Display Name', username)
                    team_short = row.get('Team Voted Short', '---')
                    try:
                        points = float(row.get('Points', '0'))
                    except ValueError:
                        points = 0.0

                    user_data[username]['Display Name'] = display_name
                    user_data[username][f'Match_{match_number}_Team_Short'] = team_short
                    user_data[username][f'Match_{match_number}_Points'] = points
                    user_data[username]['Total_Points'] += points
                    match_users.add(username)

                all_usernames.update(match_users)
                for username in all_usernames:
                    if f'Match_{match_number}_Team_Short' not in user_data[username]:
                        user_data[username][f'Match_{match_number}_Team_Short'] = '---'
                        user_data[username][f'Match_{match_number}_Points'] = 0.0

                match_number += 1
        except Exception as e:
            print(f"Error processing '{file_path}': {e}")

    if match_number == 1:
        print(f"Error: No valid CSV files processed for {WEEK}")
        return None

    leaderboard_list = [{'Username': username, **data} for username, data in user_data.items()]
    leaderboard_list.sort(key=lambda x: (-x['Total_Points'], x['Username']))
    leaderboard_list = calculate_ranks(leaderboard_list, 'Total_Points')

    fieldnames = ['Dense Rank', 'Standard Rank', 'Username', 'Display Name'] + \
                 sum([[f'Match_{i}_Team_Short', f'Match_{i}_Points'] for i in range(1, match_number)], []) + \
                 ['Total_Points']

    os.makedirs(result_dir, exist_ok=True)
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard_list)

    print(f"Weekly leaderboard created: {output_file}")
    print(f"Processed {match_number-1} matches, {len(leaderboard_list)} users")
    return output_file

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    input_dir = os.path.abspath(os.path.join(base_dir, "../data/processed", WEEK))
    output_file = combine_csv_files(input_dir)
    if output_file:
        print(f"Weekly leaderboard generation completed for {WEEK}")