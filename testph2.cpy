#$ Moisiadou Sofia 4446 #$
#$ Tsiaousi Thomai 4510 #$
def main_func1():
#{
	#declare x,y
	#declare a,b

	def fun2(a,b):
	#{
		#declare c
		while(not [ a + b * a - b // 4 > 25]):
		#{
			a = a * a -12;
			b = 15 // a - b;
			c = b * a;
			return(c);
		#}
	#}

	x = int(input());
	y= int(input());

	if (y >= 10):
	#{
		x = 10 + y;
		print(x);
		print(y);
	#}
	else:
	#{
		while([x != 2] or [y < 5]):
		#{
			a = fun2(x, y);
			return (a);
		#}
	#}
#}


if __name__ == "__main__":
	#$ call of main functions #$
	main_func1();
