#!/usr/bin/env python3
"""
Script to extract per-game statistics for NFL Quarterbacks using nfl_data_py package.

This script fetches weekly statistics for quarterbacks for the current NFL season
and saves the data to a CSV file.
"""

import nfl_data_py as nfl
import pandas as pd
from datetime import datetime
import argparse


def get_current_nfl_season():
    """
    Determine the current NFL season year.
    NFL season typically runs from September to February.
    """
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # If we're in January or February, the season year is the previous year
    if current_month <= 2:
        return current_year - 1
    else:
        return current_year


def extract_qb_game_stats(season_year=None, output_file='qb_game_stats.csv'):
    """
    Extract per-game statistics for quarterbacks.

    Args:
        season_year (int): NFL season year. If None, uses current season.
        output_file (str): Output CSV file name.

    Returns:
        pd.DataFrame: DataFrame containing QB game statistics
    """
    if season_year is None:
        season_year = get_current_nfl_season()

    print(f"Fetching QB statistics for {season_year} season...")

    # Import weekly data for the specified season
    weekly_data = nfl.import_weekly_data([season_year])

    # Filter for quarterbacks only
    qb_data = weekly_data[weekly_data['position'] == 'QB'].copy()

    # Select relevant QB statistics columns
    qb_columns = [
        'season', 'week', 'game_id', 'player_id', 'player_name', 'player_display_name',
        'position', 'recent_team', 'opponent_team',
        # Passing stats
        'completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions',
        'sacks', 'sack_yards', 'passing_air_yards', 'passing_yards_after_catch',
        'passing_first_downs', 'passing_epa', 'passing_2pt_conversions',
        # Rushing stats
        'carries', 'rushing_yards', 'rushing_tds', 'rushing_first_downs',
        'rushing_epa', 'rushing_2pt_conversions',
        # Fantasy points
        'fantasy_points', 'fantasy_points_ppr'
    ]

    # Filter to only include columns that exist in the dataset
    available_columns = [col for col in qb_columns if col in qb_data.columns]
    qb_data_filtered = qb_data[available_columns]

    # Sort by week and player name
    qb_data_filtered = qb_data_filtered.sort_values(['week', 'player_name'])

    # Save to CSV
    qb_data_filtered.to_csv(output_file, index=False)
    print(f"✓ Successfully extracted {len(qb_data_filtered)} game records")
    print(f"✓ Data saved to: {output_file}")

    # Display summary statistics
    print("\n--- Summary ---")
    print(f"Total QBs: {qb_data_filtered['player_name'].nunique()}")
    print(f"Weeks covered: {qb_data_filtered['week'].min()} - {qb_data_filtered['week'].max()}")
    print(f"Total games: {len(qb_data_filtered)}")

    # Show top 10 QBs by passing yards
    if 'passing_yards' in qb_data_filtered.columns:
        print("\n--- Top 10 QBs by Total Passing Yards ---")
        top_qbs = qb_data_filtered.groupby('player_name')['passing_yards'].sum().sort_values(ascending=False).head(10)
        for idx, (player, yards) in enumerate(top_qbs.items(), 1):
            print(f"{idx}. {player}: {yards:.0f} yards")

    return qb_data_filtered


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description='Extract NFL QB per-game statistics using nfl_data_py'
    )
    parser.add_argument(
        '--season',
        type=int,
        default=None,
        help='NFL season year (default: current season)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='qb_game_stats.csv',
        help='Output CSV file name (default: qb_game_stats.csv)'
    )

    args = parser.parse_args()

    try:
        df = extract_qb_game_stats(season_year=args.season, output_file=args.output)
        print(f"\n✓ Script completed successfully!")
        print(f"  View the data: cat {args.output}")
        print(f"  Or load in Python: pd.read_csv('{args.output}')")
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        raise


if __name__ == '__main__':
    main()
