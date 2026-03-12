from flask import Flask, render_template, request, redirect, url_for, flash
import operator

import os

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
# Secret key required for Flask flash messages
app.secret_key = 'btec_distinction_secure_secret'

# Data Structures
# teams: { 'Team Name': {'members': [list of names], 'scores': {event_id: points}} }
teams = {}
# individuals: { 'Participant Name': {'scores': {event_id: points}} }
individuals = {}

# Constants for Validation
MAX_TEAMS = 4
MAX_TEAM_MEMBERS = 5
MAX_INDIVIDUALS = 20
MAX_EVENTS = 5
MAX_PARTICIPANTS_TOTAL = MAX_TEAMS + MAX_INDIVIDUALS # Used for position sanitization

# Points Scheme: 1st=10, 2nd=8, 3rd=6, 4th=4, 5th=2, 6th=1
POINTS_SCHEME = {
    1: 10,
    2: 8,
    3: 6,
    4: 4,
    5: 2,
    6: 1
}

def is_valid_name(name):
    """
    Purpose: Validates that a name contains at least one alphabetic character.
             This prevents names from being purely numeric strings.
    Inputs: name (str)
    Outputs: bool
    """
    return any(char.isalpha() for char in name)

def calculate_points(position):
    """
    Purpose: Calculates the awarded points based on the race position achieved.
    Inputs: position (int) - The position achieved in the event.
    Outputs: points (int) - The points awarded (1st=10...6th or lower=1).
    """
    try:
        # Convert to integer safely
        pos = int(position)
        if pos < 1:
            return 0
        # Per Design Doc: 1st=10, 2nd=8, 3rd=6, 4th=4, 5th=2, 6th or lower=1
        if pos >= 6:
            return 1
        return POINTS_SCHEME.get(pos, 0)
    except ValueError:
        return 0

def get_leaderboards():
    """
    Purpose: Calculates total points and generates leaderboards with "Joint Position" tie-breaking logic.
    Inputs: None.
    Outputs: tuple (sorted_teams, sorted_individuals) 
             Each list contains tuples: (rank, name, total_points).
    Efficiency Improvement: Uses operator.itemgetter(1) for lightning-fast sorting of the raw point list.
    """
    def process_ranking(total_list):
        # Sort by points descending
        sorted_list = sorted(total_list, key=operator.itemgetter(1), reverse=True)
        ranked_list = []
        current_rank = 1
        for i, (name, points) in enumerate(sorted_list):
            if i > 0 and points < sorted_list[i-1][1]:
                current_rank = i + 1
            ranked_list.append((current_rank, name, points))
        return ranked_list

    team_totals = [(name, sum(data['scores'].values())) for name, data in teams.items()]
    individual_totals = [(name, sum(data['scores'].values())) for name, data in individuals.items()]
    
    return process_ranking(team_totals), process_ranking(individual_totals)

@app.route('/')
def index():
    """
    Purpose: Renders the main dashboard of the application with forms and live leaderboards.
    Inputs: None.
    Outputs: HTML response generated precisely from the 'index.html' template.
    """
    sorted_teams, sorted_individuals = get_leaderboards()
    return render_template('index.html', teams=sorted_teams, individuals=sorted_individuals, team_list=teams.keys(), ind_list=individuals.keys())

@app.route('/register_team', methods=['POST'])
def register_team():
    """
    Purpose: Handles the registration of a new team, validating the system limit constraints.
    Inputs: HTTP POST data containing 'team_name'.
    Outputs: A redirect response back to the main index dashboard page.
    """
    try:
        team_name = request.form.get('team_name', '').strip()
        
        if not team_name:
            flash("Validation Error: Team name cannot be empty.", "error")
            return redirect(url_for('index'))
            
        if not is_valid_name(team_name):
            flash("Validation Error: Team name must contain at least one alphabetic character. Numeric-only names are prohibited.", "error")
            return redirect(url_for('index'))
            
        if team_name in teams:
            flash(f"Team '{team_name}' is already registered.", "error")
            return redirect(url_for('index'))
            
        if len(teams) >= MAX_TEAMS:
            flash(f"Registration failed: Strict maximum limit of {MAX_TEAMS} teams has been reached.", "error")
        else:
            teams[team_name] = {'members': [], 'scores': {}}
            flash(f"Team '{team_name}' registered successfully.", "success")
            
    except Exception as e:
        flash(f"An unexpected system error occurred during team registration: {str(e)}", "error")
        
    return redirect(url_for('index'))

