#$ Moisiadou Sofia 4446 #$
#$ Tsiaousi Thomai 4510 #$
#$ In this test we created a simple programm that counts down a given number succesfully compiles in cpy #$

def main_countdown():
#{

    #declare x
    x = int(input());
    while (x>0):
    #{
        x=x-1;
        print(x);
    #}

#}

if __name__ == "__main__":
    main_countdown();