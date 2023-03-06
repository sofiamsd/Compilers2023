import argparse
from string import ascii_letters, digits, whitespace

identifier_characters = ascii_letters + "_" + digits

symbols = '+-*/<>=;,:[](){}#$"!'

add_chars = "+-"
mul_chars = "*/"
rel_chars = "<>=!"
assignment_chars = "=",
delimiter_chars = ";,:"
grouping_chars = "[](){}#"
comment_chars = "#$"

EOF = "~"
EOL = " "

class cpyCharacter(str):
    @classmethod
    def construct_if_legal_else_raise(cls, char, callable_error_handler):
        char = cls(char)
        if not char.is_legal(): 
            callable_error_handler()
        return char

    def can_be_used_in_identifiers(self):
        return self in identifier_characters
    
    def can_be_used_in_keywords(self):
        return self in ascii_letters + '_#"'
        
    def is_addOperator(self): return self in add_chars

    def is_mulOperator(self): return self in mul_chars

    def is_relOperator(self): return self in rel_chars

    def is_assignmentSymbol(self): return self in assignment_chars

    def is_delimiterSymbol(self): return self in delimiter_chars

    def is_groupingSymbol(self): return self in grouping_chars

    def is_commentSymbol(self): return self in comment_chars

    def is_hashtag(self): return self == "#"

    def is_quote(self): return self == '"'

    def is_dollar(self): return self == "$"

    def is_EOF(self): return self == EOF

    def is_legal(self):
        return self in identifier_characters + symbols + whitespace
    
EOF = cpyCharacter(EOF)
EOL = cpyCharacter(EOL)

keywords = [
    IF:="if", 
    ELSE:="else", 
    WHILE:="while",
    RETURN:="return",
    PRINT:="print", 
    INT:="int",
    INPUT:="input", 
    DEF:="def", 
    DECLARE:="#declare", 
    __NAME__:="__name__",
    __MAIN__:='"__main__"'
]

def is_keyword(string): return string in keywords

logical_operators = [
    NOT:="not", 
    OR:="or",
    AND:="and"
]

keywords.extend(logical_operators)

def is_logOperator(string): return string in logical_operators

token_families = [
    NUM:="number",
    ID:="identifier",
    KEYWORD:="keyword",
    ADD_OP:="addOperator",
    MUL_OP:="mulOperator",
    REL_OP:="relOperator"
]

class Token:
    def __init__(self, recognized_string, family, line_number, column_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number
        self.column_number = column_number
        self.validate()

    def validate(self): pass

    def first_letter(self): return self.recognized_string[0]

    def length(self): return len(self.recognized_string)

    def to_grammar_symbol(self): return self.family

    def is_EOFToken(self): return False

class NumberToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, NUM, line_number, column_number)
        
    def validate(self):
        num = int(self.recognized_string)
        if abs(num) >= 2**32:
            OutOfBoundsNumber.at(self.line_number, self.column_number, number=num)

class IdentifierToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, ID, line_number, column_number)

    def validate(self):
        if is_keyword(self.recognized_string):
            IllegalIdentifierSameAsKeywordError.at(self.line_number, self.column_number, self.length(), id=self.recognized_string)
        
        if not self.first_letter().isalpha():
            IllegalIdentifierError.at(self.line_number, self.column_number, self.length(), id=self.recognized_string)

        if len(self.recognized_string) > 30:
            IdentifierExceeding30CharsError.at(self.line_number, self.column_number, self.length(), id=self.recognized_string)

    def is_main_function(self):
        return "main_" == self.recognized_string[:5]

class KeywordToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, KEYWORD, line_number, column_number)

    def validate(self):
        if not is_keyword(self.recognized_string):
            if self.first_letter() == "#":
                IllegalHashtagUsageError.at(self.line_number, self.column_number, self.length())
            if self.first_letter() == '"':
                IllegalQuoteUsageError.at(self.line_number, self.column_number, self.length())

            NotAKeywordError.at(self.line_number, self.column_number, self.length())

    def to_grammar_symbol(self): return self.recognized_string

class AssignmentToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__("=", "assignment", line_number, column_number)
    
    def to_grammar_symbol(self): return self.recognized_string

class DelimiterToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "delimiter", line_number, column_number)

    def validate(self):
        if self.recognized_string.is_delimiterSymbol(): return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")
    
    def to_grammar_symbol(self): return self.recognized_string

class AddOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, ADD_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string.is_addOperator(): return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

class MulOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, MUL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["*", "//"]: return
        if "/" in self.recognized_string:
            SingleDashOperatorError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

class LogOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "logOperator", line_number, column_number)

    def validate(self):
        if is_logOperator(self.recognized_string): return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def to_grammar_symbol(self): return self.recognized_string

class RelOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, REL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["<", ">", "!=", "<=", ">=", "=="]: return
        if "!" in self.recognized_string:
            IllegalExclamationMarkUsageError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")
        
class GroupingSymbolToken(Token):
    def __init__(self, recognized_string, line_number, column_number):  
        super().__init__(recognized_string, "groupingSymbol", line_number, column_number)

    def validate(self):
        if self.recognized_string in ["(",")","[","]"]: return

        if self.recognized_string not in ["#{", "#}"]:
            if "#" in self.recognized_string:
                IllegalHashtagUsageError.at(self.line_number, self.column_number, self.length())
            if "{" in self.recognized_string or "}" in self.recognized_string:
                IllegalBraceUsageError.at(self.line_number, self.column_number, self.length())


    def to_grammar_symbol(self): return self.recognized_string

class EOFToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__(EOF, "__internal__", line_number, column_number)

    def is_EOFToken(self): return True


################################## lexical analyzer ##########################################

