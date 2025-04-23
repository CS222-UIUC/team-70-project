# Wikipedle Django Management Commands

## fetch_wikipedia_articles.py

Fetches random Wikipedia articles.

```
python manage.py fetch_wikipedia_articles [--count COUNT]
```

## manage_articles.py

Manages Wikipedia articles.

```
python manage.py manage_articles [options]
```

| Option | Description |
|--------|-------------|
| `--select-daily` | Select daily article for today |
| `--select-for-days DAYS` | Select articles for future days |
| `--cleanup` | Remove old articles |
| `--max-age DAYS` | Max age for articles (default: 30) |
| `--date DATE` | Select for specific date (YYYY-MM-DD) |
| `--list` | List cached articles |
| `--show ID` | Show article details |
| `--clear-all` | Clear all articles |

## manage_users.py

Manages user data.

```
python manage.py manage_users [options]
```

| Option | Description |
|--------|-------------|
| `--reset-streak` | Reset streak for inactive users |
| `--recalculate-stats` | Recalculate user statistics |
| `--user USERNAME` | Specify user for operations |
| `--inactive-days DAYS` | Days to consider inactive (default: 30) |
| `--list-inactive` | List inactive users |

## manage_test_users.py

Manages test users for development.

```
python manage.py manage_test_users [options]
```

| Option | Description |
|--------|-------------|
| `--add COUNT` | Add number of test users |
| `--delete` | Delete all test users |
| `--list` | List all test users |
| `--reset` | Reset test user data |
| `--password PASSWORD` | Set password (default: testpass123) |

## display_leaderboard.py

Displays global leaderboard data.

```
python manage.py display_leaderboard [options]
```

| Option | Description |
|--------|-------------|
| `--date DATE` | Display for specific date (YYYY-MM-DD) |
| `--days DAYS` | Display past days (default: 1) |
| `--top N` | Display top N players (default: 10) |
| `--format FORMAT` | Output format: table or JSON |
| `--username USERNAME` | Find specific user's ranking |

## update_leaderboard.py

Updates global leaderboards.

```
python manage.py update_leaderboard [options]
```

| Option | Description |
|--------|-------------|
| `--date DATE` | Update specific date (YYYY-MM-DD) |
| `--days DAYS` | Update past days (default: 1) |
| `--force` | Force update regardless of last update i