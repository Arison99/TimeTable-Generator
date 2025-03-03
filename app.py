# app.py - Main Flask application
from flask import Flask, render_template, request, jsonify
import json
from csp_solver import solve_csp, get_solution_as_timetable

app = Flask(__name__)

# Initial data structure
data = {
    "programs": ["Computer Science", "Computer Security and Forensics", "Information Technology"],
    "course_units": {
        "Computer Science": ["CS101", "CS102", "CS103", "CS104", "CS105", "CS106"],
        "Computer Security and Forensics": ["CSF101", "CSF102", "CSF103", "CSF104", "CSF105", "CSF106"],
        "Information Technology": ["IT101", "IT102", "IT103", "IT104", "IT105", "IT106"]
    },
    "cross_cutting_courses": [
        {"id": "CC101", "programs": ["Computer Science", "Information Technology"]},
        {"id": "CC102", "programs": ["Computer Science", "Computer Security and Forensics"]},
        {"id": "CC103", "programs": ["Computer Security and Forensics", "Information Technology"]},
        {"id": "CC104", "programs": ["Computer Science", "Computer Security and Forensics", "Information Technology"]}
    ],
    "rooms": ["Room A", "Room B", "Room C", "Room D"],
    "instructors": ["Instructor 1", "Instructor 2", "Instructor 3", "Instructor 4", "Instructor 5", "Instructor 6"],
    "time_slots": [
        "Monday 9-11", "Monday 11-13", "Monday 14-16", "Monday 16-18",
        "Tuesday 9-11", "Tuesday 11-13", "Tuesday 14-16", "Tuesday 16-18",
        "Wednesday 9-11", "Wednesday 11-13", "Wednesday 14-16", "Wednesday 16-18",
        "Thursday 9-11", "Thursday 11-13", "Thursday 14-16", "Thursday 16-18",
        "Friday 9-11", "Friday 11-13", "Friday 14-16", "Friday 16-18"
    ],
    "instructor_availability": {},  # Will be filled by the UI
    "instructor_expertise": {}      # Will be filled by the UI
}

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    # Parse input data from the form
    form_data = request.form
    
    # Update the instructor availability and expertise based on form data
    for instructor in data["instructors"]:
        data["instructor_availability"][instructor] = json.loads(form_data.get(f"availability_{instructor}", "[]"))
        data["instructor_expertise"][instructor] = json.loads(form_data.get(f"expertise_{instructor}", "[]"))
    
    # Run the CSP solver
    solution = solve_csp(data)
    
    if solution:
        timetable = get_solution_as_timetable(solution, data)
        return jsonify({"success": True, "timetable": timetable})
    else:
        return jsonify({"success": False, "message": "No solution found. Try relaxing some constraints."})

if __name__ == '__main__':
    app.run(debug=True)