import random
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# File paths
PEOPLE_FILE = 'people.txt'
PAST_ASSIGNMENTS_FILE = 'past_assignments.json'

# Load the list of people
def load_people(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Load past assignments
def load_past_assignments(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save past assignments
def save_past_assignments(file_path, assignments):
    with open(file_path, 'w') as file:
        json.dump(assignments, file)

# Check if a person did the task in the past n days
def did_recently(person, assignments, days=2):
    cutoff_date = datetime.now().date() - timedelta(days=days)
    return any(entry['name'] == person and datetime.strptime(entry['date'], '%Y-%m-%d').date() > cutoff_date for entry in assignments)

# Choose the next person with weighted probabilities
def choose_person(people, assignments):
    eligible_people = [person for person in people if not did_recently(person, assignments, days=2)]
    if not eligible_people:
        return None
    weights = [0.1 if did_recently(person, assignments, days=30) else 1.0 for person in eligible_people]
    return random.choices(eligible_people, weights=weights, k=1)[0]

# Assign today's dish washers
def assign_dishwashers(available_people, assignments, num_people=5):
    chosen_people = []
    remaining_people = available_people[:]
    
    while len(chosen_people) < num_people and remaining_people:
        chosen_one = choose_person(remaining_people, assignments)
        if chosen_one:
            chosen_people.append(chosen_one)
            remaining_people.remove(chosen_one)
        else:
            break
    
    return chosen_people

@app.route('/')
def index():
    people = load_people(PEOPLE_FILE)
    past_assignments = load_past_assignments(PAST_ASSIGNMENTS_FILE)
    today_dishwashers = assign_dishwashers(people, past_assignments, num_people=5)
    return render_template('index.html', dishwashers=today_dishwashers)

@app.route('/select', methods=['POST'])
def select():
    chosen_person = request.form['chosen_person']
    past_assignments = load_past_assignments(PAST_ASSIGNMENTS_FILE)
    past_assignments.append({'name': chosen_person, 'date': datetime.now().strftime('%Y-%m-%d')})
    save_past_assignments(PAST_ASSIGNMENTS_FILE, past_assignments)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
