import os
import sys

################################### syntax analyzer #########################################
# Parser : klash pou antlei lektikes monades apo ton lektiko analyth (Lex)

class Parser:

	def __init__(self, lexical_analyzer):
		self.lexical_analyzer = lexical_analyzer

	def syntax_analyzer(self):
		global token
		token = self.get_token()
		self.startRule()
		print('Compilation completed successfully')

	def get_token(self):
		return self.lexical_analyzer.next_token()


	# startRule
	#	:	def_main_part
	#		call_main_part
	#	;

	def startRule(self):
		self.def_main_part()
		self.call_main_part()

	def def_main_part(self):
		self.def_main_function()


	def def_main_function(self):
		global token
		if(token.recognized_string == 'def'):
			token = self.get_token()

			if(token.family == 'ID'):
				token = self.get_token()

				if(token.recognized_string == '('):
					token = self.get_token()

					if(token.recognized_string == ')'):
						token = self.get_token()

						if(token.recognized_string == ':'):
							token = self.get_token()

							if(token.recognized_string == '#{'):
								token = self.get_token()

								self.declarations()
								self.def_function()
								self.statements()

								if(token.recognized_string == '#}'):
									return
								else:
									self.error('Expected "#}" at the end of main function block.')
							else:
								self.error('Expected "#{" at the start of main function block.')
						else:
							self.error('Expected ":" before main function block.')
					else:
						self.error('Expected ")".')
				else:
					self.error('Expected "(".')
			else:
				self.error('Expected main function name.')
		else:
			self.error('Expected main function declaration.')


	def def_function(self):
		global token
		if(token.recognized_string == 'def'):
			token = self.get_token()

			if(token.family == 'ID'):
				token = self.get_token()

				if(token.recognized_string == '('):
					token = self.get_token()
					self.id_list()

					if(token.recognized_string == ')'):
						token = self.get_token()

						if(token.recognized_string == ':'):
							token = self.get_token()

							if(token.recognized_string == '#{'):
								token = self.get_token()

								self.declarations()
								self.def_function()
								self.statements()

								if(token.recognized_string == '#}'):
									return
								else:
									self.error('Expected "#}" at the end of function block.')
							else:
								self.error('Expected "#{" at the start of function block.')
						else:
							self.error('Expected ":" before function block.')
					else:
						self.error('Expected ")".')
				else:
					self.error('Expected "(".')
			else:
				self.error('Expected function name.')
		else:
			self.error('Expected function declaration.')


	def declarations(self):
		self.declaration_line()

	def declaration_line(self):
		global token
		while(token.recognized_string == '#declare'):
			token = self.get_token()
			self.id_list()

	def statement(self):
		self.simple_statement()
		self.structured_statement()

	def statements(self):
		self.statement()

	def simple_statement(self):
		self.assingmet_stat()
		self.print_stat()
		self.return_stat()

	def structured_statement(self):
		self.if_stat()
		self.while_stat()

	def assingmet_stat(self):
		global token
		if(token.family == 'ID'):
			token = self.get_token()

			if(token.recognized_string == assingment):
				token = self.get_token()

				if(token.recognized_string == 'int'):
					token = self.get_token()
					if(token.recognized_string == '('):
						token = self.get_token()
						if(token.recognized_string == 'input'):
							token = self.get_token()
							if(token.recognized_string == '('):
								token = self.get_token()
								if(token.recognized_string == ')'):
									token = self.get_token()
									if(token.recognized_string == ')'):
										token = self.get_token()
										if(token.recognized_string == ';'):
											token = self.get_token()
										else:
											self.error('Expected ";" at the end of input.')
									else:
										self.error('Expected ")".')
								else:
									self.error('Expected ")".')
							else:
								self.error('Expected "(" after input.')
						else:
							self.error('Expected keyword "input".')
					else:
						self.error('Expected "(" after "int".')

				else:
					self.expression()
					if(token.recognized_string == ';'):
						token = self.get_token()
					else:
						self.error('Expected ";" after expression.')

			else:
				self.error('Expected "=" after variable name.')

		else:
			self.error('Expected variable name for assignment.')



	def print_stat(self):
		global token
		if(token.recognized_string == 'print'):
			token = self.get_token()

			if(token.recognized_string == '('):
				token = self.get_token()
				self.expression()
				if(token.recognized_string == ')'):
					token = self.get_token()
					if(token.recognized_string == ';'):
						token = self.get_token()
					else:
						self.error('Expected ";" at the end of print statement')
				else:
					self.error('Expected ")".')
			else:
				self.error('Expected "(".')

		else:
			self.error('Expected keyword "print".')


	def return_stat(self):
		global token
		if(token.recognized_string == 'return'):
			token = self.get_token()

			if(token.recognized_string == '('):
				token = self.get_token()
				self.expression()
				if(token.recognized_string == ')'):
					token = self.get_token()
					if(token.recognized_string == ';'):
						token = self.get_token()
					else:
						self.error('Expected ";" at the end of return statement')
				else:
					self.error('Expected ")".')
			else:
				self.error('Expected "(".')

		else:
			self.error('Expected keyword "return".')


	def if_stat(self):
		global token
		if(token.recognized_string == 'if'):
			token = self.get_token()
			if(token.recognized_string == '('):
				token = self.get_token()
				self.condition()
				if(token.recognized_string == ')'):
					token = self.get_token()
					if(token.recognized_string == ':'):
						token = self.get_token()

						if(token.recognized_string == '#{'):
							token = self.get_token()
							self.statements()
							if(token.recognized_string == '#}'):
								token = self.get_token()
								self.else_part()
							else:
								self.error('Expected "#}" at the end of block.')
						else:
							self.statement()
							self.else_part()
					else:
						self.error('Expected ":" after if condition.')
				else:
					self.error('Expected ")".')
			else:
				self.error('Expected "(" after keyword "if".')
		else:
			self.error('Expected "if" keyword.')



	def else_part(self):
		global token
		if(token.recognized_string == 'else'):
			token = self.get_token()
			if(token.recognized_string == ':'):
				token = self.get_token()
				if(token.recognized_string == '#{'):
					token = self.get_token()
					self.statements()
					if(token.recognized_string == '#}'):
						token = self.get_token()
					else:
						self.error('Expected "#}" after statents.')
				else:
					self.statement()
			else:
				self.error('Expected ":" after "else" keyword.')
		else:
			self.error('Expected "else" keyword.')

	def while_stat(self):
		global token
		if(token.recognized_string == 'while'):
			token = self.get_token()
			if(token.recognized_string == '('):
				token = self.get_token()
				self.condition()
				if(token.recognized_string == ')'):
					token = self.get_token()
					if(token.recognized_string == ':'):
						token = self.get_token()

						if(token.recognized_string == '#{'):
							token = self.get_token()
							self.statements()
							if(token.recognized_string == '#}'):
								token = self.get_token()
							else:
								self.error('Expected "#}" at the end of block.')
						else:
							self.statement()
					else:
						self.error('Expected ":" after while condition.')
				else:
					self.error('Expected ")" after condition.')
			else:
				self.error('Expected "(".')
		else:
			self.error('Expected "while" keyword.')


	def id_list(self):
		global token
		if(token.family == 'ID'):
			token = self.get_token()
			while(token.recognized_string == ','):
				token = self.get_token()
				if(token.family == 'ID'):
					token = self.get_token()
				else:
					self.error('Expected ID but argument was type of: ' + token.family)
		else:
			self.error('Expected ID but argument was type of: ' + token.family)


	def expression(self):
		self.optional_sign()
		self.term()
		self.ADD_OP()
		self.term()

	def term(self):
		self.factor()
		self.MUP_OP()
		self.factor()

	def factor(self):
		global token
		if(token.recognized_string == 'INTEGER'):
			token = self.get_token()
		elif(token.family == 'ID'):
			token = self.get_token()
			self.idtail()
		elif(token.recognized_string == '('):
			token = self.get_token()
			self.expression()
			if(token.recognized_string == ')'):
				token = self.get_token()
			else:
				self.error('Expected ")".')
		else:
			self.error('Invalid prompt.')


	def idtail(self):
		global token
		if(token.recognized_string == '('):
			token = self.get_token()
			self.actual_par_list()
			if(token.recognized_string == ')'):
				token = self.get_token()
			else:
				self.error('Expected ")" at the end.')
		else:
			self.error('Expected "(".')


	def actual_par_list(self):
		global token
		self.expression()
		while(token.recognized_string == ','):
			token = self.get_token()
			self.expression()


	def optional_sign(self):
		self.ADD_OP()

	def condition(self):
		global token
		if(token.recognized_string == 'or'):
			token = self.get_token()
			self.bool_term()
		else:
			self.bool_term()


	def bool_term(self):
		global token
		if(token.recognized_string == 'and'):
			token = self.get_token()
			self.bool_factor()
		else:
			self.bool_factor()


	def bool_factor(self):
		global token
		if(token.recognized_string == 'not'):
			token = self.get_token()
			if(token.recognized_string == '['):
				token = self.get_token()
				self.condition()
				if(token.recognized_string == ']'):
					token = self.get_token()
				else:
					self.error('Expected "]" after condition.')
			else:
				self.error('Expected "[" after logical operator "not".')
		elif(token.recognized_string == '['):
			token = self.get_token()
			self.condition()
			if(token.recognized_string == ']'):
				token = self.get_token()
			else:
				self.error('Expected "]" after condition.')
		else:
			self.expression()
			self.REL_OP()
			self.expression()


	def call_main_part(self):
		global token
		if(token.recognized_string == 'if'):
			token = self.get_token()
			if(token.recognized_string == '__name__'):
				token = self.get_token()
				if(token.recognized_string == '=='):
					token = self.get_token()
					if(token.recognized_string == '__main__'):
						token = self.get_token()
						if(token.recognized_string == ':'):
							token = self.get_token()
							self.main_function_call()
						else:
							self.error('Expected ":" after "__main__" keyword.')
					else:
						self.error('Expected "__main__" keyword.')
				else:
					self.error('Expected "==".')
			else:
				self.error('Expected "__name__" keyword.')
		else:
			self.error('Expected "if" keyword.')


	def main_function_call(self):
		global token
		if(token.family == 'ID'):
			token = self.get_token()
			if(token.recognized_string == '('):
				token = self.get_token()
				if(token.recognized_string == ')'):
					token = self.get_token()
					if(token.recognized_string == ';'):
						token = self.get_token()
					else:
						self.error('Expected ";" at the end of function call.')
				else:
					self.error('Expected ")".')
			else:
				self.error('Expected "(" after function name.')
		else:
			self.error('Expected main function name.')






