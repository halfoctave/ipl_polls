import os
import csv
import json
from collections import defaultdict

# Set the current week up to which the leaderboard will be generated (e.g., "week1")
WEEK = "week6"

# Flag to control whether playoff points are included
INCLUDE_PLAYOFFS = False

def get_numeric_week(week_name):
    """
    Extract the numeric part from a week name string.
    
    Args:
        week_name (str): Week identifier (e.g., 'week3')
    Returns:
        int: Numeric week number (e.g., 3)
    """
    try:
        return int(week_name.lower().replace("week", "").strip())
    except ValueError:
        raise ValueError(f"Invalid week name: {week_name}")

def calculate_ranks(leaderboard, points_key='Total', prev_ranks=None):
    """
    Calculate ranks and movement for the leaderboard.
    - Standard Rank: Shared rank for tied points with skips (1, 2, 2, 4, ...).
    - Dense Rank: Shared rank for tied points without skips (1, 2, 2, 3, ...).
    - Dense Rank Movement: Change in Dense Rank (↑N, ↓N, —, N).
    - Standard Rank Movement: Change in Standard Rank.
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Total').
        prev_ranks (dict): Previous ranks {username: {"dense": rank, "standard": rank}}.
    Returns:
        list: Updated leaderboard with ranks and movement.
    """
    if not leaderboard:
        return leaderboard
    
    result = []
    current_standard_rank = 1
    dense_rank = 1
    prev_points = None
    
    for i, entry in enumerate(leaderboard):
        points = entry[points_key]
        if prev_points is not None and points < prev_points:
            current_standard_rank = i + 1
            dense_rank += 1
        entry['Standard Rank'] = current_standard_rank
        entry['Dense Rank'] = dense_rank
        
        username = entry['Username']
        if prev_ranks and username in prev_ranks:
            prev_dense_rank = prev_ranks[username].get('dense', 0)
            prev_std_rank = prev_ranks[username].get('standard', 0)
            
            dense_movement = prev_dense_rank - dense_rank
            std_movement = prev_std_rank - current_standard_rank
            
            entry['Dense Rank Movement'] = (
                f'↑{dense_movement}' if dense_movement > 0 else
                f'↓{-dense_movement}' if dense_movement < 0 else
                '—'
            )
            entry['Standard Rank Movement'] = (
                f'↑{std_movement}' if std_movement > 0 else
                f'↓{-std_movement}' if std_movement < 0 else
                '—'
            )
        else:
            entry['Dense Rank Movement'] = 'N'
            entry['Standard Rank Movement'] = 'N'
        result.append(entry)
        prev_points = points
    
    return result

