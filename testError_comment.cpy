#$ Moisiadou Sofia 4446 #$
#$ Tsiaousi Thomai 4510 #$
#$ This test will return error because the comment is given in the wrong order at line 12 #$

def main_function_example():
	#{
		#declare a, b, c
		b = 4;
		c = 3;
		a = b + c;
		
		#$ return result #$$$
		return(a);
	#}

if __name__ == "__main__":
   main_function_example();