################################## lexical analyzer ###########################################
class Lex:
	def __init__(self,current_line, file_name, token):
		self.current_line = current_line
		self.family = file_name
		self.token = token

	def __str__(self, tk):
		print(tk.recognized_string + ' family: ' + tk.family + ' line: ' + str(tk.line_number))


	def error(self,str):
		print('-------------------------------------------')
		print('ERROR was found in line: ',self.current_line)
		print(str)
		print('-------------------------------------------')
		exit()#to programma kanei exit efoson vroume to 1o error


	def next_token(self):
		global c

		sym = '_'
		add_Operators = ['+', '-']
		mul_Operators = ['*', '//']
		assingment = '='
		rel_Operators = ['<', '>', '==', '<=', '>=']
		delimiters = [';', ',', ':']
		groupingSymbols = ['[', ']', '(', ')', '{', '}']
		comment = '#$'
		logical_Operators = ['and', 'or', 'not']
		keywords = ['def', 'if', 'else', 'while', 'return', 'print', 'int', 'input', '__main__']
		declaration = '#declare'

		self.token.recognized_string = ''
		c = ''
		id_counter = 0		# to check if token size > 30

		c = file.read(1)

		while(c.isspace()):		# for whitespaces
			if(c == '\n'):
				self.token.line_number += 1
				self.current_line +=1

			c = file.read(1)

		while(c == '#'):
			id_counter += 1
			self.token.recognized_string += c 	# append to create word/token

			c = file.read(1)
			while(c.isalpha()):
				self.token.recognized_string += c
				c = file.read(1)
				id_counter += 1

				if(self.token.recognized_string == declaration):
					file.seek(file.tell()-1)
					self.token.family = 'declaration_line'
					self.__str__(self.token)
					return self.token

			if(c == '{'):
				self.token.recognized_string += c
				self.token.family = 'functionBlock'
				self.__str__(self.token)
				return self.token

			'''
			elif(c == '$'):
				self.token.recognized_string += c
				self.token.family = 'comment'
				self.__str__(self.token)
				return self.token

				c = file.read(1)
				while(c.isalpha() or c.is_digit()):
					self.token.recognized_string += c
					c = file.read(1)
				if(c == comment):
					return
			'''




		if(c.isalpha()): 	# for ascii_letters
			id_counter += 1
			self.token.recognized_string += c 	# append to create word/token

			c = file.read(1)
			while(c.isalpha() or c.isdigit() or c == sym):
				self.token.recognized_string += c
				c = file.read(1)
				id_counter += 1

			if(id_counter > 30):
				self.error('Identifier exceeds maxinum length (30).')
			else:
				if(self.token.recognized_string in keywords):
					file.seek(file.tell()-1)
					self.token.family = 'keyword'
					self.__str__(self.token)
					return self.token
				elif(self.token.recognized_string in logical_Operators):
					file.seek(file.tell()-1)
					self.token.family = 'logical_Operator'
					self.__str__(self.token)
					return self.token
				else:
					file.seek(file.tell() - 1)
					self.token.family = 'ID'
					self.__str__(self.token)
					return self.token

		elif(c.isdigit()): 		# for digits
			self.token.recognized_string += c

			c = file.read(1)
			while(c.is_digit()):
				self.token.recognized_string += c
				c = file.read(1)

			if(c.isalpha()):
				self.error('INTEGERS cannot be followed by letters')
			else:
				if(self.isEOF()):
					return self.token

				file.seek(file.tell() - 1)
				self.token.family = 'INTEGER'
				self.__str__(self.token)
				return self.token



		elif(c == '>'):
			self.token.recognized_string += c

			c = file.read(1)
			if(c == '='):

				self.token.recognized_string += c
				self.token.family = 'rel_Operator'
				self.__str__(self.token)
				return self.token

			else:
				file.seek(file.tell() - 1)
				self.token.family = 'rel_Operator'
				self.__str__(self.token)
				return self.token



		elif(c == '<'):
			self.token.recognized_string += c

			c = file.read(1)
			if(c == '='):

				self.token.recognized_string += c
				self.token.family = 'rel_Operator'
				self.__str__(self.token)
				return self.token

			else:

				file.seek(file.tell() - 1)
				self.token.family = 'rel_Operator'
				self.__str__(self.token)
				return self.token


		elif(c == '='):
			self.token.recognized_string = c

			c = file.read(1)
			if(c == '='):
				self.token.recognized_string += c
				self.token.family = 'rel_Operator'
				self.__str__(self.token)
				return self.token
			else:
				# assignment
				self.token.family = 'assignmentmet'
				self.__str__(self.token)
				return self.token
				


		elif(c in add_Operators):
			self.token.recognized_string = c
			self.token.family = 'add_Operator'
			self.__str__(self.token)
			return self.token


		elif(c in mul_Operators):
			self.token.recognized_string = c
			self.token.family = 'mul_Operator'
			self.__str__(self.token)
			return self.token


		## groupSymbol
		elif(c in groupingSymbols):
			self.token.recognized_string = c
			self.token.family = 'groupingSymbol'
			self.__str__(self.token)
			return self.token

		## delimiter
		elif(c in delimiters):
			self.token.recognized_string = c
			self.token.family = 'delimiter'
			self.__str__(self.token)
			return self.token

			## is EOF
		elif(self.isEOF()):
			token.recognized_string = 'EOF'
			token.family = ''
			self.__str__(self.token)
			return self.token

		else:
			self.error('Invalid character ' + c + ' !')

	def isEOF(self):
		global is_eof
		if(file_len == file.tell()):#an o kersoras tou arxeiou ginei isos me to mege8os tou arxeio ftasame sto telos tou

			return 1
		else:
			return 0


		## comments
