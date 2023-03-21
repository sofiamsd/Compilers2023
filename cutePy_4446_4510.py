########################################### Phase 1 ###########################################
# Moisiadou Sofia AM:4446 cse84446 
# Tsiaousi Thomai AM:4510 cse84510
# How to run the code: python3 cutePy_4446_4510.py test.cpy
# Choose one of the given tests : testError_comment.cpy, testError_brackets.cpy 
# ,testRecursion.cpy,testCountdown.cpy ,testCalculateGrade.cpy
###############################################################################################

import sys
from string import ascii_letters, digits, whitespace


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
        self.ident = "   "
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

        print(f"--- Error:\n" + self.ident + message)

        if token_length is None: token_length = self.default_token_length

        
        if token_length>0 and line_number<len(lines):
            print(f"\n--- Line {line_number+1}:")
            print(lines[line_number])
            print(f"{' '*column_number}{'^'*token_length}")
            print()

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
OutOfBoundsNumberError = Error(
    "The number {number} was found at {position}. It has an absolute value greater than 2**32"
)
SingleDashOperatorError = Error(
    "The division operator is '//', a single '/' was found at {position}",
    token_length=1
)
SyntError = Error("A syntax error occurred at {position}. Expected '{expected_value}', but '{given_value}' was given")

NoError = Error()
NoError.at = lambda *args, **kwargs: None




### Recognise each token read from input cpy file and its family ###
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

    def is_main_function(self): return "main_" == self.recognized_string[:5]


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
                # this will raise an IllegalIdentifierStartsWithDigitError
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

        if recognized_string == "=":
            if next_char == "=":
                self.consume_next_character()
                return RelOperatorToken(EQLS, starts_at_line, starts_at_column)
            else:
                return AssignmentToken(starts_at_line, starts_at_column)

        if next_char == "=":
            recognized_string += self.get_next_character()

        return RelOperatorToken(recognized_string, starts_at_line, starts_at_column)



