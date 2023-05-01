########################################### Phase 2 ###########################################
# Moisiadou Sofia AM:4446 cse84446 
# Tsiaousi Thomai AM:4510 cse84510
# How to run the code: python3 cutePy_4446_4510.py test.cpy
# Choose one of the given tests :grammar-test.cpy , testph2.cpy 
# You can also choose from the previous tests : 
# testError_comment.cpy, testError_brackets.cpy 
# ,testRecursion.cpy,testCountdown.cpy ,testCalculateGrade.cpy
###############################################################################################

from argparse import ArgumentParser, FileType
from collections import namedtuple
from contextlib import redirect_stdout
from string import ascii_letters, digits, whitespace
from sys import stdout, stderr


def print_to_stdout(text): print(f"--- {text}", file=stdout)
def print_to_stderr(text="\n"): print(text, file=stderr)

identifier_characters = ascii_letters + "_" + digits

symbols = '+-*/<>=;,:[](){}#$"!'

legal_characters = identifier_characters + symbols + whitespace


EOF = "~"
EOL = " "

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

keyword_characters = ascii_letters + '_#"'

def is_keyword(string): return string in keywords

logical_operators = [
    AND:="and",
    NOT:="not",
    OR:="or"
]

LPAR = "("
RPAR = ")"
LSQB = "["
RSQB = "]"
LBLCK = "#{"
RBLCK = "#}"

CLN = ":"
SMCLN = ";"
COM = ","

ASGN = "="

EQLS = "=="


add_chars = "+-"
mul_chars = "*/"
rel_chars = "<>=!"
assignment_chars = ASGN
delimiter_chars = CLN + SMCLN + COM 
grouping_chars = LPAR + RPAR + LSQB + RSQB + LBLCK + RBLCK 
comment_chars = "#$"


token_families = [
    NUM:="number",
    ID:="identifier",
    KEYWORD:="keyword",
    ADD_OP:="addOperator",
    MUL_OP:="mulOperator",
    REL_OP:="relOperator"
]





########################################### Errors ###########################################
### class Error : In this class we define the Errors that might appear during compilation. ###

class Error:
    def __init__(self, *messages, token_length=1):
        self.ident = "    "
        self.message = ("\n"+self.ident).join(messages)
        self.default_token_length = token_length

    def format_message(self, **kwds):
        try:
            return self.message.format(**kwds)
        except KeyError as e:
            arg = e.args[0]
            raise TypeError(f"at() missing required keyword-only argument: '{arg}'")
        except IndexError: pass
        except ValueError: pass
        raise TypeError(
            "the error message is not formed properly. \nPositional arguments are not allowed. \nWhen braces are used, they must be escaped like this: {{, }}"
        )

    def at(self, line_number, column_number, token_length=None, **additional_args):
        position = f"line {line_number+1}, column {column_number+1}"
        message = self.format_message(position=position, **additional_args)

        print_to_stderr(f"--- Error:\n" + self.ident + message)

        if token_length is None: token_length = self.default_token_length

        
        if token_length>0 and line_number<len(lines):
            print_to_stderr(f"\n--- Line {line_number+1}:")
            print_to_stderr(lines[line_number])
            print_to_stderr(f"{' '*column_number}{'^'*token_length}")
            print_to_stderr()

        exit(1)

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
OutOfBoundsNumberError = Error(
    "The number {number} was found at {position}. It has an absolute value greater than 2**32"
)
SingleDashOperatorError = Error(
    "The division operator is '//', a single '/' was found at {position}",
    token_length=1
)
SyntError = Error("A syntax error occurred at {position}. Expected '{expected_value}', but '{given_value}' was given instead")




### Recognize each token read from input cpy file and its family ###
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

    def does_it_match(self, *grammar_symbols): raise NotImplementedError
    
    def __repr__(self):
        return f"{self.recognized_string}, family: {self.family}, line: {self.line_number+1}, column: {self.column_number+1}"

class NumberToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, NUM, line_number, column_number)

    def validate(self):
        num = int(self.recognized_string)
        if abs(num) >= 2**32:
            OutOfBoundsNumberError.at(self.line_number, self.column_number, number=num)

    def does_it_match(self, *grammar_symbols): return self.family in grammar_symbols

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

    def does_it_match(self, *grammar_symbols): return self.family in grammar_symbols


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

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols

class AssignmentToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__(ASGN, "assignment", line_number, column_number)

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols

class DelimiterToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "delimiter", line_number, column_number)

    def validate(self):
        if self.recognized_string in delimiter_chars: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols

class AddOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, ADD_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in add_chars: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, *grammar_symbols): return self.family in grammar_symbols

class MulOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, MUL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["*", "//"]: return
        if "/" in self.recognized_string:
            SingleDashOperatorError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, *grammar_symbols): return self.family in grammar_symbols

class LogOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "logOperator", line_number, column_number)

    def validate(self):
        if self.recognized_string in logical_operators: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols

class RelOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, REL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["<", ">", "!=", "<=", ">=", "=="]: return
        if "!" in self.recognized_string:
            IllegalExclamationMarkUsageError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, *grammar_symbols): return self.family in grammar_symbols

    def is_eqls(self): return self.recognized_string == EQLS

class GroupingSymbolToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "groupingSymbol", line_number, column_number)

    def validate(self):
        if self.recognized_string in [LPAR,RPAR,LSQB,RSQB]: return

        if self.recognized_string not in [LBLCK, RBLCK]:
            if "#" in self.recognized_string:
                IllegalHashtagUsageError.at(self.line_number, self.column_number, self.length())
            if "{" in self.recognized_string or "}" in self.recognized_string:
                IllegalBraceUsageError.at(self.line_number, self.column_number, self.length())

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols

class EOFToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__(EOF, "__internal__", line_number, column_number)

    def does_it_match(self, *grammar_symbols): return self.recognized_string in grammar_symbols


