# basketball
This is an API built using python django framework. Tested on a Windows 10 machine, Please follow below steps for local setup

## Project setup steps
1. Install dependencies
```bash
pip install -r requirements.txt 
```

2. Create a PostgreSQL database
Create a postgres database with the name basketball_league_db

3. Update the .env file
Update the .env file with below DataBase credentials
```bash
DB_NAME=basketball_league_prod
DB_USER=<username>
DB_PASSWORD=<pwd>
DB_HOST=localhost
DB_PORT=5432
```

4. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Generate mock data 
```bash
python manage.py generate_fake_data
```

This will generate a default ADMIN, Coaches and Few Players with other relavant mappings.
Their user credentials follow below structure
```bash
username: <"admin" | "coach1" | "player0_team10">
password: <"admin@123" | "coach@123" | "player@123">
```

6. Run the development server
```bash
python manage.py runserver
```

To call the APIs you need to login first as an Admin/Coach/Player.
After the successfull login, it will return a user token, which you need to pass as the OAUTH token for other API calls as the authorization header.
Also you can register new Coaches, new Players and new Teams as well with the API set.
I have authorized the API as per requested User Permission Model. Please check basketball_league/urls.py file for more info.

8. Running Integration TestCases:
```bash
python manage.py test
```

Note: Additionally I have exported the Postman API collection as well.
