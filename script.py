import os
import subprocess
from datetime import datetime, timedelta


def get_batman_pattern():
    """
    Returns a 7-row pattern (list of 7 strings) representing the word "BATMAN" in a 7x35 grid.
    Each letter is drawn in a 7x5 block, with a single-column gap between letters.
    """
    B = ["11110", "10001", "10001", "11110", "10001", "10001", "11110"]
    A = ["01110", "10001", "10001", "11111", "10001", "10001", "10001"]
    T = ["11111", "00100", "00100", "00100", "00100", "00100", "00100"]
    M = ["10001", "11011", "10101", "10101", "10001", "10001", "10001"]
    # Reuse the same pattern for the second A
    A2 = A
    N = ["10001", "11001", "10101", "10011", "10001", "10001", "10001"]
    gap = "0"  # a single column of off pixels
    pattern = []
    for i in range(7):
        # Concatenate letter patterns with a gap in between
        row = B[i] + gap + A[i] + gap + T[i] + gap + M[i] + gap + A2[i] + gap + N[i]
        pattern.append(row)
    return pattern


def generate_commit_schedule(pattern, start_date):
    """
    Given a pattern (list of 7 strings, each of equal length) and a start_date (datetime),
    returns a dictionary mapping date strings (YYYY-MM-DD) to commit counts.

    Each "1" in the pattern corresponds to a fixed number of commits (e.g., 5), and "0" corresponds to none.
    The pattern is mapped column by column: each column is one week, each row is a day.
    """
    schedule = {}
    rows = 7
    cols = len(pattern[0])
    commit_value = 5  # number of commits per "on" cell
    for col in range(cols):
        for row in range(rows):
            date = start_date + timedelta(days=col * 7 + row)
            date_str = date.strftime("%Y-%m-%d")
            count = commit_value if pattern[row][col] == "1" else 0
            schedule[date_str] = schedule.get(date_str, 0) + count
    return schedule


def make_commit_for_date(date_str, commit_count):
    """
    Makes 'commit_count' dummy commits for a given date (date_str in YYYY-MM-DD format).
    Uses a fixed commit time and backdates commits via environment variables.
    """
    commit_time = "12:00:00"
    commit_datetime = f"{date_str}T{commit_time}"
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_datetime
    env["GIT_COMMITTER_DATE"] = commit_datetime
    for i in range(commit_count):
        # Append a dummy line to a file to simulate a change
        with open("dummy.txt", "a") as f:
            f.write(f"Commit for {date_str} #{i+1}\n")
        subprocess.run(["git", "add", "dummy.txt"], env=env, check=True)
        commit_message = f"Commit on {date_str} - commit #{i+1}"
        subprocess.run(["git", "commit", "-m", commit_message], env=env, check=True)
        print(f"Committed for {date_str}: commit #{i+1}")


def main():
    pattern = get_batman_pattern()
    # Choose a start date for the pattern.
    # For example, set it to a recent Sunday. Adjust as needed.
    today = datetime.today()
    # Calculate the most recent Sunday (weekday: Monday=0, Sunday=6)
    days_since_sunday = (today.weekday() + 1) % 7
    start_date = today - timedelta(days=days_since_sunday)
    start_date = start_date.replace(hour=12, minute=0, second=0, microsecond=0)
    schedule = generate_commit_schedule(pattern, start_date)
    # Loop over the schedule in sorted order and make commits.
    for date_str in sorted(schedule.keys()):
        commit_count = schedule[date_str]
        if commit_count > 0:
            make_commit_for_date(date_str, commit_count)
    subprocess.run(["git", "push"], check=True)
    print("Pushed all commits to GitHub.")


if __name__ == "__main__":
    main()
