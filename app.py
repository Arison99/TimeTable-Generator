# app.py - Main Flask application
from flask import Flask, render_template, request, jsonify
import json
import os
from csp_solver import solve_csp, get_solution_as_timetable

app = Flask(__name__)

# File path for storing data
DATA_FILE = 'timetable_data.json'

# Initialize with empty data structure
data = {
    "programs": [],
    "course_units": {},
    "cross_cutting_courses": [],
    "rooms": [],
    "instructors": [],
    "instructor_availability": {},
    "instructor_expertise": {},
    "time_slots": ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]  # Default time slots
}

# Function to load data from file
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            print("Data loaded successfully from", DATA_FILE)
        except Exception as e:
            print(f"Error loading data: {e}")

# Function to save data to file
def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved successfully to", DATA_FILE)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

# Load data at startup
load_data()

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/data')
def data_page():
    return render_template('data.html', data=data)

@app.route('/add-programs', methods=['POST'])
def add_program():
    program = request.form.get('program')
    if program and program not in data['programs']:
        data['programs'].append(program)
        save_data()
    return render_template('partials/program_list.html', programs=data['programs'])

@app.route('/add-course-unit', methods=['POST'])
def add_course_unit():
    program = request.form.get('program')
    course_unit = request.form.get('course_unit')
    if program in data['programs'] and course_unit:
        if program not in data['course_units']:
            data['course_units'][program] = []
        if course_unit not in data['course_units'][program]:
            data['course_units'][program].append(course_unit)
            save_data()
    return render_template('partials/course_unit_list.html', course_units=data['course_units'])

@app.route('/add-cross-cutting-course', methods=['POST'])
def add_cross_cutting_course():
    course_id = request.form.get('course_id')
    programs = request.form.getlist('programs')
    if course_id and programs:
        data['cross_cutting_courses'].append({"id": course_id, "programs": programs})
        save_data()
    return render_template('partials/cross_cutting_list.html', cross_cutting_courses=data['cross_cutting_courses'])

@app.route('/add-room', methods=['POST'])
def add_room():
    room = request.form.get('room')
    if room and room not in data['rooms']:
        data['rooms'].append(room)
        save_data()
    return render_template('partials/room_list.html', rooms=data['rooms'])

@app.route('/add-instructor', methods=['POST'])
def add_instructor():
    instructor = request.form.get('instructor')
    if instructor and instructor not in data['instructors']:
        data['instructors'].append(instructor)
        save_data()
    return render_template('partials/instructor_list.html', instructors=data['instructors'])

@app.route('/add-instructor-availability', methods=['POST'])
def add_instructor_availability():
    instructor = request.form.get('instructor')
    time_slots = request.form.getlist('time_slots')
    if instructor in data['instructors'] and time_slots:
        data['instructor_availability'][instructor] = time_slots
        save_data()
    return render_template('partials/instructor_availability.html', availabilities=data['instructor_availability'])

@app.route('/add-instructor-expertise', methods=['POST'])
def add_instructor_expertise():
    instructor = request.form.get('instructor')
    course_units = request.form.getlist('course_units')
    if instructor in data['instructors'] and course_units:
        data['instructor_expertise'][instructor] = course_units
        save_data()
    return render_template('partials/instructor_expertise.html', expertise=data['instructor_expertise'])

@app.route('/remove-room/<room>', methods=['DELETE'])
def remove_room(room):
    if room in data['rooms']:
        data['rooms'].remove(room)
        save_data()
    return render_template('partials/room_list.html', rooms=data['rooms'])

@app.route('/remove-instructor/<instructor>', methods=['DELETE'])
def remove_instructor(instructor):
    if instructor in data['instructors']:
        data['instructors'].remove(instructor)
        if instructor in data['instructor_availability']:
            del data['instructor_availability'][instructor]
        if instructor in data['instructor_expertise']:
            del data['instructor_expertise'][instructor]
        save_data()
    return render_template('partials/instructor_list.html', instructors=data['instructors'])

@app.route('/remove-expertise/<instructor>', methods=['DELETE'])
def remove_expertise(instructor):
    if instructor in data['instructor_expertise']:
        del data['instructor_expertise'][instructor]
        save_data()
    return render_template('partials/instructor_expertise.html', expertise=data['instructor_expertise'])

@app.route('/remove-availability/<instructor>', methods=['DELETE'])
def remove_availability(instructor):
    if instructor in data['instructor_availability']:
        del data['instructor_availability'][instructor]
        save_data()
    return render_template('partials/instructor_availability.html', availabilities=data['instructor_availability'])

@app.route('/remove-cross-cutting/<int:index>', methods=['DELETE'])
def remove_cross_cutting(index):
    if 0 <= index < len(data['cross_cutting_courses']):
        data['cross_cutting_courses'].pop(index)
        save_data()
    return render_template('partials/cross_cutting_list.html', cross_cutting_courses=data['cross_cutting_courses'])

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    # Parse input data from the form
    form_data = request.form
    
    # Update the instructor availability and expertise based on form data
    for instructor in data["instructors"]:
        availability_key = f"availability_{instructor}"
        expertise_key = f"expertise_{instructor}"
        
        if availability_key in form_data:
            data["instructor_availability"][instructor] = json.loads(form_data.get(availability_key, "[]"))
        
        if expertise_key in form_data:
            data["instructor_expertise"][instructor] = json.loads(form_data.get(expertise_key, "[]"))
    
    # Run the CSP solver
    solution = solve_csp(data)
    
    if solution:
        timetable = get_solution_as_timetable(solution, data)
        return jsonify({"success": True, "timetable": timetable})
    else:
        return jsonify({"success": False, "message": "No solution found. Try relaxing some constraints or adding more data."})

if __name__ == '__main__':
    app.run(debug=True)