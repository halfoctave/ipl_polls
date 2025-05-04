import csv
import os
import re
from collections import defaultdict

# Set the final week to process (e.g., "week6")
WEEK = "week6"

def get_overall_winner_top_n(file_path, n=3):
    """
    Get the top N winners from the overall winner leaderboard.
    
    Args:
        file_path (str): Path to the overall winner leaderboard CSV
        n (int): Number of top winners to return
    Returns:
        list: List of (username, display_name, total_points) tuples
    """
    winners = []
    if not os.path.exists(file_path):
        print(f"Error: Overall winner leaderboard '{file_path}' does not exist")
        return winners
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['Username']
            display_name = row['Display Name']
            total_points = float(row['Total'])
            winners.append((username, display_name, total_points))
    
    # Sort by total points descending and take top N
    winners.sort(key=lambda x: x[2], reverse=True)
    return winners[:n]

def get_overall_margin_winner(file_path):
    """
    Get the 1st place winner from the overall margin leaderboard.
    
    Args:
        file_path (str): Path to the overall margin leaderboard CSV
    Returns:
        tuple: (username, display_name, total_points) or None
    """
    if not os.path.exists(file_path):
        print(f"Error: Overall margin leaderboard '{file_path}' does not exist")
        return None
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        top_winner = None
        max_points = -1
        for row in reader:
            username = row['Username']
            display_name = row['Display Name']
            total_points = float(row['Total'])
            if total_points > max_points:
                max_points = total_points
                top_winner = (username, display_name, total_points)
    
    return top_winner

