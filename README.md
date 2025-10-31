# WP-MS-mig

Migration Wordpress posts to Mediastream platform

## WordPress Post Fetcher

This repository includes a small Python utility that retrieves posts from the WordPress REST API and stores the fields in a local SQLite database.

### Requirements

- Python 3.9+
- `requests` library (`pip install requests`)

### Configuration

1. Copy the sample configuration file and update it with your WordPress credentials and target database location:

   ```bash
   cp config.example.ini config.ini
   ```

2. Edit `config.ini` and set:
   - `base_url`: Base URL of the WordPress site.
   - `username` and `application_password`: Optional, required if the posts are not public. Use a WordPress Application Password.
   - `date`: ISO-8601 date (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`) used to fetch posts created on or after that moment.
   - `per_page`: Number of posts fetched per request (up to 100).
   - `path`: SQLite database file path where posts will be stored.

### Usage

Install dependencies and run the fetcher:

```bash
pip install -r requirements.txt  # or pip install requests
python fetch_posts.py --config config.ini
```

You can adjust the log verbosity:

```bash
python fetch_posts.py --config config.ini --log-level DEBUG
```

The script will create the SQLite database (if it does not exist) and insert or update the posts returned by the WordPress API. Each execution respects the provided date filter, so only posts created on or after the specified date are retrieved.

### Database Schema

Posts are stored in the `posts` table with the following columns:

- `id` (primary key)
- `date`
- `slug`
- `status`
- `type`
- `link`
- `title`
- `content`
- `excerpt`

Running the script multiple times will update existing records if WordPress posts change.