################################## lexical analyzer ##########################################
### class LexicalAnalyzer : Reads tokens and returns the to SyntaxAnalyzer (Parser). ###
class LexicalAnalyzer:

    def __init__(self, lines):
        self.line_number = 0
        self.column_number = 0
        self.lines = lines

    def is_end_of_file_reached(self): return self.line_number >= len(self.lines)

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

    def change_position(self, line, column):
        self.line_number = line
        self.column_number = column

    def peek_next_character(self, offset=0, allow_illegal_chars=False):
        if self.is_end_of_file_reached(): return EOF
        if self.is_end_of_line_reached(offset): return EOL

        column = self.column_number + offset
        next_char = self.current_line()[column]

        if next_char not in legal_characters and not allow_illegal_chars:
            IllegalCharacterError.at(self.line_number, column, char=next_char)

        return next_char

    def get_next_character(self, allow_illegal_chars=False):
        next_character = self.peek_next_character(allow_illegal_chars=allow_illegal_chars)
        self.change_column()
        return next_character

    def consume_next_character(self): self.change_column()

    def skip_whitespace(self):
        while not self.is_end_of_file_reached():
            next_char = self.peek_next_character()
            if next_char.isspace(): self.consume_next_character()
            else: break

    def skip_comment(self):
        if self.peek_next_character(0) == "#":
            if self.peek_next_character(1) != "$": return

            line = self.line_number
            column = self.column_number
            self.consume_next_character()
            self.consume_next_character()

            while not self.is_end_of_file_reached():
                char = self.get_next_character(allow_illegal_chars=True)
                if char == "#":
                    char = self.get_next_character()
                    if char == "$": return

            CommentError.at(line, column)

    def get_next_token(self):

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

        if char == EOF: return EOFToken(line, column)
        if char.isdigit(): return self.process_token_starting_with_digit()
        if char in identifier_characters: return self.process_token_starting_with_letter()
        if char == "#": return self.process_token_starting_hashtag()
        if char == '"': return self.process_token_starting_quote()
        if char in delimiter_chars:
            self.consume_next_character()
            return DelimiterToken(char, line, column)
        if char in grouping_chars:
            self.consume_next_character()
            return GroupingSymbolToken(char, line, column)
        if char in add_chars:
            self.consume_next_character()
            return AddOperatorToken(char, line, column)
        if char in mul_chars: return self.process_token_starting_mulOperator()
        if char in rel_chars: return self.process_token_starting_relOperator()
        if char == "$": IllegalDollarSignUsageError.at(line, column)

    def process_token_starting_with_digit(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()

            if next_char.isdigit():
                recognized_string += self.get_next_character()
            elif next_char in identifier_characters:
                self.change_position(starts_at_line, starts_at_column)
                self.process_token_starting_with_letter() 
            else:
                return NumberToken(recognized_string, starts_at_line, starts_at_column)

    def process_token_starting_with_letter(self):
        starts_at_line = self.line_number
        starts_at_column = self.column_number
        recognized_string = self.get_next_character()

        while True:
            next_char = self.peek_next_character()

            if next_char in identifier_characters:
                recognized_string += self.get_next_character()
            else:
                if recognized_string in logical_operators:
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

            if next_char in identifier_characters:
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

            if next_char in keyword_characters:
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

        if recognized_string == ASGN:
            if next_char == ASGN:
                self.consume_next_character()
                return RelOperatorToken(EQLS, starts_at_line, starts_at_column)
            else:
                return AssignmentToken(starts_at_line, starts_at_column)

        if next_char == ASGN:
            recognized_string += self.get_next_character()

        return RelOperatorToken(recognized_string, starts_at_line, starts_at_column)

    def lexical_analyzer(self, print_results=False):
        while True:
            token = self.get_next_token()
            if token.recognized_string == EOF: break
            if print_results: print_to_stdout(token)

        if print_results: print_to_stdout("\n")
    
        self.change_position(0,0)
        print_to_stdout('The lexical analysis was completed successfully.')
        
        

############################## intermediate code ######################################

Quad = namedtuple('Quad', "label, operator, operand1, operand2, operand3")
_ = "_"



class IntermediateCodeGenerator:
    def __init__(self):
        self.quads = dict()
        self.quad_counter = 1
        self.temp_counter = 0
    
    def genQuad(self, operator, operand1=_, operand2=_, operand3=_):
        label = self.nextQuad()
        self.quads[label] = Quad(label, operator, operand1, operand2, operand3)
        self.quad_counter += 1
        
    def nextQuad(self): return str(self.quad_counter)
    
    def currentTemp(self): return f"_T{self.temp_counter}"
    
    def newTemp(self):
        self.temp_counter += 1
        return self.currentTemp()
    
    def write_to(self, file_name): #write into int file 
        Len = len(str(len(self.quads)))
        with open(file_name, "w") as int_file:
            for quad in self.quads.values():
                int_file.write(
                    f"{quad.label.rjust(Len)}: {quad.operator} {quad.operand1} {quad.operand2} {quad.operand3}\n"
                ) 
        print_to_stdout('The intermediate code generation was completed successfully.')
        print(f"    {file_name} has been created.")
        
    def backpatch(self, quadlist, label):
        for quadlabel in quadlist:
            quad = self.quads[quadlabel]
            self.quads[quadlabel] = quad._replace(operand3=label)
    
    def halt(self): self.genQuad("halt")
    
    def jump(self, target=_): self.genQuad("jump", operand3=target)
        
    def begin_block(self, name): self.genQuad("begin_block", name)
    
    def end_block(self, name): self.genQuad("end_block", name)
    
    def in_(self, var): self.genQuad("in", var)
    
    def out(self, var): self.genQuad("out", var)
    
    def par(self, var, mode): self.genQuad("par", var, mode)
    
    def par_cv(self, var): self.par(var, "cv")
    
    def par_ret(self, var): self.par(var, "ret")
    
    def call(self, name): self.genQuad("call", name)
    
    def ret(self, var): self.genQuad("ret", var)
    
    def assign(self, source, target):
        if source!=target: self.genQuad(":=", operand1=source, operand3=target)
    

################################### symbol table #############################################

class SymbolTableGenerator:
    def __init__(self, output_file):
        self.counter = 0
        self.level = 0
        self.offset = 0
        self.scopelst = []
        self.entitylst = []
        self.datatype = "INT"
        self.mode = "CV"
        self.output_file = output_file
        open(output_file, "w").close()

    def print_report_message(self):
        print_to_stdout('The symbol table generation was completed successfully.')
        print(f"    {self.output_file} has been created.")

    def write(self, *text):
        with open(self.output_file, "a") as file:
            with redirect_stdout(file): print(*text)

    def create_scope(self, scope):
        self.scope = scope
        self.scopelst.append(scope)
        self.level += 1
        self.write("Scope level: ", self.level, " , ", "     Scope: ", self.scope)

    def delete_scope(self, scope):
        del self.scopelst[-1]
        self.level -= 1
        self.delete_entity(scope)
        self.write("DELETE SCOPE!     CURRENT LEVEL: ", self.level, " , ", "CURRENT SCOPE LIST: ", self.scopelst)

    def create_var_entity(self, name):
        self.name = name
        self.entitylst.append(name)
        self.offset += 4
        self.write("VARIABLE ENTITY: ", self.name, " , ", "DATATYPE: ", self.datatype, " , ", "OFFSET: ", self.offset, " , ", "LEVEL: ", self.level)

    def create_par_entity(self, name):
        self.name = name
        self.entitylst.append(name)
        self.offset += 4
        self.write("PARAMETER ENTITY: ", self.name, " , ", "DATATYPE: ", self.datatype, " , ", "MODE: ", self.mode, " , ", "OFFSET: ", self.offset, " , ", "LEVEL: ", self.level)

    def create_func_entity(self, name):
        self.name = name
        self.entitylst.append(name)
        self.offset += 4
        self.write("FUNCTION CALL ENTITY: ", self.name, " , ", "OFFSET: ", self.offset, " , ", "LEVEL: ", self.level)

    def create_temp_entity(self, name):
        self.name = name
        self.entitylst.append(name)
        self.offset += 4
        self.write("TEMPORARY VARIABLE ENTITY: ", self.name, " , ", "OFFSET: ", self.offset, " , ", "LEVEL: ", self.level)

    def delete_entity(self, name):
        self.name = name
        l = 4 * len(self.entitylst)
        del self.entitylst[-1]
        self.offset = 0 
        self.write("DELETED ALL ENTITIES FROM: ", self.name)

   

#################################### syntax analyzer #########################################
### class Parser : Derives tokens from lexical analyzer (LexicalAnalyzer). ###
class Parser:
    def __init__(self, lexical_analyzer, intermediate_code_generator, symbol_table_generator):
        self.lexical_analyzer = lexical_analyzer
        self.current_token = self.lexical_analyzer.get_next_token()
        self.next_token = self.lexical_analyzer.get_next_token()
        self.icg = intermediate_code_generator
        self.stg = symbol_table_generator

    def consume_token(self):#uses the current token and updates it  
        self.current_token = self.next_token
        self.next_token = self.lexical_analyzer.get_next_token()

    def syntax_analyzer(self): 
        self.startRule()
        print_to_stdout('The syntactic analysis was completed successfully.')
    
    def does_current_token_match(self, *expected_values): return self.current_token.does_it_match(*expected_values)#checks is current token much the expected value

    def expand_terminal_symbol(self, expected_value, error=SyntError):#compares the current token with the expected value and consumes it or raises error
        token = self.current_token
        if self.does_current_token_match(expected_value):
            self.consume_token()
        else:
            error.at(
                token.line_number, token.column_number, token.length(),
                expected_value=expected_value, given_value=token.recognized_string
            )
        return token.recognized_string

    def expand(self, symbol):#if symbol is a string then it get expand as a terminal symbol otherwise its a method  
        if isinstance(symbol, str):
            return self.expand_terminal_symbol(symbol)
        else: 
            return symbol(self)

    def expand_sequence(self, *symbols):#expands everyone of the symbols
        return [self.expand(symbol) for symbol in symbols]
        
    def expand_optional(self, *symbols, expected_values=None):#expands symbols if they match with the expected value 
        if expected_values is None: expected_values = [symbols[0]]
        for expected_value in expected_values:
            if not isinstance(expected_value, str): raise TypeError(f"expected_value must be a string, but {expected_value} was found")
        if self.does_current_token_match(*expected_values):
            return self.expand_sequence(*symbols)
        return None

    def expand_star(self, *symbols, expected_values=None):#expands symbol as many times as the expected values
        if expected_values is None: expected_values = [symbols[0]]
        for expected_value in expected_values:
            if not isinstance(expected_value, str): raise TypeError(f"expected_value must be a string, but {expected_value} was found")
        while self.does_current_token_match(*expected_values):
            self.expand_sequence(*symbols)
        
    def expand_plus(self, *symbols, expected_values=None): #expands symbols at least one time 
        self.expand_sequence(*symbols)
        self.expand_star(*symbols, expected_values=expected_values)

    def eof(self): self.expand(EOF)#expands if end of file 
    

    def id_main_function(self):
        token = self.current_token
        self.expand(ID)
        if "main_" != token.recognized_string[:5]:
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value='a function starting with "main_"',
                given_value=token.recognized_string
            )
        return token.recognized_string

    def eqls(self):
        token = self.current_token
        self.expand(REL_OP)
        if not token.is_eqls():
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=EQLS, given_value=token.recognized_string
            )
        

    def startRule(self):
        """ startRule ::= def_main_part call_main_part """
        program = "cpy_program"
        self.def_main_part()
        self.icg.begin_block(program)
        self.call_main_part()
        self.icg.halt()
        self.icg.end_block(program)
        self.eof()

    def def_main_part(self):
        """ def_main_part ::= (def_main_function)+ """
        self.expand_plus(Parser.def_main_function, expected_values=[DEF])
        
    def def_main_function(self):
        """ def_main_function ::= def id_main_function(): function_body """
        main_function_name = self.next_token.recognized_string 
        self.expand_sequence(DEF, Parser.id_main_function, LPAR, RPAR, CLN)
        self.stg.create_scope(main_function_name)
        self.function_body(main_function_name)

    def def_function(self):
        """ def_function ::= def ID(id_list): function_body """
        function_name = self.next_token.recognized_string 
        self.expand_sequence(DEF, ID, LPAR, Parser.id_list, RPAR, CLN)
        self.stg.create_scope(function_name)
        self.function_body(function_name)
        
    def function_body(self, function_name):
        """ function_body ::= #{ declarations (def_function)* statements #} """
        self.expand(LBLCK)
        self.declarations()
        self.expand_star(Parser.def_function, expected_values=[DEF])
        self.icg.begin_block(function_name)
        self.statements()
        self.icg.end_block(function_name)
        self.stg.delete_scope(function_name)
        self.expand(RBLCK)

    def declarations(self):
        """ declarations ::= (declaration_line)* """
        self.expand_star(Parser.declaration_line, expected_values=[DECLARE])
        
    def declaration_line(self):
        """ declaration_line ::= #declare id_list """
        self.expand_sequence(DECLARE, Parser.id_list)

    def statement(self): 
        if self.does_current_token_match(ID): self.assignment_stat()
        elif self.does_current_token_match(PRINT): self.print_stat()
        elif self.does_current_token_match(RETURN): self.return_stat()
        elif self.does_current_token_match(IF): self.if_stat()
        elif self.does_current_token_match(WHILE): self.while_stat()
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"a statement",
                given_value=token.recognized_string
            )

    def statements(self):
        """ statements ::= (statement_line)+ """
        self.expand_plus(Parser.statement, expected_values=[ID, PRINT, RETURN, IF, WHILE])
    
    def assignment_stat(self): 
        var = self.expand(ID)
        self.expand(ASGN)
        if self.does_current_token_match(ADD_OP, NUM, LPAR, ID):
            self.icg.assign( self.expression(), var )
            self.stg.create_var_entity(var)
        elif self.does_current_token_match(INT):
            self.expand_sequence(INT, LPAR, INPUT, LPAR, RPAR, RPAR)
            self.icg.in_(var)
            self.stg.create_var_entity(var)
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"one of the {ADD_OP}, {NUM}, {LPAR}, {ID} or {INT}",
                given_value=token.recognized_string
            )
        self.expand(SMCLN)
        
    def print_stat(self):
        """ print_stat ::= print(expression) """
        self.icg.out( self.expand_sequence(PRINT, LPAR, Parser.expression, RPAR, SMCLN)[2] )

    def return_stat(self): 
        """ return_stat ::= return(expression) """
        self.icg.ret( self.expand_sequence(RETURN, LPAR, Parser.expression, RPAR, SMCLN)[2] )

    def if_stat(self): 
        condition = self.expand_sequence(IF, LPAR, Parser.condition, RPAR, CLN)[2]
        self.icg.backpatch(condition[True], self.icg.nextQuad())
        self.statement_body()
        if_list = [self.icg.nextQuad()]
        self.icg.jump()
        self.icg.backpatch(condition[False], self.icg.nextQuad())
        self.else_part()
        self.icg.backpatch(if_list, self.icg.nextQuad())

    def else_part(self):
        self.expand_optional(ELSE, CLN, Parser.statement_body)
        
    def while_stat(self):
        condition_label = self.icg.nextQuad()
        condition = self.expand_sequence(WHILE, LPAR, Parser.condition, RPAR, CLN)[2]
        self.icg.backpatch(condition[True], self.icg.nextQuad())
        self.statement_body()
        self.icg.jump(condition_label)
        self.icg.backpatch(condition[False], self.icg.nextQuad())

    def statement_body(self):
        if self.does_current_token_match(ID, PRINT, RETURN, IF, WHILE): self.statement()
        elif self.does_current_token_match(LBLCK): self.expand_sequence(LBLCK, Parser.statements, RBLCK)
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"a statement or {LBLCK}",
                given_value=token.recognized_string
            )
        
    def id_list(self): 
        if self.does_current_token_match(ID):
            self.expand(ID)
            self.expand_star(COM, ID)
    
    def optional_sign(self):
        """ optional_sign ::= ADD_OP | e """
        if self.does_current_token_match(ADD_OP): return self.expand(ADD_OP)
    
    def expression(self):
        """ expression ::= optional_sign term ( ADD_OP term )* """
        
        sign = self.optional_sign()
        t1 = self.term()
        if sign == "-":
            if t1.isnumeric(): t1 = sign + t1
            else: self.icg.genQuad("*","-1", t1, t1) 
        
        while self.does_current_token_match(ADD_OP):
            add_op = self.expand(ADD_OP)
            t2 = self.term()
            tmp = self.icg.newTemp()
            self.icg.genQuad(add_op, t1, t2, tmp)
            t1 = tmp
            
        return t1
    
    def term(self):
        """ term ::= factor ( MUL_OP factor )* """
        
        f1 = self.factor()
        
        while self.does_current_token_match(MUL_OP):
            mul_op = self.expand(MUL_OP)
            f2 = self.factor()
            tmp = self.icg.newTemp()
            self.icg.genQuad(mul_op, f1, f2, tmp)
            self.stg.create_temp_entity(tmp)
            f1 = tmp
        return f1
    
    def factor(self):
        if self.does_current_token_match(NUM): return self.expand(NUM)
        elif self.does_current_token_match(LPAR): return self.expand_sequence(LPAR, Parser.expression, RPAR)[1]
        elif self.does_current_token_match(ID):
            id = self.expand(ID)
            if not self.does_current_token_match(LPAR): return id
            else:
                self.expand(LPAR)
                parameters = self.actual_par_list()
                self.expand(RPAR)
                for parameter in parameters:
                    self.icg.par_cv(parameter)
                    self.stg.create_par_entity(parameter)
                tmp = self.icg.newTemp()
                self.stg.create_temp_entity(tmp)
                self.icg.par_ret(tmp)
                self.icg.call(id)
                return tmp
        else: 
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"{NUM}/{ID}/{LPAR}",
                given_value=token.recognized_string
            )

        
    def actual_par_list(self):
        parameters = []
        if self.does_current_token_match(ADD_OP, NUM, LPAR, ID):
            parameters.append( self.expression() )
            while self.does_current_token_match(COM):
                parameters.append( self.expand_sequence(COM, Parser.expression)[1] )
        return parameters
        
    def condition(self): 
        false_list, true_list = self.bool_term()
        while self.does_current_token_match(OR):
            self.icg.backpatch(false_list, self.icg.nextQuad())
            self.expand(OR)
            tmp = self.bool_term()
            true_list.extend(tmp[True])
            false_list = tmp[False]
        return false_list, true_list
    
    def bool_term(self):
        false_list, true_list = self.bool_factor()
        while self.does_current_token_match(AND):
            self.icg.backpatch(true_list, self.icg.nextQuad())
            self.expand(AND)
            tmp = self.bool_factor()
            true_list = tmp[True]
            false_list.extend(tmp[False])
        return false_list, true_list
    
    def sqr_condition(self): 
        return self.expand_sequence(LSQB, Parser.condition, RSQB)[1]
        
    def bool_factor(self): 
        if self.does_current_token_match(NOT): 
            tmp = self.expand_sequence(NOT, Parser.sqr_condition)[1]
            return tmp[True], tmp[False]
        elif self.does_current_token_match(LSQB): 
            return self.sqr_condition()
        elif self.does_current_token_match(ADD_OP, NUM, LPAR, ID):
            exp1, rel_op, exp2 = self.expand_sequence(Parser.expression, REL_OP, Parser.expression)
            true_list = [self.icg.nextQuad()]
            self.icg.genQuad(rel_op, exp1, exp2)
            false_list = [self.icg.nextQuad()]
            self.icg.jump()
            return false_list, true_list
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(),
                expected_value=f"not/[/addition operator/{NUM}/(/{ID}",
                given_value=token.recognized_string
            )

    def call_main_part(self):
        """ call_main_part ::= if __name__ == "__main__"": (main_function_call)+ """
        self.expand_sequence(IF, __NAME__, Parser.eqls, __MAIN__, CLN)
        self.expand_plus(Parser.main_function_call, expected_values=[ID])
        
    def main_function_call(self): 
        """ main_function_call ::= id_main_function(); """
        main_function_name = self.expand_sequence(Parser.id_main_function, LPAR, RPAR, SMCLN)[0]
        self.icg.call(main_function_name) # it gets called without parameters and it doesn't return anything
        


######################################### Main Function ###############################################
def main():
    global lines
    
    

    input_parser = ArgumentParser(description="Compile a CutePy program.")
    input_parser.add_argument("file", type=FileType("r"), help="a CutePy file")
    input_parser.add_argument("--lex", action="store_true", help="print the results of the lexical analysis")
    args = input_parser.parse_args()
    
    try:
        with args.file as file:
            lines = []
            for line in file:
                lines.append(line.replace("\n", EOL))
    except:
        print_to_stderr("Unable to read the file provided. Is it a valid CutePy file?")
        exit(1)
        
    file_name = args.file.name.split(".", 1)[0]

    lex = LexicalAnalyzer(lines)
    lex.lexical_analyzer(print_results=args.lex)
        
    icg = IntermediateCodeGenerator()
    stg = SymbolTableGenerator(f"{file_name}.symb")
    
    par = Parser(lex, icg, stg)
    par.syntax_analyzer()
    
    icg.write_to(f"{file_name}.int")

    stg.print_report_message()

    print_to_stdout('The compilation was completed successfully.') 
    


if __name__ == "__main__":
    main()