def is_washed_out_match(match_path):
    """
    Check if a match is washed out (all participants have Points == 0).
    
    Args:
        match_path (str): Path to the match CSV
    Returns:
        bool: True if all Points are 0, False otherwise
    """
    with open(match_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        points = [float(row['Points']) for row in reader]
        return all(p == 0 for p in points) and points  # Ensure non-empty

def get_winning_streak(base_dir, excluded_users, n=3):
    """
    Find the top N members with the longest winning streaks in winner polls, excluding specified users.
    Non-participation and washed-out matches reset the streak.
    
    Args:
        base_dir (str): Base directory containing weekX/poll_winner folders
        excluded_users (set): Set of usernames to exclude
        n (int): Number of top streak winners to return
    Returns:
        list: List of (username, display_name, streak_length, start_poll, end_poll, start_num) tuples
    """
    streaks = defaultdict(list)  # username -> list of (poll_file, points)
    display_names = {}
    all_polls = []
    
    # Collect all match CSVs in order
    for week in sorted(os.listdir(base_dir)):
        if not week.startswith('week'):
            continue
        week_dir = os.path.join(base_dir, week, 'poll_winner')
        if not os.path.exists(week_dir):
            continue
        match_files = sorted(os.listdir(week_dir), key=lambda x: int(re.match(r'(\d+)-', x).group(1)))
        for match_file in match_files:
            if match_file.endswith('.csv'):
                all_polls.append((week, match_file))
    
    # Process each match
    for week, match_file in all_polls:
        match_path = os.path.join(base_dir, week, 'poll_winner', match_file)
        # Skip washed-out matches
        if is_washed_out_match(match_path):
            continue
        with open(match_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            participants = set()
            for row in reader:
                username = row['Username']
                display_name = row['Display Name']
                points = float(row['Points'])
                display_names[username] = display_name
                participants.add(username)
                streaks[username].append((match_file, points))
            
            # Record non-participation
            for username in streaks:
                if username not in participants:
                    streaks[username].append((match_file, None))
    
    streak_list = []
    
    for username, votes in streaks.items():
        if username in excluded_users:
            continue
        current_streak = 0
        max_user_streak = 0
        start_idx = 0
        best_start_idx = 0
        best_end_idx = 0
        
        for idx, (poll_file, points) in enumerate(votes):
            if points is None:  # Non-participation
                current_streak = 0
            elif points > 0:
                if current_streak == 0:
                    start_idx = idx
                current_streak += 1
                if current_streak > max_user_streak:
                    max_user_streak = current_streak
                    best_start_idx = start_idx
                    best_end_idx = idx
            else:  # Points == 0 (loss)
                current_streak = 0
        
        if max_user_streak > 0:
            start_num = int(re.match(r'(\d+)-', votes[best_start_idx][0]).group(1))
            streak_list.append((
                username,
                display_names[username],
                max_user_streak,
                votes[best_start_idx][0],
                votes[best_end_idx][0],
                start_num  # For sorting ties
            ))
    
    # Sort by streak length (descending) and earliest start match (ascending) for ties
    streak_list.sort(key=lambda x: (-x[2], x[5]))
    return streak_list[:n]

def get_overall_winning_streak(base_dir):
    """
    Find the member with the longest winning streak in winner polls, including all users.
    
    Args:
        base_dir (str): Base directory containing weekX/poll_winner folders
    Returns:
        tuple: (username, display_name, streak_length, start_poll, end_poll, start_num) or None
    """
    return get_winning_streak(base_dir, set(), n=1)[0] if get_winning_streak(base_dir, set(), n=1) else None

def get_losing_streak(base_dir, n=3):
    """
    Find the top N members with the longest losing streaks in winner polls.
    Non-participation and washed-out matches reset the streak.
    
    Args:
        base_dir (str): Base directory containing weekX/poll_winner folders
        n (int): Number of top streak losers to return
    Returns:
        list: List of (username, display_name, streak_length, start_poll, end_poll, start_num) tuples
    """
    streaks = defaultdict(list)  # username -> list of (poll_file, points)
    display_names = {}
    all_polls = []
    
    # Collect all match CSVs in order
    for week in sorted(os.listdir(base_dir)):
        if not week.startswith('week'):
            continue
        week_dir = os.path.join(base_dir, week, 'poll_winner')
        if not os.path.exists(week_dir):
            continue
        match_files = sorted(os.listdir(week_dir), key=lambda x: int(re.match(r'(\d+)-', x).group(1)))
        for match_file in match_files:
            if match_file.endswith('.csv'):
                all_polls.append((week, match_file))
    
    # Process each match
    for week, match_file in all_polls:
        match_path = os.path.join(base_dir, week, 'poll_winner', match_file)
        # Skip washed-out matches
        if is_washed_out_match(match_path):
            continue
        with open(match_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            participants = set()
            for row in reader:
                username = row['Username']
                display_name = row['Display Name']
                points = float(row['Points'])
                display_names[username] = display_name
                participants.add(username)
                streaks[username].append((match_file, points))
            
            # Reset streaks for non-participants
            for username in streaks:
                if username not in participants:
                    streaks[username].append((match_file, None))
    
    streak_list = []
    
    for username, votes in streaks.items():
        current_streak = 0
        max_user_streak = 0
        start_idx = 0
        best_start_idx = 0
        best_end_idx = 0
        
        for idx, (poll_file, points) in enumerate(votes):
            if points is None:  # Non-participation
                current_streak = 0
            elif points == 0:  # Voted but incorrect
                if current_streak == 0:
                    start_idx = idx
                current_streak += 1
                if current_streak > max_user_streak:
                    max_user_streak = current_streak
                    best_start_idx = start_idx
                    best_end_idx = idx
            else:  # Correct vote
                current_streak = 0
        
        if max_user_streak > 0:
            start_num = int(re.match(r'(\d+)-', votes[best_start_idx][0]).group(1))
            streak_list.append((
                username,
                display_names[username],
                max_user_streak,
                votes[best_start_idx][0],
                votes[best_end_idx][0],
                start_num  # For sorting ties
            ))
    
    # Sort by streak length (descending) and earliest start match (ascending) for ties
    streak_list.sort(key=lambda x: (-x[2], x[5]))
    return streak_list[:n]

def get_overall_losing_streak(base_dir):
    """
    Find the member with the longest losing streak in winner polls, including all users.
    
    Args:
        base_dir (str): Base directory containing weekX/poll_winner folders
    Returns:
        tuple: (username, display_name, streak_length, start_poll, end_poll, start_num) or None
    """
    return get_losing_streak(base_dir, n=1)[0] if get_losing_streak(base_dir, n=1) else None

def get_top_csk_voters(base_dir, n=3):
    """
    Find the top N members who voted most for CSK in winner polls, with match details.
    
    Args:
        base_dir (str): Base directory containing weekX/poll_winner folders
        n (int): Number of top voters to return
    Returns:
        list: List of (username, display_name, vote_count, poll_list) tuples
    """
    csk_votes = defaultdict(list)  # username -> list of match_numbers
    display_names = {}
    
    for week in sorted(os.listdir(base_dir)):
        if not week.startswith('week'):
            continue
        week_dir = os.path.join(base_dir, week, 'poll_winner')
        if not os.path.exists(week_dir):
            continue
        for match_file in os.listdir(week_dir):
            if not match_file.endswith('.csv'):
                continue
            match_path = os.path.join(week_dir, match_file)
            with open(match_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    username = row['Username']
                    display_name = row['Display Name']
                    team_voted_short = row['Team Voted Short']
                    if team_voted_short == 'CSK':
                        match_num = re.match(r'(\d+)-', match_file).group(1)
                        csk_votes[username].append(match_num)
                    display_names[username] = display_name
    
    # Sort users by number of CSK votes
    voters = [
        (username, display_names[username], len(votes), votes)
        for username, votes in csk_votes.items()
    ]
    voters.sort(key=lambda x: x[2], reverse=True)
    
    return voters[:n]

def main():
    """
    Generate a report of prize winners based on poll data.
    Outputs results to console and a text file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '..', 'data', 'processed')
    overall_winner_file = os.path.join(script_dir, '..', 'results', 'overall', 'poll_winner', f'{WEEK}.csv')
    overall_margin_file = os.path.join(script_dir, '..', 'results', 'overall', 'poll_margin', f'{WEEK}.csv')
    output_file = os.path.join(script_dir, '..', 'results', 'prize_winners.txt')
    
    # Get top 3 winner poll winners
    winner_top_3 = get_overall_winner_top_n(overall_winner_file, 3)
    winner_usernames = set(username for username, _, _ in winner_top_3)
    
    # Get margin poll winner
    margin_winner = get_overall_margin_winner(overall_margin_file)
    
    # Get top 3 winning streaks (excluding top 3 winners)
    winning_streaks = get_winning_streak(base_dir, winner_usernames, n=3)
    
    # Get overall longest winning streak (including top 3 winners)
    overall_winning_streak = get_overall_winning_streak(base_dir)
    
    # Get top 3 losing streaks
    losing_streaks = get_losing_streak(base_dir, n=3)
    
    # Get overall longest losing streak
    overall_losing_streak = get_overall_losing_streak(base_dir)
    
    # Get top CSK voters
    top_csk_voters = get_top_csk_voters(base_dir, 3)
    
    # Prepare text output
    output_lines = ["Prize Winners:"]
    
    # Add winner poll winners
    for i, (username, display_name, points) in enumerate(winner_top_3, 1):
        prize = f"Predict the Winner - {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd'} Place"
        output_lines.append(f"{prize}:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Total Points: {points}")
        output_lines.append("")
    
    # Add margin poll winner
    if margin_winner:
        username, display_name, points = margin_winner
        output_lines.append("Predict the Winning Margin - 1st Place:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Total Points: {points}")
        output_lines.append("")
    
    # Add winning streaks
    for i, (username, display_name, streak, start_poll, end_poll, _) in enumerate(winning_streaks, 1):
        start_num = int(re.match(r'(\d+)-', start_poll).group(1))
        end_num = int(re.match(r'(\d+)-', end_poll).group(1))
        prize = f"Longest Winning Streak - {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd'}"
        output_lines.append(f"{prize}:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Winning Streak: {streak} matches, Starting from Match #{start_num} to Match #{end_num}")
        output_lines.append("")
    
    # Add overall winning streak
    if overall_winning_streak:
        username, display_name, streak, start_poll, end_poll, _ = overall_winning_streak
        start_num = int(re.match(r'(\d+)-', start_poll).group(1))
        end_num = int(re.match(r'(\d+)-', end_poll).group(1))
        output_lines.append("Overall Longest Winning Streak:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Winning Streak: {streak} matches, Starting from Match #{start_num} to Match #{end_num}")
        output_lines.append("")
    
    # Add losing streaks
    for i, (username, display_name, streak, start_poll, end_poll, _) in enumerate(losing_streaks, 1):
        start_num = int(re.match(r'(\d+)-', start_poll).group(1))
        end_num = int(re.match(r'(\d+)-', end_poll).group(1))
        prize = f"Longest Losing Streak - {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd'}"
        output_lines.append(f"{prize}:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Losing Streak: {streak} matches, Starting from Match #{start_num} to Match #{end_num}")
        output_lines.append("")
    
    # Add overall losing streak
    if overall_losing_streak:
        username, display_name, streak, start_poll, end_poll, _ = overall_losing_streak
        start_num = int(re.match(r'(\d+)-', start_poll).group(1))
        end_num = int(re.match(r'(\d+)-', end_poll).group(1))
        output_lines.append("Overall Longest Losing Streak:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: Losing Streak: {streak} matches, Starting from Match #{start_num} to Match #{end_num}")
        output_lines.append("")
    
    # Add top CSK voters
    for i, (username, display_name, vote_count, matches) in enumerate(top_csk_voters, 1):
        match_details = [f"Match #{match_num}" for match_num in sorted(matches, key=int)]
        details = f"Voted for CSK {vote_count} times: {', '.join(match_details)}"
        prize = f"Top CSK Voter - {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd'}"
        output_lines.append(f"{prize}:")
        output_lines.append(f"  Username: {username}")
        output_lines.append(f"  Display Name: {display_name}")
        output_lines.append(f"  Details: {details}")
        output_lines.append("")
    
    # Write to text file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    # Print results
    print("\nPrize Winners:")
    for line in output_lines:
        print(line)
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()