#################################### syntax analyzer #########################################
### class Parser : Derives tokens from lexical analyzer (LexicalAnalyzer). ###
class Parser:
    def __init__(self, lexical_analyzer):
        self.lexical_analyzer = lexical_analyzer
        self.current_token = self.lexical_analyzer.get_next_token()
        self.next_token = self.lexical_analyzer.get_next_token()

    def consume_token(self):
        self.current_token = self.next_token
        self.next_token = self.lexical_analyzer.get_next_token()

    def syntax_analyzer(self):
        self.startRule()
        self.eof()
        print('Compilation completed successfully') 

    def expand_terminal_symbol(self, expected_value, other_conditions=[], error=SyntError):
        token = self.current_token
        if token.does_it_match(expected_value):
            self.consume_token()
        else:
            error.at(
                token.line_number, token.column_number, token.length(),
                expected_value=expected_value, given_value=token.recognized_string
            )

    def expand(self, symbol):
        if isinstance(symbol, str):
            self.expand_terminal_symbol(symbol)
        else: 
            symbol(self)

    def expand_sequence(self, *symbols):
        for symbol in symbols: self.expand(symbol)

    def expand_optional(self, *symbols, expected_values=None):
        if expected_values is None: expected_values = [symbols[0]]
        for expected_value in expected_values:
            if not isinstance(expected_value, str): raise TypeError(f"expected_value must be a string, but {expected_value} was found")
        if self.current_token.does_it_match(*expected_values):
            self.expand_sequence(*symbols)

    def expand_star(self, *symbols, expected_values=None):
        if expected_values is None: expected_values = [symbols[0]]
        for expected_value in expected_values:
            if not isinstance(expected_value, str): raise TypeError(f"expected_value must be a string, but {expected_value} was found")
        while self.current_token.does_it_match(*expected_values):
            self.expand_sequence(*symbols)
        
    def expand_plus(self, *symbols, expected_values=None):
        self.expand_sequence(*symbols)
        self.expand_star(*symbols, expected_values=expected_values)

    def eof(self): self.expand(EOF)

    def id_main_function(self):
        token = self.current_token
        self.expand_terminal_symbol(ID)
        if not token.is_main_function():
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value="a function starting with 'main_'",
                given_value=token.recognized_string
            )

    def eqls(self):
        token = self.current_token
        self.expand_terminal_symbol(REL_OP)
        if not token.is_eqls():
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value="==", given_value=token.recognized_string
            )
        

    def startRule(self):
        self.def_main_part()
        self.call_main_part()

    def def_main_part(self):
        self.expand_plus(Parser.def_main_function, expected_values=[DEF])
        
    def def_main_function(self):
        self.expand_sequence(DEF, ID, LPAR, RPAR, CLN, LBLCK, Parser.function_body, RBLCK)

    def function_body(self):
        self.declarations()
        self.expand_star(Parser.def_function, expected_values=[DEF])
        self.statements()

    def def_function(self):
        self.expand_sequence(DEF, ID, LPAR, Parser.id_list, RPAR, CLN, LBLCK, Parser.function_body, RBLCK)

    def declarations(self):
        self.expand_star(Parser.declaration_line, expected_values=[DECLARE])
        
    def declaration_line(self):
        self.expand_sequence(DECLARE, Parser.id_list)

    def statement(self):
        if self.current_token.does_it_match(ID): self.assignment_stat()
        elif self.current_token.does_it_match(PRINT): self.print_stat()
        elif self.current_token.does_it_match(RETURN): self.return_stat()
        elif self.current_token.does_it_match(IF): self.if_stat()
        elif self.current_token.does_it_match(WHILE): self.while_stat()
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"a statement",
                given_value=token.recognized_string
            )

    def statements(self):
        self.expand_plus(Parser.statement, expected_values=[ID, PRINT, RETURN, IF, WHILE])
    
    def assignment_stat(self):
        self.expand(ID)
        self.expand(ASGN)
        if self.current_token.does_it_match(ADD_OP, NUM, LPAR, ID):
            self.expression()
        elif self.current_token.does_it_match(INT):
            self.expand_sequence(INT, LPAR, INPUT, LPAR, RPAR, RPAR)
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"one of the {ADD_OP}, {NUM}, {LPAR}, {ID} or {INT}",
                given_value=token.recognized_string
            )
        self.expand(SMCLN)
        
    def print_stat(self):
        self.expand_sequence(PRINT, LPAR, Parser.expression, RPAR, SMCLN)

    def return_stat(self):
        self.expand_sequence(RETURN, LPAR, Parser.expression, RPAR, SMCLN)

    def if_stat(self):
        self.expand_sequence(IF, LPAR, Parser.condition, RPAR, CLN)
        self.statement_body()
        self.else_part()

    def else_part(self):
        self.expand_optional(ELSE, CLN, Parser.statement_body)
        
    def while_stat(self):
        self.expand_sequence(WHILE, LPAR, Parser.condition, RPAR, CLN)
        self.statement_body()

    def statement_body(self):
        if self.current_token.does_it_match(ID, PRINT, RETURN, IF, WHILE): self.statement()
        elif self.current_token.does_it_match(LBLCK): self.expand_sequence(LBLCK, Parser.statements, RBLCK)
        else:
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"a statement or {LBLCK}",
                given_value=token.recognized_string
            )
        
    def id_list(self): 
        if self.current_token.does_it_match(ID):
            self.expand(ID)
            self.expand_star(COM, ID)
            
    def expression(self):
        self.optional_sign()
        self.term()
        self.expand_star(ADD_OP, Parser.term)

    def term(self):
        self.factor()
        self.expand_star(MUL_OP, Parser.factor)
    
    def factor(self):
        if self.current_token.does_it_match(NUM): self.expand(NUM)
        elif self.current_token.does_it_match(LPAR): self.expand_sequence(LPAR, Parser.expression, RPAR)
        elif self.current_token.does_it_match(ID): self.expand_sequence(ID, Parser.idtail)
        else: 
            token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(), 
                expected_value=f"{NUM}/{ID}/{LPAR}",
                given_value=token.recognized_string
            ) 

    def idtail(self):
        self.expand_optional(LPAR, Parser.actual_par_list, RPAR)
        
    def actual_par_list(self):
        if self.current_token.does_it_match(ADD_OP, NUM, LPAR, ID):
            self.expression()
            self.expand_star(COM, Parser.expression)
        
    def optional_sign(self): self.expand_optional(ADD_OP)
        
    def condition(self):
        self.bool_term()
        self.expand_star(OR, Parser.bool_term)

    def sqr_condition(self):
        self.expand_sequence(LSQB, Parser.condition, RSQB)

    def bool_term(self):
        self.bool_factor()
        self.expand_star(AND, Parser.bool_factor)
        
    def bool_factor(self):
        if self.current_token.does_it_match(NOT): self.expand_sequence(NOT, Parser.sqr_condition)
        elif self.current_token.does_it_match(LSQB): self.sqr_condition()
        elif self.current_token.does_it_match(ADD_OP, NUM, LPAR, ID): self.expand_sequence(Parser.expression, REL_OP, Parser.expression)
        else:
            token: Token = self.current_token
            SyntError.at(
                token.line_number, token.column_number, token.length(),
                expected_value=f"not/[/addition operator/{NUM}/(/{ID}"
            )

    def call_main_part(self):
        self.expand_sequence(IF, __NAME__, Parser.eqls, __MAIN__, CLN)
        self.expand_plus(Parser.main_function_call, expected_values=[ID])
        
    def main_function_call(self): self.expand_sequence(Parser.id_main_function, LPAR, RPAR, SMCLN)



######################################### Main Function ###############################################
def main(argv):
    file_name = argv[1]
    global lines

    with open(file_name, 'r') as file:
        lines = []
        for line in file:
            lines.append(line.replace("\n", EOL))

    lex = LexicalAnalyzer(lines)
    
    while True:
        token = lex.get_next_token()
        if token.recognized_string == EOF: break
        print(token)

    lex.change_position(0,0)
    
    par = Parser(lex)
    par.syntax_analyzer()
    


if __name__ == "__main__":
    global lines
    
    main(sys.argv)