@app.route('/register_individual', methods=['POST'])
def register_individual():
    """
    Purpose: Handles the registration of an individual competitor, enforcing the constraints.
    Inputs: HTTP POST data containing 'individual_name'.
    Outputs: A redirect response back to the main dashboard page.
    """
    try:
        ind_name = request.form.get('individual_name', '').strip()
        
        if not ind_name:
            flash("Validation Error: Individual name cannot be empty.", "error")
            return redirect(url_for('index'))
            
        if not is_valid_name(ind_name):
            flash("Validation Error: Participant name must contain at least one alphabetic character. Numeric-only names are prohibited.", "error")
            return redirect(url_for('index'))
            
        if ind_name in individuals:
            flash(f"Individual '{ind_name}' is already registered.", "error")
            return redirect(url_for('index'))
            
        if len(individuals) >= MAX_INDIVIDUALS:
            flash(f"Registration failed: Strict maximum limit of {MAX_INDIVIDUALS} individuals reached.", "error")
        else:
            individuals[ind_name] = {'scores': {}}
            flash(f"Individual '{ind_name}' registered successfully.", "success")
            
    except Exception as e:
        flash(f"An unexpected system error occurred during individual registration: {str(e)}", "error")
        
    return redirect(url_for('index'))

@app.route('/record_score', methods=['POST'])
def record_score():
    """
    Purpose: Securely records an event score for a participant (team or individual). It enforces
             vital validation rules, such as preventing text in numeric fields and ensuring single
             entry per event.
    Inputs: HTTP POST data specifying participant_type, name, event_num, and position.
    Outputs: A redirect response back to the main overview.
    """
    try:
        participant_type = request.form.get('participant_type')
        name = request.form.get('name')
        event_num_str = request.form.get('event_num')
        position_str = request.form.get('position')
        
        # 1. Validation for purely empty fields
        if not all([participant_type, name, event_num_str, position_str]):
            flash("All fields are required to successfully record a score.", "error")
            return redirect(url_for('index'))
            
        # 2. Hard Data Type Validation with Try/Except (Handles "text in number fields" gracefully)
        try:
            event_num = int(event_num_str)
            position = int(position_str)
        except ValueError:
            flash("Validation Error: Event Number and Position must purely be integers. Text inputs are blocked.", "error")
            return redirect(url_for('index'))
            
        # 3. Logical Bounds & Sanitization (Handles Extreme Data)
        if event_num < 1 or event_num > MAX_EVENTS:
            flash(f"Sanitization Error: Event Number {event_num} is out of bounds. Must be 1 to {MAX_EVENTS}.", "error")
            return redirect(url_for('index'))
            
        if position < 1:
            flash("Sanitization Error: Position must be 1 or greater.", "error")
            return redirect(url_for('index'))
            
        if position > MAX_PARTICIPANTS_TOTAL:
            flash(f"Sanitization Error: Position {position} is unrealistic for a tournament of this size (Max {MAX_PARTICIPANTS_TOTAL} participants).", "error")
            return redirect(url_for('index'))
            
        # 4. Lookup Logic
        target_dict = teams if participant_type == 'team' else individuals
        
        if name not in target_dict:
            flash(f"Target participant '{name}' could not be located in records.", "error")
            return redirect(url_for('index'))
            
        # 5. Data Correction Logic (Allowing Updates)
        is_edit = event_num in target_dict[name]['scores']
        
        # Execute approved scoring assignment/update
        points = calculate_points(position)
        target_dict[name]['scores'][event_num] = points
        
        if is_edit:
            flash(f"Success: Entry updated! {name}'s score for Event #{event_num} corrected to Rank #{position} ({points} pts).", "success")
        else:
            flash(f"Success: Score committed! {name} obtained {points} points for Rank #{position} in Event #{event_num}.", "success")
        
    except Exception as e:
        flash(f"An unexpected critical error occurred: {str(e)}", "error")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
