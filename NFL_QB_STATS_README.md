# NFL QB Game Statistics Extractor

This Python script extracts per-game statistics for NFL quarterbacks using the `nfl_data_py` package.

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Current Season)

Extract QB statistics for the current NFL season:

```bash
python extract_qb_stats.py
```

This will create a file `qb_game_stats.csv` with all QB game statistics for the current season.

### Specify a Season

Extract QB statistics for a specific season:

```bash
python extract_qb_stats.py --season 2024
```

### Custom Output File

Specify a custom output file name:

```bash
python extract_qb_stats.py --output my_qb_stats.csv
```

### Combined Options

```bash
python extract_qb_stats.py --season 2023 --output qb_stats_2023.csv
```

## Output

The script generates a CSV file containing the following statistics per game:

### Game Information
- `season`: NFL season year
- `week`: Week number
- `game_id`: Unique game identifier
- `player_id`: Unique player identifier
- `player_name`: Player name
- `player_display_name`: Player display name
- `position`: Position (QB)
- `recent_team`: Player's team
- `opponent_team`: Opponent team

### Passing Statistics
- `completions`: Pass completions
- `attempts`: Pass attempts
- `passing_yards`: Passing yards
- `passing_tds`: Passing touchdowns
- `interceptions`: Interceptions thrown
- `sacks`: Times sacked
- `sack_yards`: Yards lost to sacks
- `passing_air_yards`: Air yards
- `passing_yards_after_catch`: Yards after catch
- `passing_first_downs`: First downs via passing
- `passing_epa`: Expected Points Added (passing)
- `passing_2pt_conversions`: 2-point conversions (passing)

### Rushing Statistics
- `carries`: Rush attempts
- `rushing_yards`: Rushing yards
- `rushing_tds`: Rushing touchdowns
- `rushing_first_downs`: First downs via rushing
- `rushing_epa`: Expected Points Added (rushing)
- `rushing_2pt_conversions`: 2-point conversions (rushing)

### Fantasy Points
- `fantasy_points`: Standard fantasy points
- `fantasy_points_ppr`: PPR fantasy points

## Script Features

1. **Automatic Season Detection**: Automatically determines the current NFL season
2. **Summary Statistics**: Displays top performers and summary stats
3. **Clean Output**: Well-formatted CSV ready for analysis
4. **Error Handling**: Graceful error handling with informative messages

## Example Analysis

After generating the CSV file, you can analyze it using pandas:

```python
import pandas as pd

# Load the data
df = pd.read_csv('qb_game_stats.csv')

# View top QBs by passing yards
top_passers = df.groupby('player_name')['passing_yards'].sum().sort_values(ascending=False).head(10)
print(top_passers)

# Calculate completion percentage
df['completion_pct'] = (df['completions'] / df['attempts'] * 100).round(2)

# View QBs with best completion percentage (min 20 attempts)
qualified_qbs = df[df['attempts'] >= 20]
top_accuracy = qualified_qbs.nlargest(10, 'completion_pct')[['player_name', 'week', 'completion_pct', 'passing_yards']]
print(top_accuracy)
```

## Data Source

This script uses the [nfl_data_py](https://github.com/cooperdff/nfl_data_py) package, which provides NFL data from nflfastR and other sources.
