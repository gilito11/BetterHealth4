import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale

# Set locale to English for month names
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# Repository data (public)
REPO_OWNER = 'gilito11'
REPO_NAME = 'BetterHealth4'
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=all&per_page=100'

# GET request to GitHub API
response = requests.get(url)
issues = response.json()

# Helper function to calculate the week of the month
def week_of_month(date):
    # Calculate the week of the month: (day - 1) // 7 + 1
    return (date.day - 1) // 7 + 1

# ------------------------------
# Data grouping dictionaries
# ------------------------------

# For Weekly chart (daily)
open_issues_daily = {}
closed_issues_daily = {}

# Global: Grouped by month; key will be a tuple (year, month)
open_issues_monthly = {}
closed_issues_monthly = {}

# Global: Grouped by week with a custom label ("Week X - Month")
# Use key as a tuple: (year, month, week_of_month)
open_issues_weekly_custom = {}
closed_issues_weekly_custom = {}

# Process each issue
for issue in issues:
    # Process creation date
    created_at_str = issue.get('created_at')
    if created_at_str:
        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        # Accumulate daily data
        open_issues_daily[created_at] = open_issues_daily.get(created_at, 0) + 1
        # Accumulate monthly data (using (year, month) as key)
        month_key = (created_at.year, created_at.month)
        open_issues_monthly[month_key] = open_issues_monthly.get(month_key, 0) + 1
        # Accumulate weekly (custom) data
        key_custom = (created_at.year, created_at.month, week_of_month(created_at))
        open_issues_weekly_custom[key_custom] = open_issues_weekly_custom.get(key_custom, 0) + 1

    # Process closing date
    closed_at_str = issue.get('closed_at')
    if closed_at_str:
        closed_at = datetime.strptime(closed_at_str, '%Y-%m-%dT%H:%M:%SZ').date()
        # Accumulate daily data
        closed_issues_daily[closed_at] = closed_issues_daily.get(closed_at, 0) + 1
        # Accumulate monthly data
        month_key_closed = (closed_at.year, closed_at.month)
        closed_issues_monthly[month_key_closed] = closed_issues_monthly.get(month_key_closed, 0) + 1
        # Accumulate weekly (custom) data
        key_custom_closed = (closed_at.year, closed_at.month, week_of_month(closed_at))
        closed_issues_weekly_custom[key_custom_closed] = closed_issues_weekly_custom.get(key_custom_closed, 0) + 1

# ------------------------------
# 1. Weekly Chart (Current Week)
# ------------------------------
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())  # Monday of current week
days_of_week = [start_week + timedelta(days=i) for i in range(7)]
open_weekly = [open_issues_daily.get(day, 0) for day in days_of_week]
closed_weekly = [closed_issues_daily.get(day, 0) for day in days_of_week]

# For the title, calculate the week number in the month and the month name
start_of_month = today.replace(day=1)
week_number = (today - start_of_month).days // 7 + 1
month_name = today.strftime('%B')

fig1 = plt.figure(figsize=(10, 5))
plt.plot(days_of_week, open_weekly, label='Open Issues', color='blue')
plt.plot(days_of_week, closed_weekly, label='Closed Issues', color='green')
plt.xlabel('Day of the Week')
plt.ylabel('Number of Issues')
plt.title(f'Weekly Progress of Open and Closed Issues - Week {week_number} {month_name}')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('weekly_chart.png')
plt.close(fig1)

# ------------------------------
# 2. Global Chart (Grouped by Month)
# ------------------------------
# Get sorted list of monthly keys (year, month)
months = sorted(set(list(open_issues_monthly.keys()) + list(closed_issues_monthly.keys())))
# Create labels in "Month-Year" format (e.g., "March-2023")
month_labels = [datetime(year, month, 1).strftime('%B-%Y') for (year, month) in months]
open_monthly = [open_issues_monthly.get(key, 0) for key in months]
closed_monthly = [closed_issues_monthly.get(key, 0) for key in months]

fig2 = plt.figure(figsize=(10, 5))
plt.plot(month_labels, open_monthly, label='Open Issues', color='blue')
plt.plot(month_labels, closed_monthly, label='Closed Issues', color='green')
plt.xlabel('Month')
plt.ylabel('Number of Issues')
plt.title('Global Progress of Open and Closed Issues (by Month)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('global_monthly_chart.png')
plt.close(fig2)

# ------------------------------
# 3. Global Chart (Grouped by Week with Custom Label "Week X - Month")
# ------------------------------
# Get the union of keys (year, month, week_of_month)
keys_custom = set(list(open_issues_weekly_custom.keys()) + list(closed_issues_weekly_custom.keys()))
# Sort keys by (year, month, week)
keys_custom = sorted(keys_custom, key=lambda k: (k[0], k[1], k[2]))

labels_custom = []
open_custom = []
closed_custom = []
for key in keys_custom:
    year, month, week = key
    # Get the month name using the first day of the month
    month_name_custom = datetime(year, month, 1).strftime('%B')
    label = f"Week {week} - {month_name_custom}"
    labels_custom.append(label)
    open_custom.append(open_issues_weekly_custom.get(key, 0))
    closed_custom.append(closed_issues_weekly_custom.get(key, 0))

fig3 = plt.figure(figsize=(10, 5))
x_positions = range(len(labels_custom))
plt.plot(x_positions, open_custom, label='Open Issues', color='blue', marker='o')
plt.plot(x_positions, closed_custom, label='Closed Issues', color='green', marker='o')
plt.xlabel('Week')
plt.ylabel('Number of Issues')
plt.title('Global Progress of Open and Closed Issues (by Week)')
plt.xticks(x_positions, labels_custom, rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('global_weekly_chart.png')
plt.close(fig3)
