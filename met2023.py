import argparse
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

        global lines;print(lines,line_number)#todo remove
        # offending_line = lines[line_number] #todo remove

        print(f"--- Error:\n" + self.ident + message)

        if token_length is None: token_length = self.default_token_length

        if token_length>0:
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

    def does_it_match(self, grammar_symbol): raise NotImplementedError

class NumberToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, NUM, line_number, column_number)

    def validate(self):
        num = int(self.recognized_string)
        if abs(num) >= 2**32:
            OutOfBoundsNumberError.at(self.line_number, self.column_number, number=num)

    def does_it_match(self, grammar_symbol): return self.family == grammar_symbol

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

    def does_it_match(self, grammar_symbol): 
        print(f"expected {self.family}, found {grammar_symbol}")
        return self.family == grammar_symbol

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

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol

class AssignmentToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__(ASGN, "assignment", line_number, column_number)

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol

class DelimiterToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "delimiter", line_number, column_number)

    def validate(self):
        if self.recognized_string in delimiter_chars: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol

class AddOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, ADD_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in add_chars: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, grammar_symbol): return self.family == grammar_symbol

class MulOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, MUL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["*", "//"]: return
        if "/" in self.recognized_string:
            SingleDashOperatorError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, grammar_symbol): return self.family == grammar_symbol

class LogOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "logOperator", line_number, column_number)

    def validate(self):
        if self.recognized_string in logical_operators: return
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol

class RelOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, REL_OP, line_number, column_number)

    def validate(self):
        if self.recognized_string in ["<", ">", "!=", "<=", ">=", "=="]: return
        if "!" in self.recognized_string:
            IllegalExclamationMarkUsageError.at(self.line_number, self.column_number)
        raise ValueError(f"wrong initialization of {self.__class__.__name__}")

    def does_it_match(self, grammar_symbol): 
        return self.family == grammar_symbol or self.recognized_string == EQLS

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

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol

class EOFToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__(EOF, "__internal__", line_number, column_number)

    def does_it_match(self, grammar_symbol): return self.recognized_string == grammar_symbol


################################## lexical analyzer ##########################################

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

    def peek_next_character(self, offset=0):
        if self.is_end_of_file_reached(): return EOF
        if self.is_end_of_line_reached(offset): return EOL

        column = self.column_number + offset
        next_char = self.current_line()[column]

        if next_char not in legal_characters:
            IllegalCharacterError.at(self.line_number, column, char=next_char)

        return next_char

    def get_next_character(self):
        next_character = self.peek_next_character()
        self.change_column()
        return next_character

    def consume_next_character(self): self.change_column()

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








def terminal_symbol(expected_value, error=SyntError):
    def terminal_symbol_impl(par):
        token = par.current_token
        if token.does_it_match(expected_value):
            print(f"token '{token.recognized_string}' @ {token.line_number,token.column_number} got captured as {expected_value}")#todo! remove
            par.consume_token()
        else:
            error.at(
                token.line_number, token.column_number, token.length(),
                expected_value=expected_value, given_value=token.recognized_string
            )
    terminal_symbol_impl.expected_value = expected_value
    return terminal_symbol_impl

def sequence(*symbols):
    def sequence_impl(par):
        print("\nnew seq")
        for symbol in symbols: 
            token = par.current_token 
            print(f"    found token '{token.recognized_string}' @ {token.line_number,token.column_number}")#todo! remove
            print(symbol)
            symbol(par)
    sequence_impl.expected_value = symbols[0].expected_value
    return sequence_impl

# def star(expected_value, *symbols):
#     def star_impl(par):
#         while par.current_token.does_it_match(expected_value):
#             for symbol in symbols: symbol(par)
#     return star_impl

# def optional(expected_value, *symbols, error=SyntError):
#     def optional_impl(par):
#         if par.current_token.does_it_match(expected_value):
#             for symbol in symbols: symbol(par)
#     return optional_impl
    
