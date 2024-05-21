import random
import json
import sys
from datetime import datetime, timedelta
from collections import Counter

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

# Main function
def main(test_mode=False):
    people = load_people(PEOPLE_FILE)
    past_assignments = load_past_assignments(PAST_ASSIGNMENTS_FILE)
    
    # Example of available people for today (can be the full list or a subset)
    available_people = people
    
    # Assign the task
    today_dishwashers = assign_dishwashers(available_people, past_assignments, num_people=5)
    
    if today_dishwashers:
        print("Today's dishwashers are:")
        for idx, person in enumerate(today_dishwashers, start=1):
            print(f"{idx}. {person}")
        
        if test_mode:
            # Simulate random choice for testing
            chosen_index = random.choice([1, 2, 3, 4, 5])
        else:
            # Prompt user to input who actually did the dishwashing
            while True:
                try:
                    chosen_index = int(input(f"Who ended up doing the dishwashing? (Enter 1, 2, 3, 4, or 5): "))
                    if chosen_index in [1, 2, 3, 4, 5]:
                        break
                    else:
                        print("Invalid input. Please enter 1, 2, 3, 4, or 5.")
                except ValueError:
                    print("Invalid input. Please enter a number (1, 2, 3, 4, or 5).")
        
        chosen_person = today_dishwashers[chosen_index - 1]
        past_assignments.append({'name': chosen_person, 'date': datetime.now().strftime('%Y-%m-%d')})
        
        # Save the updated assignments
        save_past_assignments(PAST_ASSIGNMENTS_FILE, past_assignments)
        
        print(f"{chosen_person} did the dishwashing today.")
    else:
        print("No one is available to do the dishes today.")

# Test script
def test_probability(runs=1000):
    results = Counter()
    people = load_people(PEOPLE_FILE)
    
    # Reset past assignments
    past_assignments = []
    save_past_assignments(PAST_ASSIGNMENTS_FILE, past_assignments)
    
    for _ in range(runs):
        today_dishwashers = assign_dishwashers(people, past_assignments, num_people=5)
        if today_dishwashers:
            chosen_person = random.choice(today_dishwashers)  # Simulate user choosing one of the five
            results.update([chosen_person])
            past_assignments.append({'name': chosen_person, 'date': datetime.now().strftime('%Y-%m-%d')})
        
        # Reset past assignments periodically to simulate a continuous process
        if len(past_assignments) > 40:  # For example, reset after a certain number of assignments
            past_assignments = []
            save_past_assignments(PAST_ASSIGNMENTS_FILE, past_assignments)
    
    # Print the results
    total_picks = sum(results.values())
    print(f"Total picks in {runs} runs: {total_picks}")
    for person in people:
        print(f"{person}: {results[person]} times, probability: {results[person] / total_picks:.2%}")

if __name__ == "__main__":
    if '--test' in sys.argv:
        test_probability(1000)
    else:
        main()
