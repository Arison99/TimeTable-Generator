# csp_solver.py - CSP solver implementation using backtracking
from constraint import Problem, AllDifferentConstraint
import itertools

def solve_csp(data):
    """
    Solve the university timetable scheduling CSP problem
    """
    problem = Problem()
    
    # Gather all courses (regular and cross-cutting)
    all_courses = []
    for program in data["programs"]:
        all_courses.extend(data["course_units"][program])
    all_courses.extend([cc["id"] for cc in data["cross_cutting_courses"]])
    
    # Variables: Each course needs a (room, time slot, instructor) assignment
    for course in all_courses:
        problem.addVariable(course, [
            (room, time_slot, instructor)
            for room in data["rooms"]
            for time_slot in data["time_slots"]
            for instructor in data["instructors"]
            if instructor_is_available(instructor, time_slot, data) and 
               instructor_has_expertise(instructor, course, data)
        ])
    
    # Constraint 1: No two courses can be in the same room at the same time
    for course1, course2 in itertools.combinations(all_courses, 2):
        problem.addConstraint(
            lambda c1, c2: c1[0] != c2[0] or c1[1] != c2[1],  # Different room or different time
            (course1, course2)
        )
    
    # Constraint 2: No instructor can teach two different courses at the same time
    for course1, course2 in itertools.combinations(all_courses, 2):
        problem.addConstraint(
            lambda c1, c2: c1[2] != c2[2] or c1[1] != c2[1],  # Different instructor or different time
            (course1, course2)
        )
    
    # Constraint 3: Courses for the same program must not overlap in time
    for program in data["programs"]:
        program_courses = data["course_units"][program]
        for course1, course2 in itertools.combinations(program_courses, 2):
            problem.addConstraint(
                lambda c1, c2: c1[1] != c2[1],  # Different time slots
                (course1, course2)
            )
    
    # Constraint 4: Cross-cutting courses must not overlap with their respective program courses
    for cc in data["cross_cutting_courses"]:
        cc_id = cc["id"]
        for program in cc["programs"]:
            for course in data["course_units"][program]:
                problem.addConstraint(
                    lambda cc_val, course_val: cc_val[1] != course_val[1],  # Different time slots
                    (cc_id, course)
                )
    
    # Solve the CSP
    return problem.getSolution()

def instructor_is_available(instructor, time_slot, data):
    """Check if instructor is available in the given time slot"""
    if instructor not in data["instructor_availability"]:
        return True  # Default to available if not specified
    return time_slot in data["instructor_availability"][instructor]

def instructor_has_expertise(instructor, course, data):
    """Check if instructor has expertise for the given course"""
    if instructor not in data["instructor_expertise"]:
        return True  # Default to having expertise if not specified
    
    # For cross-cutting courses, check if the instructor has expertise in any of the related programs
    for cc in data["cross_cutting_courses"]:
        if cc["id"] == course:
            for program in cc["programs"]:
                if program in data["instructor_expertise"][instructor]:
                    return True
            return False
    
    # For regular courses, determine which program it belongs to
    for program in data["programs"]:
        if course in data["course_units"][program]:
            return program in data["instructor_expertise"][instructor]
    
    return False  # Default if course not found

def get_solution_as_timetable(solution, data):
    """Convert the CSP solution to a timetable format for display"""
    # Create an empty timetable
    timetable = {
        room: {time_slot: None for time_slot in data["time_slots"]}
        for room in data["rooms"]
    }
    
    # Fill in the timetable with the solution
    for course, (room, time_slot, instructor) in solution.items():
        # Determine which program(s) this course belongs to
        programs = []
        for program in data["programs"]:
            if course in data["course_units"][program]:
                programs.append(program)
        
        # Check if it's a cross-cutting course
        if not programs:
            for cc in data["cross_cutting_courses"]:
                if cc["id"] == course:
                    programs = cc["programs"]
                    break
        
        timetable[room][time_slot] = {
            "course": course,
            "instructor": instructor,
            "programs": programs
        }
    
    return timetable