#################################### syntax analyzer #########################################
# Parser : klash pou antlei lektikes monades apo ton lektiko analyth (Lex)

class Parser:
    def __init__(self, lexical_analyzer):
        self.lexical_analyzer = lexical_analyzer
        # self.lines = self.lexical_analyzer.lines
        self.current_token = self.lexical_analyzer.get_next_token()
        self.next_token = self.lexical_analyzer.get_next_token()

    # def peek_next_token(self): return self.next_token

    def consume_token(self):
        self.current_token = self.next_token
        self.next_token = self.lexical_analyzer.get_next_token()

    def syntax_analyzer(self):
        self.startRule()
        self.eof()
        print('Compilation completed successfully') #replace print with uniform print
        
    def star(self, expected_value=None, *symbols):
        if expected_value is None: expected_value = symbols[0].expected_value
        while self.current_token.does_it_match(expected_value):
            for symbol in symbols: symbol()
    
    def plus(self, expected_value=None, *symbols):
        if expected_value is None: expected_value = symbols[0].expected_value
        for symbol in symbols: symbol()
        self.star(expected_value, *symbols)

    def optional(self, expected_value=None, *symbols):
        if expected_value is None: expected_value = symbols[0].expected_value
        if self.current_token.does_it_match(expected_value):
            for symbol in symbols: symbol()

    eof = terminal_symbol(EOF)

    num = terminal_symbol(NUM)
    id = terminal_symbol(ID)
    add_op = terminal_symbol(ADD_OP)
    mul_op = terminal_symbol(MUL_OP)
    rel_op = terminal_symbol(REL_OP)

    if_ = terminal_symbol(IF)
    else_ = terminal_symbol(ELSE)
    while_ = terminal_symbol(WHILE)
    return_ = terminal_symbol(RETURN)
    print_ = terminal_symbol(PRINT)
    int_ = terminal_symbol(INT)
    input_ = terminal_symbol(INPUT)
    def_ = terminal_symbol(DEF)
    declare_ = terminal_symbol(DECLARE)
    name_ = terminal_symbol(__NAME__)
    main_ = terminal_symbol(__MAIN__)

    and_ = terminal_symbol(AND)
    or_ = terminal_symbol(OR)
    not_ = terminal_symbol(NOT)

    lpar = terminal_symbol(LPAR)
    rpar = terminal_symbol(RPAR)
    lsqb = terminal_symbol(LSQB)
    rsqb = terminal_symbol(RSQB)
    lblck = terminal_symbol(LBLCK)
    rblck = terminal_symbol(RBLCK)

    cln = terminal_symbol(CLN)
    smcln = terminal_symbol(SMCLN)
    com = terminal_symbol(COM)

    asgn = terminal_symbol(ASGN)

    eqls = terminal_symbol(EQLS)

    def id_main_function(self):
        token = self.current_token
        self.id()
        if "main_" != token.recognized_string[:5]:
            raise Exception() #todo message
        
    id_main_function.expected_value = ID             
        
    def function_body(self):
        self.declarations()
        self.star(self.def_function)
        self.statements()

    def id_list(self):
        def star_comma_id():
            return self.star(self.com, self.id)
        self.optional(self.id, star_comma_id)

    def_function = sequence(
        def_, id, lpar, id_list, rpar,
            lblck,
                function_body,
            rblck
    )

    declaration_line = sequence(declare_, id_list)

    def declarations(self): self.star(self.declaration_line)        
    
    def condition(self):
        self.bool_term()
        self.star(self.or_, self.bool_term)

    def bool_term(self):
        self.bool_factor()
        self.star(self.and_, self.bool_factor)

    bracketed_condition = sequence(lsqb, condition, rsqb)

    def bool_factor(self):
        token = self.current_token
        if token.does_it_match(NOT):
            self.not_(); self.bracketed_condition()
        elif token.does_it_match(LSQB):
            self.bracketed_condition()
        elif token.recognized_string in [NUM, ID, LPAR, ADD_OP]: #this is wrong
            self.expression()
            self.rel_op()
            self.expression()
        else:
            raise NotImplementedError()#todo
        
    def actual_par_list(self):
        token = self.current_token
        if token.recognized_string in [ADD_OP, NUM, LPAR, ID]:
            self.expression()
            self.star(self.com, self.expression)

    def idtail(self):
        self.optional(self.lpar, self.actual_par_list, self.rpar)

    def factor(self):
        token = self.current_token
        if token.does_it_match(NUM):
            self.num()
        elif token.does_it_match(ID):
            self.id()
            self.idtail()
        elif token.does_it_match(LPAR):
            self.lpar()
            self.expression()
            self.rpar()
        else:
            raise Exception() #todo
            self.error('Invalid prompt.')

    def term(self):
        self.factor()
        self.star(self.mul_op, self.factor())

    def optional_sign(self): self.optional(self.add_op)

    def expression(self):
        self.optional_sign()
        self.term()
        self.star(self.add_op, self.term)

    def statements(self):
        token = self.current_token
        while token.recognized_string in [ID, PRINT, RETURN, IF, WHILE]:
            self.statement()

    def statement(self):
        token = self.current_token
        if token.does_it_match(ID):
            self.assignment_stat()
        elif token.does_it_match(PRINT):
            self.print_stat()
        elif token.does_it_match(RETURN):
            self.return_stat()
        elif token.does_it_match(IF):
            self.if_stat()
        elif token.does_it_match(WHILE):
            self.while_stat()
        else:
            raise Exception()#todo somekind of error

    def statement_body(self):
        token = self.current_token
        if token.recognized_string in [ID, PRINT, RETURN, IF, WHILE]:
            self.statement
        elif token.does_it_match(LBLCK):
            self.lblck()
            self.statements()
            self.rblck()
        else:
            raise Exception("todo some kind of error")
    
    input_seq = sequence(int_, lpar, input_, lpar, rpar, rpar)

    def assignment_stat(self):
        self.id()
        self.eqls()
        self.lpar()
        token = self.current_token()
        if token.does_it_match(INT):
            self.input_seq()
        elif token.recognized_string in [NUM, ID, LPAR, ADD_OP]:
            self.expression()
        else:
            raise NotImplementedError() #todo
        self.smcln()
    
    print_stat = sequence(print_, lpar, expression, rpar, smcln)
    return_stat = sequence(return_, lpar, expression, rpar, smcln)
    
    def else_part(self): self.optional(self.else_, self.cln, self.statement_body)

    if_stat = sequence(
        if_, lpar, condition, rpar, cln,
            statement_body,
        else_part
    )
    
    while_stat = sequence(
        while_, lpar, condition, rpar, cln,
            statement_body
    )    

    def_main_function = sequence(
        def_, id_main_function, lpar, rpar, cln,
            lblck,
                function_body,
            rblck
    )

    def def_main_part(self): 
        self.plus(self.def_main_function)
    def_main_part.expected_value = def_.expected_value

    main_function_call = sequence(id_main_function, lpar, rpar, smcln)

    def main_function_calls(self):
        self.plus(self.main_function_call)
        
    call_main_part = sequence(
        if_, name_, eqls, main_, cln,
            main_function_calls
    )

    startRule = sequence(def_main_part, call_main_part)


def main(argv):
    file_name = argv[1]
    global lines

    with open(file_name, 'r') as file:
        lines = []
        for line in file:
            lines.append(line.replace("\n", EOL))

    lex = LexicalAnalyzer(lines)
    print(f"\n\n{lines=}\n\n")
    
    

    
    while not lex.is_end_of_file_reached():
        token: Token = lex.get_next_token()
        print(f"{token.recognized_string}, family: {token.family}, line: {token.line_number+1}, column: {token.column_number+1}")

    lex.change_position(0,0)
    print("\n\n")
    par = Parser(lex)
    par.syntax_analyzer()
    

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