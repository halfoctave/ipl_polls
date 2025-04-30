# IPL Polls Leaderboard Generator

The **IPL Polls Leaderboard Generator** is a Python-based toolset for processing Indian Premier League (IPL) poll data and generating leaderboards. These scripts are primarily written for a contest held at Indian Console Gamers (ICG) Discord server using the EasyPoll Disord bot. It handles two type of polls i.e. predict the winner and predict the winning margin prediction polls for matches, as well as playoff team predictions. 

## Features

- **Match Poll Processing**: Converts per-match JSON polls into CSVs with user votes and points for both winner and margin predictions.
- **Playoff Poll Processing**: Evaluates playoff team predictions, awarding points for correct picks.
- **Weekly Leaderboards**: Combines match results for a given week into a single CSV with user rankings for winner and margin polls.
- **Overall Leaderboards**: Aggregates points across weeks, optionally including playoff points, with rank movement tracking for winner, margin, and combined polls.
- **Detailed Leaderboards**: Provides per-match team selections and points for each user for winner and margin polls.
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
│   │   │   ├── poll_winner/
│   │   │   │   └── 06-20250326_RRvsKKR.json
│   │   │   │   └── 07-20250327_SRHvsLSG.json
│   │   │   ├── poll_margin/
│   │   │   │   └── 06-20250326_RRvsKKR.json
│   │   │   │   └── 07-20250327_SRHvsLSG.json
│   │   ├── week2/
│   │   ├── week3/
│   │   └── playoff_predictions.json
│   ├── processed/
│   │   ├── week1/
│   │   │   ├── poll_winner/
│   │   │   │   └── 06-20250326_RRvsKKR.csv
│   │   │   │   └── 07-20250327_SRHvsLSG.csv
│   │   │   ├── poll_margin/
│   │   │   │   └── 06-20250326_RRvsKKR.csv
│   │   │   │   └── 07-20250327_SRHvsLSG.csv
│   │   ├── week2/
│   │   ├── week3/
│   │   └── playoff_predictions.csv
├── results/
│   ├── weekly/
│   │   ├── poll_winner/
│   │   │   └── week1.csv
│   │   ├── poll_margin/
│   │   │   └── week1.csv
│   ├── overall/
│   │   ├── poll_winner/
│   │   │   └── week1.csv
│   │   ├── poll_margin/
│   │   │   └── week1.csv
│   │   ├── combined/
│   │   │   └── week1.csv
│   ├── detailed/
│   │   ├── poll_winner/
│   │   │   └── week1.csv
│   │   ├── poll_margin/
│   │   │   └── week1.csv
│   ├── ranks/
│   │   ├── poll_winner/
│   │   │   └── week1.json
│   │   ├── poll_margin/
│   │   │   └── week1.json
│   │   ├── combined/
│   │   │   └── week1.json
├── scripts/
│   ├── 1a-generate_winner_results.py
│   ├── 1b-generate_margin_results.py
│   ├── 2a-generate_weekly_winner_leaderboard.py
│   ├── 2b-generate_weekly_margin_leaderboard.py
│   ├── 3a-generate_overall_winner_leaderboard.py
│   ├── 3b-generate_overall_margin_leaderboard.py
│   ├── 4-generate_overall_leaderboard.py
│   ├── 5a-generate_detailed_winner_leaderboard.py
│   ├── 5b-generate_detailed_margin_leaderboard.py
│   └── 6-generate_playoff_results.py
└── README.md
```

- **data/raw/**: Contains input JSON poll files (match polls in `weekN/poll_winner/` and `weekN/poll_margin/`, playoff poll as `playoff_predictions.json`).
- **data/processed/**: Stores processed CSV outputs (match CSVs in `weekN/poll_winner/` and `weekN/poll_margin/`, playoff CSV as `playoff_predictions.csv`).
- **results/**: Holds leaderboard CSVs (`weekly/`, `overall/`, `detailed/`) and rank JSONs (`ranks/`).
- **scripts/**: Contains Python scripts for processing and generating leaderboards.

## Scripts

The project includes the following Python scripts, each with a specific role:

1. **`1a-generate_winner_results.py`** (Artifact ID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

   - **Purpose**: Processes JSON poll files for winner predictions and generates CSV files with user votes and points.
   - **Input**: JSON files in `data/raw/weekN/poll_winner/` (e.g., `1-MIvsRR.json`).
   - **Output**: CSVs in `data/processed/weekN/poll_winner/` (e.g., `1-MIvsRR.csv`).
   - **Key Features**: Assigns custom points based on the match winner, uses short team names (e.g., `MI`, `RR`).

2. **`1b-generate_margin_results.py`** (Artifact ID: `b2c3d4e5-f678-9012-bcde-f12345678901`)

   - **Purpose**: Processes JSON poll files for margin predictions and generates CSV files with user votes and points.
   - **Input**: JSON files in `data/raw/weekN/poll_margin/` (e.g., `1-MIvsRR.json`).
   - **Output**: CSVs in `data/processed/weekN/poll_margin/` (e.g., `1-MIvsRR.csv`).
   - **Key Features**: Parses margin ranges, assigns points based on the correct margin prediction.

3. **`2a-generate_weekly_winner_leaderboard.py`** (Artifact ID: `c3d4e5f6-7890-1234-cdef-123456789012`)

   - **Purpose**: Combines weekly winner poll CSV files into a single leaderboard CSV, calculating ranks.
   - **Input**: CSVs in `data/processed/weekN/poll_winner/`.
   - **Output**: CSV in `results/weekly/poll_winner/weekN.csv`.
   - **Key Features**: Adds `Dense Rank` and `Standard Rank`, handles missing votes with `---`.

4. **`2b-generate_weekly_margin_leaderboard.py`** (Artifact ID: `d4e5f6c7-8901-2345-def0-234567890123`)

   - **Purpose**: Combines weekly margin poll CSV files into a single leaderboard CSV, calculating ranks.
   - **Input**: CSVs in `data/processed/weekN/poll_margin/`.
   - **Output**: CSV in `results/weekly/poll_margin/weekN.csv`.
   - **Key Features**: Adds `Dense Rank` and `Standard Rank`, handles missing votes with `---`.

5. **`3a-generate_overall_winner_leaderboard.py`** (Artifact ID: `e5f6c7d8-9012-3456-ef01-345678901234`)

   - **Purpose**: Generates an overall leaderboard from weekly winner leaderboards, including ranks and movement.
   - **Input**: CSVs in `results/weekly/poll_winner/`, optionally `data/processed/playoff_predictions.csv`, previous ranks in `results/ranks/poll_winner/`.
   - **Output**: CSV in `results/overall/poll_winner/weekN.csv`, JSON in `results/ranks/poll_winner/weekN.json`.
   - **Key Features**: Tracks `Dense Rank Movement` and `Standard Rank Movement` (e.g., `↑2`, `↓1`, `—`, `N`).

6. **`3b-generate_overall_margin_leaderboard.py`** (Artifact ID: `f6c7d8e9-0123-4567-f012-456789012345`)

   - **Purpose**: Generates an overall leaderboard from weekly margin leaderboards, including ranks and movement.
   - **Input**: CSVs in `results/weekly/poll_margin/`, optionally `data/processed/playoff_predictions.csv`, previous ranks in `results/ranks/poll_margin/`.
   - **Output**: CSV in `results/overall/poll_margin/weekN.csv`, JSON in `results/ranks/poll_margin/weekN.json`.
   - **Key Features**: Tracks `Dense Rank Movement` and `Standard Rank Movement` (e.g., `↑2`, `↓1`, `—`, `N`).

7. **`4-generate_overall_leaderboard.py`** (Artifact ID: `c7d8e9f0-1234-5678-0123-567890123456`)

   - **Purpose**: Generates a combined overall leaderboard from overall winner and margin leaderboards.
   - **Input**: CSVs in `results/overall/poll_winner/` and `results/overall/poll_margin/`.
   - **Output**: CSV in `results/overall/combined/weekN.csv`, JSON in `results/ranks/combined/weekN.json`.
   - **Key Features**: Combines points from winner and margin polls, calculates combined ranks and movement.

8. **`5a-generate_detailed_winner_leaderboard.py`** (Artifact ID: `d8e9f0c1-2345-6789-1234-678901234567`)

   - **Purpose**: Generates a detailed leaderboard for winner polls, including per-match selections.
   - **Input**: CSVs in `results/weekly/poll_winner/`.
   - **Output**: CSV in `results/detailed/poll_winner/weekN.csv`.
   - **Key Features**: Lists every match’s team and points for each user, with `Dense Rank` and `Standard Rank`.

9. **`5b-generate_detailed_margin_leaderboard.py`** (Artifact ID: `e9f0c1d2-3456-7890-2345-789012345678`)

   - **Purpose**: Generates a detailed leaderboard for margin polls, including per-match selections.
   - **Input**: CSVs in `results/weekly/poll_margin/`.
   - **Output**: CSV in `results/detailed/poll_margin/weekN.csv`.
   - **Key Features**: Lists every match’s margin and points for each user, with `Dense Rank` and `Standard Rank`.

10. **`6-generate_playoff_results.py`** (Artifact ID: `f0c1d2e3-4567-8901-3456-890123456789`)

    - **Purpose**: Processes playoff prediction polls and generates a CSV with results and ranks.
    - **Input**: JSON in `data/raw/playoff_predictions.json`.
    - **Output**: CSV in `data/processed/playoff_predictions.csv`.
    - **Key Features**: Handles multiple votes per user (4 teams), calculates points for correct picks, includes rankings.

## Prerequisites

- **Python**: Version 3.8 or higher.
- **Dependencies**: Standard library modules only (`json`, `csv`, `os`, `collections`, `re`).
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

   - Place match poll JSON files in `data/raw/weekN/poll_winner/` and `data/raw/weekN/poll_margin/` (e.g., `data/raw/week3/poll_winner/1-MIvsRR.json`).
   - Place playoff poll JSON in `data/raw/playoff_predictions.json`.
   - See Input File Formats for JSON structure.

4. **Create Output Directories** (optional):

   - The scripts automatically create `data/processed/`, `results/weekly/`, `results/overall/`, `results/detailed/`, and `results/ranks/` as needed.

## Usage

Run the scripts in sequence to process polls and generate leaderboards. Update the `WEEK` variable in each script (e.g., `WEEK = "week3"`) to match the target week.

1. **Process Winner Match Polls**:

   ```bash
   cd scripts
   python 1a-generate_winner_results.py
   ```

   - Processes all JSONs in `data/raw/week3/poll_winner/` into CSVs in `data/processed/week3/poll_winner/`.

2. **Process Margin Match Polls**:

   ```bash
   python 1b-generate_margin_results.py
   ```

   - Processes all JSONs in `data/raw/week3/poll_margin/` into CSVs in `data/processed/week3/poll_margin/`.

3. **Generate Weekly Winner Leaderboard**:

   ```bash
   python 2a-generate_weekly_winner_leaderboard.py
   ```

   - Combines CSVs from `data/processed/week3/poll_winner/` into `results/weekly/poll_winner/week3.csv`.

4. **Generate Weekly Margin Leaderboard**:

   ```bash
   python 2b-generate_weekly_margin_leaderboard.py
   ```

   - Combines CSVs from `data/processed/week3/poll_margin/` into `results/weekly/poll_margin/week3.csv`.

5. **Generate Overall Winner Leaderboard**:

   ```bash
   python 3a-generate_overall_winner_leaderboard.py
   ```

   - Aggregates CSVs from `results/weekly/poll_winner/` into `results/overall/poll_winner/week3.csv`.
   - Set `INCLUDE_PLAYOFFS = True` to include `data/processed/playoff_predictions.csv`.

6. **Generate Overall Margin Leaderboard**:

   ```bash
   python 3b-generate_overall_margin_leaderboard.py
   ```

   - Aggregates CSVs from `results/weekly/poll_margin/` into `results/overall/poll_margin/week3.csv`.
   - Set `INCLUDE_PLAYOFFS = True` to include `data/processed/playoff_predictions.csv`.

7. **Generate Combined Overall Leaderboard**:

   ```bash
   python 4-generate_overall_leaderboard.py
   ```

   - Combines `results/overall/poll_winner/week3.csv` and `results/overall/poll_margin/week3.csv` into `results/overall/combined/week3.csv`.

8. **Generate Detailed Winner Leaderboard**:

   ```bash
   python 5a-generate_detailed_winner_leaderboard.py
   ```

   - Creates `results/detailed/poll_winner/week3.csv` from `results/weekly/poll_winner/`.

9. **Generate Detailed Margin Leaderboard**:

   ```bash
   python 5b-generate_detailed_margin_leaderboard.py
   ```

   - Creates `results/detailed/poll_margin/week3.csv` from `results/weekly/poll_margin/`.

10. **Process Playoff Poll**:

    ```bash
    python 6-generate_playoff_results.py
    ```

    - Converts `data/raw/playoff_predictions.json` into `data/processed/playoff_predictions.csv`.

### Example Workflow

For IPL week 3:

1. Place winner and margin JSONs (e.g., `1-MIvsRR.json`) in `data/raw/week3/poll_winner/` and `data/raw/week3/poll_margin/`.
2. Run `1a-generate_winner_results.py` and `1b-generate_margin_results.py` to create CSVs in `data/processed/week3/poll_winner/` and `data/processed/week3/poll_margin/`.
3. Run `2a-generate_weekly_winner_leaderboard.py` and `2b-generate_weekly_margin_leaderboard.py` to create `results/weekly/poll_winner/week3.csv` and `results/weekly/poll_margin/week3.csv`.
4. Run `3a-generate_overall_winner_leaderboard.py` and `3b-generate_overall_margin_leaderboard.py` to create `results/overall/poll_winner/week3.csv` and `results/overall/poll_margin/week3.csv`.
5. Run `4-generate_overall_leaderboard.py` to create `results/overall/combined/week3.csv`.
6. Run `5a-generate_detailed_winner_leaderboard.py` and `5b-generate_detailed_margin_leaderboard.py` to create `results/detailed/poll_winner/week3.csv` and `results/detailed/poll_margin/week3.csv`.
7. Place `playoff_predictions.json` in `data/raw/` and run `6-generate_playoff_results.py` to create `data/processed/playoff_predictions.csv`.

## Input File Formats

### Winner Match Poll JSON (`data/raw/weekN/poll_winner/1-MIvsRR.json`)

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

### Margin Match Poll JSON (`data/raw/weekN/poll_margin/1-MIvsRR.json`)

```json
{
  "margin": "14 runs",
  "points": 5.0,
  "answers": [
    {"id": "1", "name": "Win by 1-10 runs OR by 7-8 wickets"},
    {"id": "2", "name": "Win by 11-20 runs OR by 9-10 wickets"}
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

- `margin`: Match margin (e.g., `"14 runs"`, `"3 wickets"`).
- `points`: Points for correct margin prediction (e.g., `5.0`).
- `answers`: List of margin options (full descriptions).
- `votes`: List of user votes with `user` details and `answerId`.

### Playoff Poll JSON (`data/raw/playoff_predictions.json`)

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
  "qualifiedteams": ["RCB", "DC", "GT", "PBKS"]
}
```

- `points`: Points per correct team prediction (e.g., `4.0`).
- `answers`: List of team options (full names).
- `votes`: List of user votes (each user can vote for 4 teams).
- `qualifiedteams`: List of 4 correct playoff teams (short names).

### CSV Outputs

- **Winner Match CSV** (`data/processed/week3/poll_winner/1-MIvsRR.csv`):

  ```
  Username,Display Name,Team Voted Short,Team Voted,Points
  user1,User One,MI,Mumbai Indians,3.0
  user2,User Two,RR,Rajasthan Royals,0.0
  ```

- **Margin Match CSV** (`data/processed/week3/poll_margin/1-MIvsRR.csv`):

  ```
  Username,Display Name,Margin Voted Short,Margin Voted,Points
  user1,User One,1-10R,Win by 1-10 runs OR by 7-8 wickets,0.0
  user2,User Two,11-20R,Win by 11-20 runs OR by 9-10 wickets,5.0
  ```

- **Playoff CSV** (`data/processed/playoff_predictions.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Predicted Teams,Correct Picks,Points
  1,1,user1,User One,CSK, KKR, MI, RR,CSK, KKR, MI, RR,16.0
  ```

- **Weekly Winner CSV** (`results/weekly/poll_winner/week3.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Match_1_Team_Short,Match_1_Points,...,Total_Points
  1,1,user1,User One,MI,3.0,...,6.0
  ```

- **Overall Winner CSV** (`results/overall/poll_winner/week3.csv`):

  ```
  Dense Rank,Dense Rank Movement,Standard Rank,Standard Rank Movement,Username,Display Name,Week1,Week2,Week3,Total
  1,—,1,—,user1,User One,5.0,4.0,6.0,15.0
  ```

- **Detailed Winner CSV** (`results/detailed/poll_winner/week3.csv`):

  ```
  Dense Rank,Standard Rank,Username,Display Name,Match_1_Team_Short,Match_1_Points,...,Total_Points
  1,1,user1,User One,MI,3.0,...,15.0
  ```

## File Encoding

- **CSV Files**: Written and read with `UTF-8-SIG` encoding to include a Byte Order Mark (BOM) for Excel compatibility, ensuring special characters (e.g., accented names, emojis) display correctly.
- **JSON Files**: Written and read with `UTF-8` encoding (no BOM) to adhere to JSON standards.

## Troubleshooting

- **Error: "Input directory does not exist"**:
  - Ensure `data/raw/weekN/poll_winner/` and `data/raw/weekN/poll_margin/` exist and contain JSON files.
  - Verify `WEEK` variable matches the folder (e.g., `week3`).
- **Error: "Invalid JSON"**:
  - Check JSON files for correct syntax (e.g., missing commas, brackets).
  - Use a JSON validator (e.g., VS Code, online tools).
- **Special Characters Garbled in Excel**:
  - Confirm CSVs are opened in Excel with UTF-8 encoding (File > Open > Text Import Wizard > UTF-8).
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
- Add logging to `scripts/logs/` for debugging.
- Support additional poll types (e.g., player performance predictions).
- Enhance error handling or input validation.
- Create a CLI interface for easier script execution.

## Contact

For questions, issues, or suggestions, open an issue on GitHub or GitLab.

Happy IPL polling!