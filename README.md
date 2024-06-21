# basketball
Matific Assignment

## Project setup steps
1. Install dependencies
```bash
pip install -r requirements.txt 
```

2. Create a PostgreSQL database
Create a postgres database with the name basketball_league_db

3. Update the .env file
Update the .env file with database user_name and password

4. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Generate mock data 
```bash
python manage.py generate_fake_data
```

6. Run the development server
```bash
python manage.py runserver
```
