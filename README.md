# IPL Polls Leaderboard Generator

The **IPL Polls Leaderboard Generator** is a Python-based toolset for processing Indian Premier League (IPL) poll data and generating leaderboards. It processes match and playoff prediction polls, calculates points based on user votes, and produces detailed, weekly, and overall leaderboards in CSV format. The project is designed for IPL organizers, fans, or communities running prediction polls to track user performance across matches and seasons.

## Features

- **Match Poll Processing**: Converts per-match JSON polls into CSVs with user votes and points.
- **Playoff Poll Processing**: Evaluates playoff team predictions, awarding points for correct picks.
- **Weekly Leaderboards**: Combines match results for a given week into a single CSV with user rankings.
- **Overall Leaderboards**: Aggregates points across weeks, optionally including playoff points, with rank movement tracking.
- **Detailed Leaderboards**: Provides per-match team selections and points for each user.
- **Excel Compatibility**: Outputs CSVs with UTF-8-SIG encoding to ensure special characters (e.g., accented names, emojis) display correctly in Microsoft Excel.
- **Ranking System**: Supports `Dense Rank` (no skips, e.g., 1, 2, 2, 3) and `Standard Rank` (with skips, e.g., 1, 2, 2, 4).

## Repository Links

- GitHub: https://github.com/halfoctave/ipl_polls
- GitLab: https://gitlab.com/halfoctave/ipl_polls

## Project Structure

The project uses a specific folder structure to organize input data, scripts, and outputs:

```
ipl_polls/
├── data/
│   ├── raw/
│   │   ├── week1/
│   │   │   ├── 1-MIvsRR.json
│   │   │   ├── 2-CSKvsKKR.json
│   │   │   └── ...
│   │   ├── week2/
│   │   ├── week3/
│   │   └── playoff.json
│   ├── processed/
│   │   ├── week1/
│   │   │   ├── 1-MIvsRR.csv
│   │   │   ├── 2-CSKvsKKR.csv
│   │   │   └── ...
│   │   ├── week2/
│   │   ├── week3/
│   │   └── playoff_prediction.csv
├── results/
│   ├── weekly/
│   │   ├── week1.csv
│   │   ├── week2.csv
│   │   └── week3.csv
│   ├── overall/
│   │   ├── overall_week1.csv
│   │   ├── overall_week2.csv
│   │   └── overall_week3.csv
│   ├── detailed/
│   │   ├── detailed_week1.csv
│   │   ├── detailed_week2.csv
│   │   └── detailed_week3.csv
│   ├── ranks/
│   │   ├── ranks_overall_week1.json
│   │   ├── ranks_overall_week2.json
│   │   └── ranks_overall_week3.json
├── ipl_polls/
│   ├── 1-generate_match_results.py
│   ├── 2-generate_weekly_leaderboard.py
│   ├── 3-generate_overall_leaderboard.py
│   ├── 4-generate_detailed_leaderboard.py
│   ├── 5-generate_playoff_results.py
└── README.md
```

