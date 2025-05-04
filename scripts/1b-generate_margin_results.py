import json
import csv
import os
import re

# Set the current week to process (e.g., "week1")
WEEK = "week6"

def parse_margin(margin_str):
    """
    Parse the margin string into number and unit (runs, wickets, or Super Over).
    
    Args:
        margin_str (str): Margin string, e.g., "14 runs", "3 wickets", "Super Over"
    Returns:
        tuple: (number, unit) where number is int or None, unit is "runs", "wickets", or "super_over"
    """
    if not margin_str or not isinstance(margin_str, str):
        return None, None
    margin_str = margin_str.lower().strip()
    if margin_str == "super over":
        return None, "super_over"
    match = re.match(r"(\d+)\s*(runs|wickets)", margin_str)
    if not match:
        return None, None
    number = int(match.group(1))
    unit = match.group(2)
    return number, unit

def parse_answer_range(answer_name, margin_unit):
    """
    Parse an answer's name to extract run, wicket, or Super Over options, using the margin unit to determine short name.
    
    Args:
        answer_name (str): Answer name, e.g., "Win by 11-20 runs OR by 9-10 wickets", "Win by Super Over"
        margin_unit (str): "runs", "wickets", or "super_over" from the margin field
    Returns:
        tuple: (run_min, run_max, wicket_min, wicket_max, is_super_over, short_name)
               run_max/wicket_max is None for open-ended or single values
               is_super_over is True if the answer is for Super Over
               short_name is abbreviated form (e.g., "11-20R", "1W", "SO")
    """
    run_min = run_max = wicket_min = wicket_max = None
    is_super_over = False
    short_name = "Unknown"
    
    answer_name_lower = answer_name.lower()
    
    # Match Super Over
    if "super over" in answer_name_lower:
        is_super_over = True
        short_name = "SO"
    
    # Match run ranges: XX-XX runs, XX+ runs, or XX runs
    run_match = re.search(r"(\d+)(?:-(\d+)|[+])?\s*runs?", answer_name_lower)
    # Match wicket ranges: X-X wickets, X+ wickets, X wicket(s)
    wicket_match = re.search(r"(\d+)(?:-(\d+)|[+])?\s*wicket(?:s)?", answer_name_lower)
    
    if run_match:
        run_min = int(run_match.group(1))
        run_max = int(run_match.group(2)) if run_match.group(2) else None
    
    if wicket_match:
        wicket_min = int(wicket_match.group(1))
        wicket_max = int(wicket_match.group(2)) if wicket_match.group(2) else None
    
    # Set short_name based on margin_unit
    if not is_super_over:
        if margin_unit == "runs" and run_min is not None:
            if run_max is not None:
                short_name = f"{run_min}-{run_max}R"
            elif run_match.group(0).endswith("+ runs"):
                short_name = f"{run_min}+R"
            else:
                short_name = f"{run_min}R"
        elif margin_unit == "wickets" and wicket_min is not None:
            if wicket_max is not None:
                short_name = f"{wicket_min}-{wicket_max}W"
            elif wicket_match.group(0).endswith("+ wickets"):
                short_name = f"{wicket_min}+W"
            else:
                short_name = f"{wicket_min}W"
    
    return run_min, run_max, wicket_min, wicket_max, is_super_over, short_name

def find_winning_answer(margin_number, margin_unit, answers):
    """
    Find the answer whose range or option matches the margin.
    
    Args:
        margin_number (int): Margin value, e.g., 14, None for Super Over
        margin_unit (str): "runs", "wickets", or "super_over"
        answers (list): List of answer dicts with 'id', 'name'
    Returns:
        dict: Winning answer dict or None if no match
    """
    for answer in answers:
        run_min, run_max, wicket_min, wicket_max, is_super_over, _ = parse_answer_range(answer['name'], margin_unit)
        
        if margin_unit == "super_over" and is_super_over:
            return answer
        
        if margin_unit == "runs" and run_min is not None:
            if run_max is None:  # Open-ended (e.g., "61+ runs") or single (e.g., "14 runs")
                if margin_number >= run_min:
                    return answer
            elif run_min <= margin_number <= run_max:
                return answer
                
        elif margin_unit == "wickets" and wicket_min is not None:
            if wicket_max is None:  # Open-ended (e.g., "5+ wickets") or single (e.g., "1 wicket")
                if margin_number >= wicket_min:
                    return answer
            elif wicket_min <= margin_number <= wicket_max:
                return answer
    
    return None

def process_poll_to_csv(json_data, output_file):
    """
    Convert a single JSON margin poll file to CSV format, assigning custom points based on margin match.
    
    Args:
        json_data (dict): Parsed JSON content
        output_file (str): Path where the resulting CSV file will be saved
    Raises:
        ValueError: If JSON data is missing required keys
    """
    if not isinstance(json_data, dict):
        raise ValueError("JSON data must be a dictionary")
    
    if "margin" not in json_data or "answers" not in json_data or "votes" not in json_data:
        raise ValueError("JSON missing required keys: 'margin', 'answers', 'votes'")

    # Parse the margin
    margin_number, margin_unit = parse_margin(json_data.get("margin", ""))
    if margin_number is None and margin_unit not in ["super_over"] or \
       margin_number is not None and margin_unit not in ["runs", "wickets"]:
        raise ValueError(f"Invalid margin format: '{json_data.get('margin', '')}'")

    # Get custom points for this match, defaulting to 1
    match_points = float(json_data.get("points", 1))

    # Find the winning answer
    winning_answer = find_winning_answer(margin_number, margin_unit, json_data['answers'])
    winning_answer_id = winning_answer['id'] if winning_answer else None
    
    # Create a mapping of answer IDs to full names and short names
    answer_map = {}
    short_name_map = {}
    for answer in json_data['answers']:
        _, _, _, _, _, short_name = parse_answer_range(answer['name'], margin_unit)
        answer_map[answer['id']] = answer['name']
        short_name_map[answer['id']] = short_name
    
    # Initialize list to store CSV rows
    csv_rows = []
    headers = ['Username', 'Display Name', 'Margin Voted Short', 'Margin Voted', 'Points']

    # Process each vote
    for vote in json_data['votes']:
        user = vote.get('user', {})
        username = user.get('username', 'Unknown')
        display_name = user.get('globalName', username)
        answer_id = vote.get('answerId')
        full_answer_name = answer_map.get(answer_id, "Unknown")
        answer_short_name = short_name_map.get(answer_id, "Unknown")
        points = match_points if answer_id == winning_answer_id else 0

        csv_rows.append({
            'Username': username,
            'Display Name': display_name,
            'Margin Voted Short': answer_short_name,
            'Margin Voted': full_answer_name,
            'Points': points
        })
    
    # Sort rows by username
    csv_rows.sort(key=lambda x: x['Username'])
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Created CSV: {output_file}")

def main():
    """
    Process all JSON margin poll files for the specified week, converting them to CSV files.
    Reads from data/raw/weekX/poll_margin and saves to data/processed/weekX/poll_margin.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, '..', 'data', 'raw', WEEK, 'poll_margin')
    output_dir = os.path.join(script_dir, '..', 'data', 'processed', WEEK, 'poll_margin')

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    if not json_files:
        print(f"Error: No JSON files found in '{input_dir}'")
        return

    for filename in json_files:
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.csv")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            process_poll_to_csv(json_data, output_file)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{input_file}'")
        except ValueError as e:
            print(f"Error processing '{input_file}': {e}")
        except Exception as e:
            print(f"Unexpected error processing '{input_file}': {e}")

    print(f"Processed {len(json_files)} JSON files for {WEEK}")

if __name__ == "__main__":
    main()