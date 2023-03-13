#$ Tests for CutePy #$


def main1function():
	#{

		#declare x
		x = int(input());
		y = x + 5;
		print(y);

	#}

#############################################################
# line 4 : error main function name
#############################################################



def main_function_ex():
	#{
		#declare x,y
		x = int(input());
		y = 15;
		while[x < y]:
		#{
			y= y+1;
		#}

		print(y);
	#}

#############################################################
# line 25 : error "[" "]" are used for logical expressions
#############################################################


def 1main_function():
	#{
		# declare a, b, c
		b = 4;
		c = 3;
		a = b + c;
		
		#$ return result #$
		return(a);
	#}

##############################################################
# line 38 : error number "1" before main function name
##############################################################


def main_function_example():
	#{
		# declare a, b, c
		b = 4;
		c = 3;
		a = b + c;
		
		#$$$ return result #$
		return(a);
	#}

##############################################################
# line 61 : error comment
##############################################################


def main_func():
	#{
		#declre x,y
		x = int(input());
		y = int(input());
		if((x == 1) and (y != 5)):
			return(1);
		else:
			return(x);
	#}

##############################################################
# line 75 : error "[" and "]" are used for logical expressions
##############################################################


def main_f():
	#{
		#declare x
		x = 5;

		def func(x):
			#{
				#declare y;
				y = 0;

				while (x>y):
				#{
					x = x - 1;
					func(x);
				#}
			#}
	#}

###############################################################
# auto ua prepei na to pernaei, mporoume na valoume na kanei 
# anadromh th main gia na doume an petaei sfalma /
# na valoume parametrous sth main
###############################################################




def main_main():
	#{
		#$ declarations #$
		#declare x1, x2
		#declare x3

		x1 = int(input());
		x2 = int(input());
		x3 = 3;

		#$ local functions #$

		def func1(x1, x2):
			#{
				#$ boolterm conditions #$
				if(not [x1 >= x2] and [x1 != x2]):
					return (x1);
				else:
					return (x2);
			#}



		def func2(x1, x2, x3):
			#{
				#$ declarations #$
				#declare i

				i = func1(x1,x2);
				while(i <= 0):
					#{
						print(i);
					#}
			#}
	#}

##############################################################
# prepei na to pernaei kanonika 
##############################################################