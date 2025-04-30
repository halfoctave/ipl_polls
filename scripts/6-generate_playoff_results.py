import json
import csv
import os

# Define short names mapping
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
    - Standard Rank: Shared rank for tied points with skips (1, 2, 2, 4, ...).
    - Dense Rank: Shared rank for tied points without skips (1, 2, 2, 3, ...).
    
    Args:
        leaderboard (list): List of dicts with user data, sorted by points_key descending.
        points_key (str): Key for sorting points (default 'Points').
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

def process_playoff_poll(input_file, output_file):
    """
    Process a playoff prediction poll JSON file and output results to CSV.
    Users predict 4 teams, earning points for each correct prediction.
    
    Args:
        input_file (str): Path to playoff JSON file
        output_file (str): Path to output CSV file
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{input_file}'")
        return

    if not isinstance(data, dict) or 'votes' not in data or 'answers' not in data:
        print(f"Error: JSON missing required keys: 'votes', 'answers'")
        return

    message_id = data.get("messageId", "Unknown")
    points_per_correct = float(data.get("points", 0))
    answers = {answer["id"]: answer["name"] for answer in data["answers"]}
    
    playoff_teams = data.get("qualifiedteams", [])
    if not playoff_teams or len(playoff_teams) != 4:
        print(f"Error: 'playoffteams' must contain exactly 4 teams, got {len(playoff_teams)}")
        return
    playoff_teams_set = set(playoff_teams)

    user_votes = {}
    for vote in data["votes"]:
        user = vote.get("user", {})
        user_id = user.get("id", "Unknown")
        username = user.get("username", "Unknown")
        display_name = user.get("globalName", username)
        answer_id = vote.get("answerId")

        if user_id not in user_votes:
            user_votes[user_id] = {
                "Username": username,
                "Display Name": display_name,
                "Teams": []
            }
        full_team_name = answers.get(answer_id, "Unknown")
        short_team_name = SHORT_NAMES.get(full_team_name, full_team_name)
        user_votes[user_id]["Teams"].append(short_team_name)

    results = []
    for user_id, user_data in user_votes.items():
        predicted_teams = set(user_data["Teams"])
        correct_picks = predicted_teams.intersection(playoff_teams_set)
        points = len(correct_picks) * points_per_correct

        results.append({
            "Username": user_data["Username"],
            "Display Name": user_data["Display Name"],
            "Predicted Teams": ", ".join(sorted(user_data["Teams"])),
            "Correct Picks": ", ".join(sorted(correct_picks)) if correct_picks else "---",
            "Points": points
        })

    results.sort(key=lambda x: (-x["Points"], x["Username"]))
    results = calculate_ranks(results, 'Points')

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    headers = ["Dense Rank", "Standard Rank", "Username", "Display Name", 
               "Predicted Teams", "Correct Picks", "Points"]
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"Playoff results created: {output_file}")
    print(f"Message ID: {message_id}, Playoff teams: {', '.join(playoff_teams)}")
    print(f"Total participants: {len(user_votes)}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "..", "data", "raw", "playoff_predictions.json")
    output_file = os.path.join(base_dir, "..", "data", "processed", "playoff_predictions.csv")
    process_playoff_poll(input_file, output_file)