'''
		elif(c ==  '#'):
			self.token.recognized_string = c

			c = file.read(1)
			if(c == '$'):
				self.token.recognized_string += c
				self.token.family = 'comment'
				self.__str__(self.token)
				return self.token

				while(c != '#$'):
					c = file.read(1)
					print(c)
					if(file_len == file.tell()):	#isEOF
						self.error('End of file reached. Comment should be closed.')
				c = file.read(1)

			elif(c == '{'):
				self.token.recognized_string += c
				self.token.family = 'functionBlock'
				self.__str__(self.token)
				return self.token

			elif(c.isalpha()):
				if(c == 'd'):
					self.token.recognized_string += c
					self.token.family = 'declaration_line'
					self.__str__(self.token)
					return self.token
'''





class Token:
	def __init__(self, recognized_string, family, line_number):
		self.recognized_string = recognized_string
		self.family = family
		self.line_number = line_number


def main(argv):
	global file_len
	global file
	global lex
	file = open(sys.argv[1], "r")
	file_len = 0
	file_len = len(file.read())
	file.seek(0)
	#arxikopoihseiw twn object
	#1 -> token pou 8a diavazei o lex
	#2 -> lex pou 8a exei ta current lines kai 8a pernaei to token ston parser(suntaktiko analuth)
	#3 -> parser(suntaktikos analuths)
	token = Token('','',1)
	lex = Lex(1,file,token)

	par = Parser(lex)
	par.syntax_analyzer()




main(sys.argv[1])
