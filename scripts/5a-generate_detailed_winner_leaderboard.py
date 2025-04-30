import os
import csv
from collections import defaultdict

# Set the current week up to which the leaderboard will be generated (e.g., "week1")
WEEK = "week6"

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

def generate_detailed_leaderboard():
    """
    Generate a detailed leaderboard CSV combining winner poll matches up to the specified week.
    Includes per-match team selections and points.
    
    Returns:
        str: Path to the generated leaderboard CSV file
    """
    try:
        week_num = int(WEEK.replace("week", ""))
    except ValueError:
        print(f"Error: Invalid week string '{WEEK}'")
        return None

    base_dir = os.path.dirname(__file__)
    input_dir = os.path.abspath(os.path.join(base_dir, '../results/weekly/poll_winner'))
    output_dir = os.path.abspath(os.path.join(base_dir, '../results/detailed/poll_winner'))
    output_file = os.path.join(output_dir, f'week{week_num}.csv')

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return None

    csv_files = sorted(f for f in os.listdir(input_dir) if f.startswith("week") and f.endswith(".csv"))
    week_files = [os.path.join(input_dir, f) for f in csv_files if int(f.replace("week", "").replace(".csv", "")) <= week_num]

    if not week_files:
        print(f"Error: No weekly CSV files found up to {WEEK} in '{input_dir}'")
        return None

    combined_data = defaultdict(lambda: {'Display Name': '', 'Matches': {}, 'Total_Points': 0.0})
    current_match_offset = 0

    for file in week_files:
        try:
            with open(file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                sample_row = next(reader, None)
                if not sample_row or 'Total_Points' not in sample_row:
                    print(f"Error: Invalid or empty CSV '{file}'")
                    continue
                match_count = sum(1 for key in sample_row if key.startswith('Match_') and 'Team_Short' in key)
                f.seek(0)
                reader = csv.DictReader(f)

                for row in reader:
                    username = row['Username']
                    user_data = combined_data[username]
                    
                    if not user_data['Display Name'] and row.get('Display Name'):
                        user_data['Display Name'] = row['Display Name']
                    
                    for match_num in range(1, match_count + 1):
                        global_match_num = current_match_offset + match_num
                        short_key = f'Match_{match_num}_Team_Short'
                        points_key = f'Match_{match_num}_Points'
                        
                        if short_key in row and row[short_key] and row[short_key] != '---':
                            try:
                                points = float(row[points_key] or '0')
                            except ValueError:
                                points = 0.0
                            user_data['Matches'][global_match_num] = {
                                'Team_Short': row[short_key],
                                'Points': points
                            }
                    
                    try:
                        user_data['Total_Points'] += float(row['Total_Points'] or '0')
                    except ValueError:
                        user_data['Total_Points'] += 0.0
            
            current_match_offset += match_count
        except Exception as e:
            print(f"Error processing '{file}': {e}")

    if not combined_data:
        print(f"Error: No valid data processed for {WEEK}")
        return None

    max_matches = max((max(data['Matches'].keys(), default=0) for data in combined_data.values()), default=0)
    leaderboard_list = [
        {'Username': username, 'Display Name': data['Display Name'], 
         'Total_Points': data['Total_Points'], 'Matches': data['Matches']}
        for username, data in combined_data.items()
    ]

    leaderboard_list.sort(key=lambda x: (-x['Total_Points'], x['Username']))
    leaderboard_list = calculate_ranks(leaderboard_list, 'Total_Points')

    os.makedirs(output_dir, exist_ok=True)
    headers = ['Dense Rank', 'Standard Rank', 'Username', 'Display Name']
    for i in range(1, max_matches + 1):
        headers.extend([f'Match_{i}_Team_Short', f'Match_{i}_Points'])
    headers.append('Total_Points')

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for entry in leaderboard_list:
            row = {
                'Dense Rank': entry['Dense Rank'],
                'Standard Rank': entry['Standard Rank'],
                'Username': entry['Username'],
                'Display Name': entry['Display Name'],
                'Total_Points': entry['Total_Points']
            }
            for i in range(1, max_matches + 1):
                match = entry['Matches'].get(i, {'Team_Short': '---', 'Points': 0.0})
                row[f'Match_{i}_Team_Short'] = match['Team_Short']
                row[f'Match_{i}_Points'] = match['Points']
            writer.writerow(row)

    print(f"Detailed winner poll leaderboard created: {output_file}")
    print(f"Processed {len(week_files)} weeks, {max_matches} matches, {len(combined_data)} users")
    return output_file

if __name__ == "__main__":
    output_file = generate_detailed_leaderboard()
    if output_file:
        print(f"Detailed winner poll leaderboard generation completed for {WEEK}")