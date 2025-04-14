import os
import csv
from collections import defaultdict

# Set the current week up to which the leaderboard will be generated (e.g., "week1")
WEEK = "week3"

# Flag to control whether playoff points are included in the leaderboard
INCLUDE_PLAYOFFS = False  # Set to True to include playoff points, False to exclude

def get_numeric_week(week_name):
    """
    Extract the numeric part from a week name string.
    
    Args:
        week_name (str): Week identifier (e.g., 'week3')
    Returns:
        int: Numeric week number (e.g., 3)
    """
    return int(week_name.lower().replace("week", "").strip())

def calculate_ranks(leaderboard, points_key='Total'):
    """
    Calculate ranks for the leaderboard.
    - Competitive Rank: Shared rank for tied points (1st, 2nd, 2nd, 3rd, ...).
    - Sequential Rank: Counts distinct point totals (1st, 2nd, 2nd, 3rd, ...).
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Total').
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

def generate_leaderboard(_):
    """
    Generate a leaderboard CSV from combined weekly CSV files up to the specified week,
    optionally including playoff points based on the INCLUDE_PLAYOFFS flag.
    Includes points per week, optionally playoff points, total, and Sequential/Competitive Rank columns.
    
    Parameters:
        _ (None): Unused parameter for compatibility (can be ignored)
    Returns:
        str: Path to the generated leaderboard CSV file
    """
    # Get base directory of this script
    base_dir = os.path.dirname(__file__)

    # Define input and output directories relative to script location
    input_dir = os.path.abspath(os.path.join(base_dir, "../results/combined_csv"))  # Input for weeks
    playoff_input_dir = os.path.abspath(os.path.join(base_dir, "../output_csv"))   # Input for playoffs
    output_dir = os.path.abspath(os.path.join(base_dir, "../results/leaderboard")) # Output
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_dir, f"leaderboard_{WEEK}{'_with_playoffs' if INCLUDE_PLAYOFFS else ''}.csv")

    # Get all combined week files from the input directory and sort them
    all_files = sorted(f for f in os.listdir(input_dir) if f.startswith("combined_week") and f.endswith(".csv"))
    cutoff_week = get_numeric_week(WEEK)

    # Filter files to include only those up to the specified week
    selected_files = [
        f for f in all_files
        if get_numeric_week(f.split('_')[1].split('.')[0]) <= cutoff_week
    ]

    # Dictionary to store leaderboard data with default empty Display Name and float-based points
    leaderboard = defaultdict(lambda: {'Display Name': ''})

    # List to track week columns for the CSV header
    week_columns = []

    # Process each selected weekly CSV file
    for file in selected_files:
        week_name = file.split('.')[0].split('_')[-1]    # Extract week part (e.g., 'week1')
        week_key = week_name.capitalize()                # Format as column name (e.g., 'Week1')
        week_columns.append(week_key)                    # Add to list of week columns

        filepath = os.path.join(input_dir, file)
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['Username'].strip()           # Clean username
                display_name = row.get('Display Name', '').strip()  # Clean display name, default to empty
                try:
                    points = float(row.get('Total_Points', '0')) # Convert total points to float, default 0.0
                except ValueError:
                    points = 0.0                            # Use float default for invalid values

                # Update leaderboard with user data
                leaderboard[username]['Display Name'] = display_name
                leaderboard[username][week_key] = points    # Store points for this week as float

    # Process playoff prediction points if flag is True
    if INCLUDE_PLAYOFFS:
        playoff_file = os.path.join(playoff_input_dir, "playoff_prediction.csv")
        if os.path.exists(playoff_file):
            with open(playoff_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    username = row['Username'].strip()           # Clean username
                    display_name = row.get('Display Name', '').strip()  # Clean display name
                    try:
                        points = float(row.get('Points', '0'))   # Convert playoff points to float, default 0.0
                    except ValueError:
                        points = 0.0                         # Use float default for invalid values

                    # Update leaderboard with playoff data
                    leaderboard[username]['Display Name'] = display_name
                    leaderboard[username]['Playoffs'] = points  # Store playoff points as float
        else:
            print(f"Warning: Playoff file '{playoff_file}' not found. Proceeding without playoff points.")

    # Convert to list and calculate totals
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

    # Sort by Total descending, then Username ascending
    leaderboard_list.sort(key=lambda x: (-x['Total'], x['Username']))

    # Calculate ranks
    leaderboard_list = calculate_ranks(leaderboard_list, 'Total')

    # Define CSV header with rank columns, username, display name, week columns, playoffs (if included), and total
    fieldnames = ['Sequential Rank', 'Competitive Rank', 'Username', 'Display Name'] + columns + ['Total']

    # Write the leaderboard to a CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard_list)

    print("Leaderboard CSV file written successfully.")
    return output_file  # Return the path to the generated file

# === Run the script ===
if __name__ == "__main__":
    # Generate the leaderboard and get the output file path
    output_file = generate_leaderboard(None)
    # Print confirmation of where the leaderboard was saved
    if output_file:
        print(f"Leaderboard saved as '{output_file}'")