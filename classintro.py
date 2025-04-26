students = []

class StudentInfo:

    def setStudent(self, name, age):
        self.name = name
        self.age = age
        student = {'Name': self.name, 'Age': self.age}
        students.append(student)
        return student

    @staticmethod
    def getStudent():
        return "students this is string a static method"



stdinfo = StudentInfo()
stdinfo.setStudent("John", 20)

stdinfo.setStudent("Jane", 22)
stdinfo.setStudent("Doe", 21)

stdinfo1 = StudentInfo()

print(f"1",stdinfo)
print(f"2",stdinfo1)
print(f"3",students)
print(StudentInfo.getStudent())

print("show ing what kind of __name it is:-----------> ", __name__)

if __name__ == "__main__":
    print(" * this is inside double dunder* ")
    stdinfo = StudentInfo()
    print(StudentInfo.getStudent())
    stdinfo.setStudent("John1", 20)
    stdinfo.setStudent("Jane2", 22)
    stdinfo.setStudent("Doe3", 21)
    


    ''' this is a class that is used to create a student object and set the name and age of the student. 
    but the object is not used to get the name and age of the student.
    instead, the class is used to create a student object and set the name and age of the student.
    but the object is not used to get the name and age of the student.'''


''' here class is used to create a student object and set the name and age of the student. 
    but the object is not used to get the name and age of the student.
    instead, the class is used to create a student object and set the name and age of the student.
    but the object is not used to get the name and age of the student.'''

