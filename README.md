Technologies Used
- Python 3 with Flask
- MySQL
- HTML/CSS
How to Run

1. Clone the Repo

git clone https://github.com/JeremyMarlinghaus/job-application-tracker.git
cd job-application-tracker


2. Install the Required Packages

pip install flask mysql-connector-python


3. Set Up the Database
Run the schema file in MySQL to create all the tables and load the sample data:

mysql -u root -p < schema.sql

4. Add Your MySQL Password
In database.py, find line 7 and replace `YOUR_PASSWORD` with your actual MySQL password:
python
password="YOUR_PASSWORD",


5. Start the App
python app.py

6. Open It in Your Browser
http://127.0.0.1:5000


What the App Does
- Dashboard - Shows a quick overview of all your stats
- Companies - Keep track of companies you're interested in
- Jobs - Save job listings you want to apply to
- Applications - Log your applications and update their status as things progress
- Contacts - Store recruiter and hiring manager info
- Job Match - Type in your skills and see which jobs you'd be a good fit for using our percentage calculator