- **data/raw/**: Contains input JSON poll files (match polls in `weekN/` subfolders, playoff poll as `playoff.json`).
- **data/processed/**: Stores processed CSV outputs (match CSVs in `weekN/`, playoff CSV as `playoff_prediction.csv`).
- **results/**: Holds leaderboard CSVs (`weekly/`, `overall/`, `detailed/`) and rank JSONs (`ranks/`).
- **ipl_polls/**: Contains Python scripts and a `logs/` folder (optional, for future logging).
- **README.md**: This file.

## Scripts

The project includes five Python scripts, each with a specific role:

1. `1-generate_match_results.py`

   - **Purpose**: Processes per-match JSON poll files for a given week, converting them to CSVs with user votes, team selections, and points.
   - **Input**: JSON files in `data/raw/weekN/` (e.g., `1-MIvsRR.json`).
   - **Output**: CSVs in `data/processed/weekN/` (e.g., `1-MIvsRR.csv`).
   - **Key Features**: Assigns custom points based on the match winner, uses short team names (e.g., `MI`, `RR`).

2. `2-generate_weekly_leaderboard.py`

   - **Purpose**: Combines match CSVs for a week into a single leaderboard CSV, including per-match team selections, points, and rankings.
   - **Input**: CSVs in `data/processed/weekN/`.
   - **Output**: CSV in `results/weekly/weekN.csv`.
   - **Key Features**: Adds `Dense Rank` and `Standard Rank`, handles missing votes with `---`.

3. `3-generate_overall_leaderboard.py`

   - **Purpose**: Aggregates points across weeks (optionally including playoffs) into an overall leaderboard with rank movement.
   - **Input**: CSVs in `results/weekly/`, optionally `data/processed/playoff_prediction.csv`, previous ranks in `results/ranks/`.
   - **Output**: CSV in `results/overall/overall_weekN.csv`, JSON in `results/ranks/ranks_overall_weekN.json`.
   - **Key Features**: Tracks `Dense Rank Movement` and `Standard Rank Movement` (e.g., `↑2`, `↓1`, `—`, `N`).

4. `4-generate_detailed_leaderboard.py`

   - **Purpose**: Creates a detailed leaderboard with per-match team selections and points across all weeks.
   - **Input**: CSVs in `results/weekly/`.
   - **Output**: CSV in `results/detailed/detailed_weekN.csv`.
   - **Key Features**: Lists every match’s team and points for each user, with `Dense Rank` and `Standard Rank`.

5. `5-generate_playoff_results.py`

   - **Purpose**: Processes playoff prediction polls, awarding points for correct team picks.
   - **Input**: JSON in `data/raw/playoff.json`.
   - **Output**: CSV in `data/processed/playoff_prediction.csv`.
   - **Key Features**: Handles multiple votes per user (4 teams), calculates points for correct picks, includes rankings.

## Prerequisites

- **Python**: Version 3.8 or higher.
- **Dependencies**: Standard library modules only (`json`, `csv`, `os`, `collections`).
- **Operating System**: Windows, macOS, or Linux.
- **Tools**: Git for cloning the repository, a text editor (e.g., VS Code) for modifications.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/halfoctave/ipl_polls.git
   # or
   git clone https://gitlab.com/halfoctave/ipl_polls.git
   cd ipl_polls
   ```

2. **Set Up Python Environment**:

   - Ensure Python 3.8+ is installed:

     ```bash
     python --version
     ```

   - No external libraries are required, as the scripts use Python’s standard library.

3. **Prepare Input Data**:

   - Place match poll JSON files in `data/raw/weekN/` (e.g., `data/raw/week3/1-MIvsRR.json`).
   - Place playoff poll JSON in `data/raw/playoff.json`.
   - See Input File Formats for JSON structure.

4. **Create Output Directories** (optional):

   - The scripts automatically create `data/processed/`, `results/weekly/`, `results/overall/`, `results/detailed/`, and `results/ranks/` as needed.

## Usage

Run the scripts in sequence to process polls and generate leaderboards. Update the `WEEK` variable in each script (e.g., `WEEK = "week3"`) to match the target week.

1. **Process Match Polls**:

   ```bash
   cd ipl_polls
   python generate_match_results.py
   ```

   - Processes all JSONs in `data/raw/week3/` into CSVs in `data/processed/week3/`.

2. **Generate Weekly Leaderboard**:

   ```bash
   python generate_weekly_leaderboard.py
   ```

   - Combines CSVs from `data/processed/week3/` into `results/weekly/week3.csv`.

3. **Generate Overall Leaderboard**:

   ```bash
   python generate_overall_leaderboard.py
   ```

   - Aggregates CSVs from `results/weekly/` into `results/overall/overall_week3.csv`.
   - Set `INCLUDE_PLAYOFFS = True` to include `data/processed/playoff_prediction.csv`.

4. **Generate Detailed Leaderboard**:

   ```bash
   python generate_detailed_leaderboard.py
   ```

   - Creates `results/detailed/detailed_week3.csv` from `results/weekly/` CSVs.

5. **Process Playoff Poll**:

   ```bash
   python generate_playoff_results.py
   ```

   - Converts `data/raw/playoff.json` into `data/processed/playoff_prediction.csv`.

### Example Workflow

For IPL week 3:

1. Place JSONs (e.g., `1-MIvsRR.json`, `2-CSKvsKKR.json`) in `data/raw/week3/`.
2. Run `generate_match_results.py` to create CSVs in `data/processed/week3/`.
3. Run `generate_weekly_leaderboard.py` to create `results/weekly/week3.csv`.
4. Run `generate_overall_leaderboard.py` to create `results/overall/overall_week3.csv`.
5. Run `generate_detailed_leaderboard.py` to create `results/detailed/detailed_week3.csv`.
6. Place `playoff.json` in `data/raw/` and run `generate_playoff_results.py` to create `data/processed/playoff_prediction.csv`.

## Input File Formats

### Match Poll JSON (`data/raw/weekN/1-MIvsRR.json`)

```json
{
  "winner": "MI",
  "points": 3.0,
  "answers": [
    {"id": "1", "name": "Mumbai Indians"},
    {"id": "2", "name": "Rajasthan Royals"}
  ],
  "votes": [
    {
      "user": {"id": "u1", "username": "user1", "globalName": "User One"},
      "answerId": "1"
    },
    {
      "user": {"id": "u2", "username": "user2", "globalName": "User Two"},
      "answerId": "2"
    }
  ]
}
```

- `winner`: Short name of the winning team (e.g., `MI`).
- `points`: Points for correct vote (e.g., `3.0`).
- `answers`: List of team options (full names).
- `votes`: List of user votes with `user` details and `answerId`.

### Playoff Poll JSON (`data/raw/playoff.json`)

```json
{
  "messageId": "12345",
  "points": 4.0,
  "answers": [
    {"id": "1", "name": "Chennai Super Kings"},
    {"id": "2", "name": "Kolkata Knight Riders"},
    {"id": "3", "name": "Mumbai Indians"},
    {"id": "4", "name": "Rajasthan Royals"},
    {"id": "5", "name": "Delhi Capitals"}
  ],
  "votes": [
    {
      "user": {"id": "u1", "username": "user1", "globalName": "User One"},
      "answerId": "1"
    },
    {
      "user": {"id": "u1", "username": "user1", "globalName": "User One"},
      "answerId": "2"
    }
  ],
  "playoffteams": ["CSK", "KKR", "MI", "RR"]
}
```

- `points`: Points per correct team prediction (e.g., `4.0`).
- `answers`: List of team options (full names).
- `votes`: List of user votes (each user can vote for 4 teams).
- `playoffteams`: List of 4 correct playoff teams (short names).

### CSV Outputs

- **Match CSV** (`data/processed/week3/1-MIvsRR.csv`):

  ```
  Username,Display Name,Team Voted Short,Team Voted,Points
  user1,User One,MI,Mumbai Indians,3.0
  user2,User Two,RR,Rajasthan Royals,0.0
  ```

- **Playoff CSV** (`data/processed/playoff_prediction.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Predicted Teams,Correct Picks,Points
  1,1,user1,User One,CSK, KKR, MI, RR,CSK, KKR, MI, RR,16.0
  ```

- **Weekly CSV** (`results/weekly/week3.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Match_1_Team_Short,Match_1_Points,...,Total_Points
  1,1,user1,User One,MI,3.0,...,6.0
  ```

- **Overall CSV** (`results/overall/overall_week3.csv`):

  ```
  Dense Rank,Dense Rank Movement,Standard Rank,Standard Rank Movement,Username,Display Name,Week1,Week2,Week3,Total
  1,—,1,—,user1,User One,5.0,4.0,6.0,15.0
  ```

- **Detailed CSV** (`results/detailed/detailed_week3.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Match_1_Team_Short,Match_1_Points,...,Total_Points
  1,1,user1,User One,MI,3.0,...,15.0
  ```

## File Encoding

- **CSV Files**: Written and read with `UTF-8-SIG` encoding to include a Byte Order Mark (BOM) for Excel compatibility, ensuring special characters (e.g., accented names, emojis) display correctly.
- **JSON Files**: Written and read with `UTF-8` encoding (no BOM) to adhere to JSON standards.

## Troubleshooting

- **Error: "Input directory does not exist"**:
  - Ensure `data/raw/weekN/` exists and contains JSON files.
  - Verify `WEEK` variable matches the folder (e.g., `week3`).
- **Error: "Invalid JSON"**:
  - Check JSON files for correct syntax (e.g., missing commas, brackets).
  - Use a JSON validator (e.g., VS Code, online tools).
- **Special Characters Garbled in Excel**:
  - Confirm CSVs are opened in Excel with UTF-8 encoding (File &gt; Open &gt; Text Import Wizard &gt; UTF-8).
  - All CSVs are written with `UTF-8-SIG`, so this should be rare.
- **Missing Output Files**:
  - Ensure input files are present and scripts are run in order (match, weekly, overall, detailed, playoff).
  - Check for errors in the console output.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository on GitHub or GitLab.

2. Create a branch for your changes:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make changes, test thoroughly, and commit:

   ```bash
   git commit -m "Add your feature"
   ```

4. Push to your fork and create a pull request:

   ```bash
   git push origin feature/your-feature
   ```

5. Ensure your code follows Python PEP 8 style guidelines and includes tests if applicable.

Ideas for contributions:

- Add logging to `ipl_polls/logs/` for debugging.
- Support additional poll types (e.g., player performance predictions).
- Enhance error handling or input validation.
- Create a CLI interface for easier script execution.

## Contact

For questions, issues, or suggestions, open an issue on GitHub or GitLab.

Happy IPL polling!