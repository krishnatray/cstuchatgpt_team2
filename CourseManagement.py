import json
import random
import string

class CourseManagement:
    def __init__(self):
        self.courses = []

    def load_courses_data(self):
        try:
            with open('courses.json', 'r') as file:
                self.courses = json.load(file)
        except FileNotFoundError:
            self.courses = []

    def save_courses_data(self):
        with open('courses.json', 'w') as file:
            json.dump(self.courses, file, indent=4)

    def get_course_information(self, course_id=None, course_title=None, course_description=None):
        self.load_courses_data()

        if not course_id and not course_title:
            return "Please provide either 'course_id' or 'course_title'."
        #print (course_id, self.courses)
        for course_data in self.courses:
            #print(course_data['course_id'], course_id)
            #print(course_data['course_id'] == course_id)
            if course_data['course_id'] == course_id or course_data['course_title'] == course_title:

                return json.dumps(course_data)

        return "Course not found."

    def create_course_information(self, course_id, course_title, course_description):
        self.load_courses_data()

        for existing_course in self.courses:
            if existing_course['course_id'] == course_id:
                return f"Course with ID '{course_id}' already exists. Cannot create a duplicate course. Do you want to update it?"

        # Create a new course dictionary for the current course
        course_data = {
            'course_id': course_id,
            'course_title': course_title,
            'course_description': course_description
        }

        # Append the new course dictionary to the list
        self.courses.append(course_data)

        # Write the updated list of course data back to the JSON file
        self.save_courses_data()

        return f"Course information for '{course_id}' has been saved to 'courses.json'."

    def update_course_information(self, course_id, new_title=None, new_description=None):
        self.load_courses_data()

        course_found = False
        for course_data in self.courses:
            if course_data['course_id'] == course_id:
                # Update the course data with new information if provided
                if new_title:
                    course_data['course_title'] = new_title
                if new_description:
                    course_data['course_description'] = new_description
                course_found = True
                break

        if not course_found:
            return f"Course with ID '{course_id}' not found."

        # Write the updated list of course data back to the JSON file
        self.save_courses_data()

        return f"Course information for '{course_id}' has been updated."

# Example usage:
if __name__ == "__main__":
    course_manager = CourseManagement()

    # Generate course information for 5 courses
    course_manager.create_course_information("CSCI101", "Introduction to Computer Science", "Learn the basics of programming.")
    course_manager.create_course_information("MATH202", "Advanced Mathematics", "Covers calculus and linear algebra.")
    course_manager.create_course_information("ENG301", "English Literature", "Explore classic works of literature.")
    course_manager.create_course_information("HIST101", "World History", "Covers major historical events.")

    # Get course information
    print(course_manager.get_course_information(course_id="CSCI101"))
    print(course_manager.get_course_information(course_title="Advanced Mathematics"))

    # Update course information
    course_manager.update_course_information("ENG301", new_description="Explore classic works of English literature.")

    # Print the list of courses
    print(course_manager.courses)
