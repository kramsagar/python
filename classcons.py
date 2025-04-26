students = []


class Student:

	school_name = "Springfield Elementary"

	def __init__(self, name, student_id=332):
		self.name = name
		self.student_id = student_id
		students.append(self)

	def __str__(self):
		return "Student " + self.name

	def get_name_upper(self):
		return self.name.upper()

	def get_school_name(self):
		return self.school_name


one = Student("james",123)
two = Student("john", 456)
three = Student("job")

print(one); 
print(two)
print(three)


print(students)
print(students[0].get_name_upper())
print(students[0])


#class variable
print(Student.school_name);print(id(Student.school_name));
print(one.school_name);print(id(one.school_name));
print(two.school_name) ;print(id(two.school_name));
print(one.get_school_name()); print(id(one.get_school_name()));
print(two.get_school_name()); print(id(two.get_school_name()));