def generate_leaderboard():
    """
    Generate a combined overall leaderboard CSV from overall winner and margin poll CSVs
    for the specified week, including ranks and movement.
    
    Returns:
        str: Path to the generated leaderboard CSV file
    """
    base_dir = os.path.dirname(__file__)
    winner_input_dir = os.path.abspath(os.path.join(base_dir, "../results/overall/poll_winner"))
    margin_input_dir = os.path.abspath(os.path.join(base_dir, "../results/overall/poll_margin"))
    output_dir = os.path.abspath(os.path.join(base_dir, "../results/overall/combined"))
    ranks_dir = os.path.abspath(os.path.join(base_dir, "../results/ranks/combined"))
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ranks_dir, exist_ok=True)

    week_num = get_numeric_week(WEEK)
    output_file = os.path.join(output_dir, f"week{week_num}{'_with_playoffs' if INCLUDE_PLAYOFFS else ''}.csv")
    winner_file = os.path.join(winner_input_dir, f"week{week_num}{'_with_playoffs' if INCLUDE_PLAYOFFS else ''}.csv")
    margin_file = os.path.join(margin_input_dir, f"week{week_num}{'_with_playoffs' if INCLUDE_PLAYOFFS else ''}.csv")

    # Check if at least one input file exists
    winner_exists = os.path.exists(winner_file)
    margin_exists = os.path.exists(margin_file)
    if not (winner_exists or margin_exists):
        print(f"Error: Neither winner file '{winner_file}' nor margin file '{margin_file}' exists")
        return None

    # Load previous week's ranks
    prev_week_num = week_num - 1
    prev_ranks_file = os.path.join(ranks_dir, f"week{prev_week_num}.json")
    prev_ranks = {}
    if os.path.exists(prev_ranks_file):
        try:
            with open(prev_ranks_file, 'r', encoding='utf-8') as f:
                prev_ranks = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in '{prev_ranks_file}', proceeding without previous ranks")

    leaderboard = defaultdict(lambda: {'Display Name': ''})
    week_columns = set()

    # Process winner poll CSV
    if winner_exists:
        try:
            with open(winner_file, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                expected_fields = ['Username', 'Display Name', 'Total']
                if not all(field in reader.fieldnames for field in expected_fields):
                    print(f"Error: Missing required fields in '{winner_file}'")
                else:
                    for row in reader:
                        username = row['Username'].strip()
                        display_name = row.get('Display Name', username).strip()
                        leaderboard[username]['Display Name'] = display_name
                        for week in range(1, week_num + 1):
                            if f"Week{week}" in row:
                                week_key = f"Winner_Week{week}"
                                try:
                                    points = float(row.get(f"Week{week}", '0'))
                                except ValueError:
                                    points = 0.0
                                leaderboard[username][week_key] = points
                                week_columns.add(week_key)
                        if INCLUDE_PLAYOFFS and 'Playoffs' in row:
                            try:
                                points = float(row.get('Playoffs', '0'))
                            except ValueError:
                                points = 0.0
                            leaderboard[username]['Playoffs'] = points
        except Exception as e:
            print(f"Error processing '{winner_file}': {e}")

    # Process margin poll CSV
    if margin_exists:
        try:
            with open(margin_file, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                expected_fields = ['Username', 'Display Name', 'Total']
                if not all(field in reader.fieldnames for field in expected_fields):
                    print(f"Error: Missing required fields in '{margin_file}'")
                else:
                    for row in reader:
                        username = row['Username'].strip()
                        display_name = row.get('Display Name', username).strip()
                        leaderboard[username]['Display Name'] = display_name
                        for week in range(1, week_num + 1):
                            if f"Week{week}" in row:
                                week_key = f"Margin_Week{week}"
                                try:
                                    points = float(row.get(f"Week{week}", '0'))
                                except ValueError:
                                    points = 0.0
                                leaderboard[username][week_key] = points
                                week_columns.add(week_key)
                        if INCLUDE_PLAYOFFS and 'Playoffs' in row:
                            try:
                                points = float(row.get('Playoffs', '0'))
                            except ValueError:
                                points = 0.0
                            leaderboard[username]['Playoffs'] = points
        except Exception as e:
            print(f"Error processing '{margin_file}': {e}")

    if not leaderboard:
        print(f"Error: No valid data processed from '{winner_file}' or '{margin_file}'")
        return None

    leaderboard_list = []
    columns = [f"{poll_type}_Week{week}" for week in range(1, week_num + 1) for poll_type in ['Winner', 'Margin'] if f"{poll_type}_Week{week}" in week_columns] + (['Playoffs'] if INCLUDE_PLAYOFFS else [])
    for username, data in leaderboard.items():
        entry = {'Username': username, 'Display Name': data['Display Name']}
        total = 0.0
        for col in columns:
            points = data.get(col, 0.0)
            entry[col] = points
            total += points
        entry['Total'] = total
        leaderboard_list.append(entry)

    leaderboard_list.sort(key=lambda x: (-x['Total'], x['Username']))
    leaderboard_list = calculate_ranks(leaderboard_list, 'Total', prev_ranks)

    current_ranks = {
        entry['Username']: {
            'dense': entry['Dense Rank'],
            'standard': entry['Standard Rank']
        } for entry in leaderboard_list
    }
    with open(os.path.join(ranks_dir, f"week{week_num}.json"), 'w', encoding='utf-8') as f:
        json.dump(current_ranks, f, ensure_ascii=False)

    fieldnames = ['Dense Rank', 'Dense Rank Movement', 'Standard Rank', 'Standard Rank Movement',
                  'Username', 'Display Name'] + columns + ['Total']

    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard_list)

    combined_files = []
    if winner_exists:
        combined_files.append(winner_file)
    if margin_exists:
        combined_files.append(margin_file)
    
    print(f"Combined overall leaderboard created: {output_file}")
    print(f"Combined files: {' '.join(combined_files)}")
    print(f"Total users: {len(leaderboard_list)}")
    return output_file

if __name__ == "__main__":
    output_file = generate_leaderboard()
    if output_file:
        print(f"Combined overall leaderboard generation completed for {WEEK}")