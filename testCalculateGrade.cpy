#$ Moisiadou Sofia 4446 #$
#$ Tsiaousi Thomai 4510 #$
#$ In this test we created a simple programm that calculates the lesson's grade and succesfully compiles in cpy #$


def main_calculateGrade():
#{
    #declare x , y
    x=3;
    y=5;
    project_grade = x*(1//2);
    exam_grade = y*(1//2);
    final_grade = project_grade + exam_grade; 

    if (project_grade >=5):
        if (exam_grade>=5):
            print(final_grade);
        else :
            print(exam_grade);
    else :
        print(project_grade);
#}

if __name__ == "__main__":
    main_calculateGrade();