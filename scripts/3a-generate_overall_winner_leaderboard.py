import os
import csv
import json
from collections import defaultdict

# Set the current week up to which the leaderboard will be generated (e.g., "week1")
WEEK = "week8"

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
    Generate an overall leaderboard CSV from weekly CSVs up to the specified week,
    optionally including playoff points. Includes ranks and movement.
    
    Returns:
        str: Path to the generated leaderboard CSV file
    """
    base_dir = os.path.dirname(__file__)
    input_dir = os.path.abspath(os.path.join(base_dir, "../results/weekly/poll_winner"))
    playoff_input_dir = os.path.abspath(os.path.join(base_dir, "../data/processed"))
    output_dir = os.path.abspath(os.path.join(base_dir, "../results/overall/poll_winner"))
    ranks_dir = os.path.abspath(os.path.join(base_dir, "../results/ranks/poll_winner"))
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(ranks_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"week{WEEK.replace('week', '')}{'_with_playoffs' if INCLUDE_PLAYOFFS else ''}.csv")

    if not os.path.exists(input_dir):
        print(f"Error: Weekly input directory '{input_dir}' does not exist")
        return None

    # Load previous week's ranks
    prev_week_num = get_numeric_week(WEEK) - 1
    prev_ranks_file = os.path.join(ranks_dir, f"week{prev_week_num}.json")
    prev_ranks = {}
    if os.path.exists(prev_ranks_file):
        try:
            with open(prev_ranks_file, 'r', encoding='utf-8') as f:
                prev_ranks = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in '{prev_ranks_file}', proceeding without previous ranks")

    all_files = sorted(f for f in os.listdir(input_dir) if f.startswith("week") and f.endswith(".csv"))
    cutoff_week = get_numeric_week(WEEK)
    selected_files = [f for f in all_files if get_numeric_week(f.split('.')[0]) <= cutoff_week]

    if not selected_files:
        print(f"Error: No weekly CSV files found up to {WEEK} in '{input_dir}'")
        return None

    leaderboard = defaultdict(lambda: {'Display Name': ''})
    week_columns = []

    for file in selected_files:
        week_name = file.split('.')[0]
        week_key = week_name.capitalize()
        week_columns.append(week_key)

        filepath = os.path.join(input_dir, file)
        try:
            with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                if 'Total_Points' not in reader.fieldnames:
                    print(f"Error: Missing 'Total_Points' in '{file}'")
                    continue
                for row in reader:
                    username = row['Username'].strip()
                    display_name = row.get('Display Name', username).strip()
                    try:
                        points = float(row.get('Total_Points', '0'))
                    except ValueError:
                        points = 0.0
                    leaderboard[username]['Display Name'] = display_name
                    leaderboard[username][week_key] = points
        except Exception as e:
            print(f"Error processing '{filepath}': {e}")

    if INCLUDE_PLAYOFFS:
        playoff_file = os.path.join(playoff_input_dir, "playoff_predictions.csv")
        if os.path.exists(playoff_file):
            try:
                with open(playoff_file, newline='', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    if 'Points' not in reader.fieldnames:
                        print(f"Error: Missing 'Points' in '{playoff_file}'")
                    else:
                        for row in reader:
                            username = row['Username'].strip()
                            display_name = row.get('Display Name', username).strip()
                            try:
                                points = float(row.get('Points', '0'))
                            except ValueError:
                                points = 0.0
                            leaderboard[username]['Display Name'] = display_name
                            leaderboard[username]['Playoffs'] = points
            except Exception as e:
                print(f"Error processing '{playoff_file}': {e}")
        else:
            print(f"Warning: Playoff file '{playoff_file}' not found, proceeding without playoff points")

    leaderboard_list = []
    columns = week_columns + (['Playoffs'] if INCLUDE_PLAYOFFS else [])
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
    with open(os.path.join(ranks_dir, f"week{WEEK.replace('week', '')}.json"), 'w', encoding='utf-8') as f:
        json.dump(current_ranks, f, ensure_ascii=False)

    fieldnames = ['Dense Rank', 'Dense Rank Movement', 'Standard Rank', 'Standard Rank Movement',
                  'Username', 'Display Name'] + columns + ['Total']

    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard_list)

    print(f"Overall leaderboard created: {output_file}")
    print(f"Processed weeks: {', '.join(week_columns)}{', Playoffs' if INCLUDE_PLAYOFFS else ''}")
    print(f"Total users: {len(leaderboard_list)}")
    return output_file

if __name__ == "__main__":
    output_file = generate_leaderboard()
    if output_file:
        print(f"Overall leaderboard generation completed for {WEEK}")