class LexicalAnalyzer:

    def __init__(self, lines):
        self.line_number = 0
        self.column_number = 0
        self.lines = lines

    def is_end_of_file_reached(self):
        return self.line_number >= len(self.lines) 

    def is_end_of_line_reached(self, offset=0):
        return self.column_number+offset >= len(self.current_line())

    def current_line(self):
        if self.is_end_of_file_reached(): return EOF
        return self.lines[self.line_number]

    def change_column(self):
        if self.is_end_of_file_reached(): return
        self.column_number += 1
        if self.is_end_of_line_reached():
            self.line_number += 1
            self.column_number = 0

    def reset_position(self, line, column):
        self.line_number = line
        self.column_number = column

    def peek_next_character(self, offset=0):
        if self.is_end_of_file_reached(): return EOF
        if self.is_end_of_line_reached(offset): return EOL

        column = self.column_number + offset
        next_char = self.current_line()[column]
        
        return cpyCharacter.construct_if_legal_else_raise(
            next_char,
            callable_error_handler=lambda : IllegalCharacterError.at(self.line_number, column, char=next_char)
        )
        
    def get_next_character(self):
        next_character = self.peek_next_character()
        self.change_column()
        return next_character
    
    def consume_next_character(self):
        self.change_column()
    
    def skip_whitespace(self):
        while not self.is_end_of_file_reached():
            next_char = self.peek_next_character()
            if next_char.isspace():
                self.consume_next_character()
            else:
                break

    def skip_comment(self):
        if self.peek_next_character(0) == "#":
            if self.peek_next_character(1) != "$":
                return
            # print("comments on", self.line_number, self.column_number)
            line = self.line_number
            column = self.column_number
            self.consume_next_character()
            self.consume_next_character()

            while not self.is_end_of_file_reached():
                char = self.get_next_character()
                if char == "#":
                    char = self.get_next_character()
                    if char == "$":
                        # print("comments off", self.line_number, self.column_number-1)
                        return
            
            CommentError.at(line, column)

    
    def get_next_token(self):
        """
        Returns the next recognized token or detects an error and exits.
        Before calling it, there should be a check if the end of the file 
        has been reached.
        """
        line = self.line_number
        column = self.column_number

        while not self.is_end_of_line_reached():
            self.skip_whitespace()
            self.skip_comment()
            if line != self.line_number or column != self.column_number:
                line = self.line_number
                column = self.column_number
            else:
                break

        char = self.peek_next_character()

        if char.is_EOF():
            return EOFToken(line, column)

        if char.isdigit():
            return self.process_token_starting_with_digit()
        
        if char.can_be_used_in_identifiers():
            return self.process_token_starting_with_letter()
        
        if char.is_hashtag():
            return self.process_token_starting_hashtag()
        
        if char.is_quote():
            return self.process_token_starting_quote()

        if char.is_delimiterSymbol():
            self.consume_next_character()
            return DelimiterToken(char, line, column)
        
        if char.is_groupingSymbol():
            self.consume_next_character()
            return GroupingSymbolToken(char, line, column)

        if char.is_addOperator():
            self.consume_next_character()
            return AddOperatorToken(char, line, column)
        
        if char.is_mulOperator():
            return self.process_token_starting_mulOperator()
            
        if char.is_relOperator():
            return self.process_token_starting_relOperator()
        
        if char.is_dollar():
            IllegalDollarSignUsageError.at(line, column)
    
    def process_token_starting_with_digit(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()
            
            if next_char.isdigit():
                recognized_string += self.get_next_character()
            elif next_char.can_be_used_in_identifiers():
                # this will raise an IllegalIdentifierStartsWithDigitError
                self.reset_position(starts_at_line, starts_at_column)
                self.process_token_starting_with_letter()
            else:
                return NumberToken(recognized_string, starts_at_line, starts_at_column)
            

    def process_token_starting_with_letter(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()

            if next_char.can_be_used_in_identifiers():
                recognized_string += self.get_next_character()
            else:
                if is_logOperator(recognized_string):
                    return LogOperatorToken(recognized_string, starts_at_line, starts_at_column)
                elif is_keyword(recognized_string):
                    return KeywordToken(recognized_string, starts_at_line, starts_at_column)
                else:
                    return IdentifierToken(recognized_string, starts_at_line, starts_at_column)
    
    def process_token_starting_hashtag(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()

            if next_char.can_be_used_in_identifiers():
                recognized_string += self.get_next_character()
            else:
                if is_keyword(recognized_string):
                    return KeywordToken(recognized_string, starts_at_line, starts_at_column)
                elif next_char in ["{", "}"]:
                    recognized_string += self.get_next_character()
                    return GroupingSymbolToken(recognized_string, starts_at_line, starts_at_column)
                else:
                    return KeywordToken(recognized_string, starts_at_line, starts_at_column)
                
    def process_token_starting_quote(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()

            if next_char.can_be_used_in_keywords():
                recognized_string += self.get_next_character()
            else:
                return KeywordToken(recognized_string, starts_at_line, starts_at_column)
    
    def process_token_starting_mulOperator(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        if recognized_string == "*":
            return MulOperatorToken(recognized_string, starts_at_line, starts_at_column)
        else:
            next_char = self.get_next_character()
            return MulOperatorToken("/" + next_char, starts_at_line, starts_at_column)
            
    
    def process_token_starting_relOperator(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        next_char = self.peek_next_character()

        if recognized_string.is_assignmentSymbol():
            if next_char.is_assignmentSymbol():
                self.consume_next_character()
                return RelOperatorToken("==", starts_at_line, starts_at_column)
            else:
                return AssignmentToken(starts_at_line, starts_at_column)

        if next_char == "=":
            recognized_string += self.get_next_character()
        
        return RelOperatorToken(recognized_string, starts_at_line, starts_at_column)
        

SYMBOLS = [
    LPAR:="(",
    RPAR:=")",
    LSQBR:="[",
    RSQBR:="]",
    LCDBLK:="#{",
    RCDBLK:="#}",
    COM:=",",
    COL:=":",
    SCOL:=";",
    EQLS:="="
]


        
#################################### syntax analyzer #########################################
# Parser : klash pou antlei lektikes monades apo ton lektiko analyth (Lex)

class Parser:
    def __init__(self, lexical_analyzer):
        self.lexical_analyzer = lexical_analyzer
        self.lines = self.lexical_analyzer.lines

    def peek_token(self):#handle EOFError?
        try:
            return self.look_ahead_token
        except AttributeError:
            self.look_ahead_token = self.lexical_analyzer.get_next_token()
            return self.look_ahead_token
    
    def get_token(self):#handle EOFError?
        next_token = self.look_ahead_token
        self.look_ahead_token = self.lexical_analyzer.get_next_token()
        return next_token
    
    def syntax_analyzer(self):
        global token
        token = self.get_token()
        self.startRule()
        print('Compilation completed successfully') #replace print with uniform print
        

    def startRule(self):
        self.def_main_part()
        self.call_main_part()

    #todo this
    def def_main_part(self):
        while True:
            self.def_main_function()
            if ...:
                break
    

    def def_main_function(self):
        global token
        if(token.recognized_string == 'def'):
            token = self.get_token()

            if(token.family == ID):
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
                                #todo ???
                                while ...:
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

            if(token.family == ID):
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

                                # introduce body ???
                                self.declarations()
                                # todo this, kleen star
                                while ...:
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
        #kleen star
        while ...:
            self.declaration_line()

    def declaration_line(self):
        global token
        # while(token.recognized_string == '#declare'):
        if (token.recognized_string == '#declare'):
            token = self.get_token()
            self.id_list()
        else:
            self.error("TODO!!!")

    def statement(self):
        if ...:
            self.simple_statement()
        elif ...:
            self.structured_statement()

    def statements(self):
        #at least one; +
        while ...:
            self.statement()

    def simple_statement(self):
        if ...:
            self.assingmet_stat()
        elif ...:
            self.print_stat()
        elif ...:
            self.return_stat()

    def structured_statement(self):
        if ...:
            self.if_stat()
        elif ...:
            self.while_stat()

    def assignmet_stat(self):
        global token
        if(token.family == ID):
            token = self.get_token()

            if(token.recognized_string == "="):
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
                            # this is wrong
                            # it is optional
                            self.else_part()
                    else:
                        self.error('Expected ":" after if condition.')
                else:
                    self.error('Expected ")".')
            else:
                self.error('Expected "(" after keyword "if".')
        else:
            self.error('Expected "if" keyword.')

    #introduce if statement body

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
        if(token.family == ID):
            token = self.get_token()
            while(token.recognized_string == ','):
                token = self.get_token()
                if(token.family == ID):
                    token = self.get_token()
                else:
                    self.error('Expected ID but argument was type of: ' + token.family)
        else:
            self.error('Expected ID but argument was type of: ' + token.family)


    def expression(self):
        self.optional_sign()
        self.term()
        # klein star
        while ...:
            self.ADD_OP()
            self.term()

    def term(self):
        self.factor()
        #klein star
        while ...:
            self.MUP_OP()
            self.factor()

    def factor(self):
        global token
        if(token.recognized_string == NUM):
            token = self.get_token()
        elif(token.family == ID):
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
        #correct this
        self.ADD_OP()

    def condition(self):
        global token
        #is equivelant?
        if(token.recognized_string == 'or'):
            token = self.get_token()
            self.bool_term()
        else:
            self.bool_term()


    def bool_term(self):
        global token
        #is equivelant?
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
            self.REL_OP() #??? 
            self.expression()


    def call_main_part(self):
        global token
        if(token.recognized_string == 'if'):
            token = self.get_token()
            if(token.recognized_string == '__name__'):
                token = self.get_token()
                if(token.recognized_string == '=='):
                    token = self.get_token()
                    if(token.recognized_string == '"__main__"'):
                        token = self.get_token()
                        if(token.recognized_string == ':'):
                            token = self.get_token()
                            # plus; one or more times
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




        


########################################### Errors ###########################################

class Error:
    def __init__(self, *messages, token_length=1):
        self.ident = "   "
        self.message = ("\n"+self.ident).join(messages)
        self.default_token_length = token_length

    def format_message(self, **kwds):
        try:
            return self.message.format(**kwds)
        except KeyError as e:
            arg = e.args[0]
            raise TypeError(f"at() missing required keyword-only argument: '{arg}'")
        except IndexError:
            pass
        except ValueError:
            pass
        raise TypeError(
            "the error message is not formed properly. \nPositional arguments are not allowed. \nWhen braces are used, they must be escaped like this: {{, }}"
        )

    def at(self, line_number, column_number, token_length=None, **additional_args):
        position = f"line {line_number+1}, column {column_number+1}"
        message = self.format_message(position=position, **additional_args)
        
        global lines
        offending_line = lines[line_number]

        print(f"Error:\n" + self.ident + message)
        
        if token_length is None:
            token_length = self.default_token_length
        
        print()
        print(offending_line)
        print(f"{' '*column_number}{'^'*token_length}")

        exit()

CommentError = Error(
    "The end of the file was reached even though a comment was not closed.",
    "The offending comment was found at {position}",
    token_length=2
)
IdentifierExceeding30CharsError = Error(
    "A identifier with more than 30 characters was found at {position}"
)
IllegalCharacterError = Error(
    "The illegal character '{char}' was found at {position}.",
    "The only legal characters are:",
    r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789#"+-*/<>!=;,:[](){{}}#$" \t\r\n',
    token_length=1
)
IllegalIdentifierError = Error(
    "The illegal identifier '{id}' was found at {position}.",
    "An identifier must start with a letter and it can only use alphanumeric characters and underscores"
)
IllegalIdentifierSameAsKeywordError = Error(
    "The illegal identifier '{id}' was found at {position}.",
    "It has the same name with the keyword {keyword}"
)
IllegalIdentifierStartsWithDigitError = Error(
    "The illegal identifier '{id}' was found at {position}.",
    "An identifier must start with a letter; not a number",
)
IllegalBraceUsageError = Error(
    "A misspelled block declaration or an illegal usage of a brace was found at {position}.",
    "The only valid uses of '{{', '}}' are in: #{{, #}}"
)
IllegalDollarSignUsageError = Error(
    "A misspelled comment delimiter or an illegal usage of a dollar sign was found at {position}.",
    "The only valid use of '$' is in: #$"
)
IllegalExclamationMarkUsageError = Error(
    "A misspelled inequality symbol or an illegal usage of an exclamation mark was found at {position}.",
    "The only valid use of '!' is in: !="
)
IllegalHashtagUsageError = Error(
    "A misspelled variable declaration, block declaration or comment delimiter was found at {position}.",
    "The only valid uses of '#' are in: #declare, #{{, #}} and #$.",
    "An identifier must start with a letter and it can only use alphanumeric characters and underscores"
)
IllegalQuoteUsageError = Error(
    "A misspelled keyword or an illegal identifier was found at {position}.",
    'The only valid use of \'"\' is in the keyword "__main__".',
    "An identifier must start with a letter and it can only use alphanumeric characters and underscores"
)
NotAKeywordError = Error(
    "A misspelled keyword or an illegal identifier was found at {position}.",
    "An identifier must start with a letter and it can only use alphanumeric characters and underscores"
)
OutOfBoundsNumber = Error(
    "The number {number} was found at {position}. It has an sabsolute value greater than 2**32"
)
SingleDashOperatorError = Error(
    "The division operator is '//', a single '/' was found at {position}",
    token_length=1
)
SyntaxError = Error("A syntax error occured at {position}")




def main(argv):
    file_name = argv[1]
    global lines

    with open(file_name, 'r') as file:
        lines = []
        for line in file:
            lines.append(line.replace("\n", EOL))

    lex = LexicalAnalyzer(lines)
    print(lex.lines)
    while not lex.is_end_of_file_reached():
        token: Token = lex.get_next_token()
        print(f"{token.recognized_string}, family: {token.family}, line: {token.line_number+1}, column: {token.column_number+1}")

    par = Parser(lex)



#todo customize this
# cmdline = argparse.ArgumentParser(
#                     prog = 'ProgramName',
#                     description = 'What the program does',
#                     epilog = 'Text at the bottom of help'
# )

# cmdline.add_argument('filename')           # positional argument
# cmdline.add_argument('-c', '--count')      # option that takes a value
# cmdline.add_argument('-v', '--verbose',action='store_true')
# args = cmdline.parse_args()
# print(args.filename, args.count, args.verbose)



if __name__ == "__main__":
    global lines
    
    import sys #remove this
    main(sys.argv)