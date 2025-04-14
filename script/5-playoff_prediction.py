import json
import csv
import os

# Define short names mapping based on the provided JSON
SHORT_NAMES = {
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Kolkata Knight Riders": "KKR",
    "Lucknow Super Giants": "LSG",
    "Mumbai Indians": "MI",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH"
}

def calculate_ranks(leaderboard, points_key='Points'):
    """
    Calculate ranks for the leaderboard.
    - Competitive Rank: Shared rank for tied points (1st, 2nd, 2nd, 3rd, ...).
    - Sequential Rank: Counts distinct point totals (1st, 2nd, 2nd, 3rd, ...).
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Points').
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

def process_playoff_poll(input_file, output_file):
    """
    Process a playoff prediction poll JSON file and output results to CSV.
    Users predict 4 teams, earning points for each correct prediction.
    Playoff teams are read from the 'playoffteams' key in the JSON file.

    Parameters:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output CSV file
    """
    # Read the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{input_file}' is not a valid JSON file.")
        return

    # Extract poll details
    message_id = data.get("messageId", "Unknown")
    points_per_correct = float(data.get("points", 0))  # 2.25 points per correct pick
    answers = {answer["id"]: answer["name"] for answer in data["answers"]}
    votes = data.get("votes", [])
    
    # Get playoff teams from JSON
    playoff_teams = data.get("playoffteams", [])
    if not playoff_teams or len(playoff_teams) != 4:
        print("Error: 'playoffteams' key missing, empty, or does not contain exactly 4 teams in the JSON.")
        return
    playoff_teams_set = set(playoff_teams)  # Convert to set for efficient lookup

    # Process votes by user
    user_votes = {}
    for vote in votes:
        user_id = vote["user"]["id"]
        username = vote["user"]["username"]
        display_name = vote["user"].get("globalName", username)
        answer_id = vote["answerId"]

        if user_id not in user_votes:
            user_votes[user_id] = {
                "Username": username,
                "Display Name": display_name,
                "Teams": []
            }
        full_team_name = answers.get(answer_id, "Unknown")
        short_team_name = SHORT_NAMES.get(full_team_name, "Unknown")
        user_votes[user_id]["Teams"].append(short_team_name)

    # Calculate points based on playoff teams
    results = []
    for user_id, user_data in user_votes.items():
        predicted_teams = set(user_data["Teams"])  # User's predictions as a set
        correct_picks = predicted_teams.intersection(playoff_teams_set)  # Matching teams
        points = len(correct_picks) * points_per_correct  # Points as float

        results.append({
            "Username": user_data["Username"],
            "Display Name": user_data["Display Name"],
            "Predicted Teams": ", ".join(sorted(user_data["Teams"])),  # Sorted for consistency
            "Correct Picks": ", ".join(sorted(correct_picks)) if correct_picks else "---",
            "Points": points
        })

    # Sort results by points (descending) and username (ascending) for ties
    results.sort(key=lambda x: (-x["Points"], x["Username"]))

    # Calculate ranks
    results = calculate_ranks(results, 'Points')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write to CSV
    headers = ["Sequential Rank", "Competitive Rank", "Username", "Display Name", "Predicted Teams", "Correct Picks", "Points"]
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"Poll results for message ID {message_id} written to '{output_file}'")
    print(f"Actual playoff teams: {', '.join(playoff_teams)}")
    print(f"Total participants: {len(user_votes)}")

# === Run the script ===
if __name__ == "__main__":
    # Define paths relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "..", "input_json")
    output_dir = os.path.join(base_dir, "..", "output_csv")
    
    # Input JSON file (adjust filename as needed)
    input_file = os.path.join(input_dir, "playoff_poll.json")
    
    # Output CSV file
    output_file = os.path.join(output_dir, "playoff_prediction.csv")

    # Process the poll
    process_playoff_poll(input_file, output_file)