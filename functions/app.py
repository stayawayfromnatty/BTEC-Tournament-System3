import os
import operator
import re
import serverless_wsgi
from flask import Flask, render_template, request, redirect, url_for, flash

# Consolidate Flask engine and Serverless handler into one file for Netlify
# Robust absolute path for templates folder to ensure Netlify finds it
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'btec_distinction_secure_secret'

# --- Data Structures ---
teams = {}
individuals = {}
MAX_TEAMS = 4
MAX_INDIVIDUALS = 20
MAX_EVENTS = 5
MAX_PARTICIPANTS_TOTAL = MAX_TEAMS + MAX_INDIVIDUALS
POINTS_SCHEME = {1: 10, 2: 8, 3: 6, 4: 4, 5: 2}

def is_valid_name(name):
    # Enforces alphanumeric and space characters only, and checks for at least one letter
    return bool(re.match(r'^[a-zA-Z0-9\s]+$', name)) and any(char.isalpha() for char in name)

def calculate_points(position):
    try:
        pos = int(position)
        if pos < 1: return 0
        if pos >= 6: return 1
        return POINTS_SCHEME.get(pos, 0)
    except ValueError: return 0

def get_leaderboards():
    def process_ranking(total_list):
        sorted_list = sorted(total_list, key=lambda x: x[1], reverse=True)
        ranked_list = []
        current_rank = 1
        for i, (name, points, scores) in enumerate(sorted_list):
            if i > 0 and points < sorted_list[i-1][1]:
                current_rank = i + 1
            ranked_list.append((current_rank, name, points, scores))
        return ranked_list
    team_totals = [(name, sum(data['scores'].values()), data['scores']) for name, data in teams.items()]
    individual_totals = [(name, sum(data['scores'].values()), data['scores']) for name, data in individuals.items()]
    return process_ranking(team_totals), process_ranking(individual_totals)

@app.route('/')
def index():
    sorted_teams, sorted_individuals = get_leaderboards()
    return render_template('index.html', teams=sorted_teams, individuals=sorted_individuals, team_list=teams.keys(), ind_list=individuals.keys())

@app.route('/register_team', methods=['POST'])
def register_team():
    team_name = request.form.get('team_name', '').strip()
    if not team_name or not is_valid_name(team_name):
        flash("Validation Error: Team name must be non-empty and contains letters.", "error")
    elif team_name in teams:
        flash(f"Error: Team '{team_name}' already exists.", "error")
    elif len(teams) >= MAX_TEAMS:
        flash("Limit reached: Max 4 teams allowed.", "error")
    else:
        teams[team_name] = {'members': [], 'scores': {}}
        flash(f"Success: Team '{team_name}' registered.", "success")
    return redirect(url_for('index'))

@app.route('/register_individual', methods=['POST'])
def register_individual():
    ind_name = request.form.get('individual_name', '').strip()
    if not ind_name or not is_valid_name(ind_name):
        flash("Validation Error: Name must be non-empty and contains letters.", "error")
    elif ind_name in individuals:
        flash(f"Error: Individual '{ind_name}' already exists.", "error")
    elif len(individuals) >= MAX_INDIVIDUALS:
        flash("Limit reached: Max 20 individuals allowed.", "error")
    else:
        individuals[ind_name] = {'scores': {}}
        flash(f"Success: Individual '{ind_name}' registered.", "success")
    return redirect(url_for('index'))

@app.route('/record_score', methods=['POST'])
def record_score():
    try:
        type = request.form.get('participant_type')
        name = request.form.get('name')
        ev = int(request.form.get('event_num'))
        pos = int(request.form.get('position'))
        
        if ev < 1 or ev > MAX_EVENTS:
            flash("Sanitization Error: Event out of range.", "error")
        elif pos < 1 or pos > MAX_PARTICIPANTS_TOTAL:
            flash(f"Sanitization Error: Rank {pos} is unrealistic.", "error")
        else:
            target = teams if type == 'team' else individuals
            if name in target:
                is_edit = ev in target[name]['scores']
                pts = calculate_points(pos)
                target[name]['scores'][ev] = pts
                msg = "Entry updated!" if is_edit else "Score committed!"
                flash(f"Success: {msg} {name} got {pts} pts.", "success")
            else:
                flash("Error: Participant not found.", "error")
    except (ValueError, TypeError):
        flash("Validation Error: Please enter numeric values for event and position.", "error")
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    teams.clear()
    individuals.clear()
    flash("Success: All standard data and leaderboards have been reset.", "success")
    return redirect(url_for('index'))

# Netlify Serverless Handler with Error Logging
def handler(event, context):
    try:
        return serverless_wsgi.handle_request(app, event, context)
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        return {
            "statusCode": 500,
            "body": f"Flask Engine Initialization Error: {str(e)}\n\nTraceback:\n{error_info}",
            "headers": {"Content-Type": "text/plain"}
        }

if __name__ == '__main__':
    app.run(debug=True)
