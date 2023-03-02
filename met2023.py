ascii_lowercase    = "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", \
                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", \
                     "u", "v", "w", "x", "y", "z"

ascii_uppercase    = "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", \
                     "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", \
                     "U", "V", "W", "X", "Y", "Z" 

ascii_letters      = ascii_lowercase + ascii_uppercase

digits             = "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"

underscore = "_",
identifier_characters = ascii_letters + underscore + digits


keywords = ["if", "else", "while", "return", "print", "int", "input", "def", "#declare", "__name__", '"__main__"']
keyword_characters = identifier_characters + ("#", "\"")

logical_operators = ["not", "or", "and"]

add_chars = "+", "-"
mul_chars = "*", "/"
rel_chars = "<", ">", "="
assignment_chars = "=",
delimiter_chars = ";", ",", ":"
grouping_chars = "[" , "]" , "(" ,")" ,"#", "{", "}"
comment_chars = "#", "$"

symbols            = "+", "-", "*", "/", "<", ">", "=", ";", ",", ":", \
                     "[", "]", "(", ")", "{", "}", "#", "$", "\""

white_characters   = " ", "\t", "\r", "\n" 

printable_characters = keyword_characters + symbols

legal_characters     = printable_characters + white_characters


def is_ascii_letter(char):
    return char in ascii_letters

def is_digit(char):
    return char in digits

def can_be_used_in_identifiers(char):
    return char in identifier_characters

def can_be_used_in_keywords(char):
    return char in keyword_characters

def is_keyword(string):
    return string in keywords

def is_addOperator(char):
    return char in add_chars

def is_mulOperator(char):
    return char in mul_chars

def is_relOperator(char):
    return char in rel_chars

def is_logOperator(string):
    return string in logical_operators

def is_assignmentSymbol(char):
    return char in assignment_chars

def is_delimiterSymbol(char):
    return char in delimiter_chars

def is_groupingSymbol(char):
    return char in grouping_chars

def is_commentSymbol(char):
    return char in comment_chars

def is_character_illegal(char):
    return char not in legal_characters


class Error:
    def __init__(self, message, additional_info=None, sep=".\n" + " "*7):
        self.message = message
        if additional_info is None:
            self.additional_info = ""
        else:
            self.additional_info = sep + additional_info

    def at(self, line_number, column_number):
        print(f"Error: {self.message} at line {line_number+1}, column {column_number+1}{self.additional_info}", end="")
        exit()


CommentError = Error(
    "A comment was opened",
    "or at some earlier point and it was not closed before the end of the file",
    sep=" "
)
IdentifierExceeding30CharsError = Error(
    "An identifier with more than 30 characters was found"
)
IllegalCharacterError = Error(
    "An illegal character was found",
    "These are the only legal characters:\n" + " "*7 + "".join(printable_characters) + r" \t\r\n",
    sep=". "
)
IllegalIdentifierError = Error(
    "An illegal identifier was found",
    "An identifier must start with a letter and use ASCII characters"
)
IllegalIdentifierSameAsKeywordError = Error(
    "An illegal identifier was found",
    "A keyword cannot be used as an identifier"
)
IllegalIdentifierStartsWithDigitError = Error(
    "An illegal identifier was found or a space was forgotten",
    "An identifier must start with a letter and not a number"
)

IllegalHashtagUsageError = Error(
    "A misspelled keyword, comment delimiter or an illegal identifier was found",
    "The only legal uses of # are in #{, #}, #declare or #$"
)
IllegalQuoteUsageError = Error(
    "A misspelled keyword or an illegal identifier was found",
    "The only legal use of \" is in the keyword \"__main__\""
)
NotKeywordError = Error(
    "A misspelled keyword or an illegal identifier was found",
    "An identifier must start with a letter and use ASCII characters"
)
OutOfBoundsNumber = Error(
    "There is a number with absolute value greater than 2**32"
)
SingleDashOperatorError = Error("The division operator is //, a single / was found")
SyntaxError = Error("A syntax error occured")


class Token:
    def __init__(self, recognized_string, family, line_number, column_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number
        self.column_number = column_number
        self.validate()

    def validate(self):
        pass

    def first_letter(self): return self.recognized_string[0]
    
    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):
        raise NotImplementedError()

class NumberToken(Token):
    def validate(self):
        num = int(self.recognized_string)
        if abs(num) >= 2**32:
            OutOfBoundsNumber.at(self.line_number, self.column_number)

    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):
        recognized_string = starting_with

        while True:
            next_char = lex.peek_next_character()

            if is_digit(next_char):
                recognized_string += next_char
                lex.change_column()
            elif can_be_used_in_identifiers(next_char):
                IllegalIdentifierStartsWithDigitError.at(starts_at_line, starts_at_column)
            else:
                return NumberToken(recognized_string, "number", starts_at_line, starts_at_column)

class IdentifierToken(Token):
    def validate(self):
        if is_keyword(self.recognized_string):
            IllegalIdentifierSameAsKeywordError.at(self.line_number, self.column_number)
        
        if not is_ascii_letter(self.first_letter()):
            IllegalIdentifierError.at(self.line_number, self.column_number)

        if len(self.recognized_string) > 30:
            IdentifierExceeding30CharsError.at(self.line_number, self.column_number)

    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):
        recognized_string = starting_with

        while True:
            next_char = lex.peek_next_character()

            if can_be_used_in_identifiers(next_char):
                recognized_string += next_char
                lex.change_column()
            else:
                if is_keyword(recognized_string):
                    return KeywordToken(recognized_string, "keyword", starts_at_line, starts_at_column)
                elif is_logOperator(recognized_string):
                    return LogOperatorToken(recognized_string, starts_at_line, starts_at_column)
                else:
                    return IdentifierToken(recognized_string, "identifier", starts_at_line, starts_at_column)

class KeywordToken(Token):
    def validate(self):
        if not is_keyword(self.recognized_string):
            if self.first_letter() == "#":
                IllegalHashtagUsageError.at(self.line_number, self.column_number)
            if self.first_letter() == "\"":
                IllegalQuoteUsageError.at(self.line_number, self.column_number)

            NotKeywordError.at(self.line_number, self.column_number)

    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):
        recognized_string = starting_with

        while True:
            next_char = lex.peek_next_character()

            if can_be_used_in_keywords(next_char):
                recognized_string += next_char
                lex.change_column()
            else:
                if recognized_string == "#" and is_groupingSymbol(next_char):
                    recognized_string += next_char
                    return GroupingSymbolToken(recognized_string, starts_at_line, starts_at_column)
                else:
                    return KeywordToken(recognized_string, "keyword", starts_at_line, starts_at_column)


class AssignmentToken(Token):
    def __init__(self, line_number, column_number):
        super().__init__("=", "assignment", line_number, column_number)

class DelimiterToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "delimiter", line_number, column_number)

class AddOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "addOperator", line_number, column_number)

class MulOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "mulOperator", line_number, column_number)

    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):
        if starting_with == "*":
            return MulOperatorToken(starting_with, starts_at_line, starts_at_column)

        if starting_with == "/":
            next_char = lex.get_next_character()
            if next_char == "/":
                return MulOperatorToken("//", starts_at_line, starts_at_column)
            SingleDashOperatorError.at(starts_at_line, starts_at_column)

class LogOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "logOperator", line_number, column_number)

class RelOperatorToken(Token):
    def __init__(self, recognized_string, line_number, column_number):
        super().__init__(recognized_string, "relOperator", line_number, column_number)

    @staticmethod
    def create_from(lex, starting_with, starts_at_line, starts_at_column):        
        next_char = lex.peek_next_character()

        if starting_with == "=":
            if next_char == "=":
                lex.change_column()
                return RelOperatorToken("==", starts_at_line, starts_at_column)
            else:
                return AssignmentToken(starts_at_line, starts_at_column)

        recognized_string = starting_with

        if starting_with == "<" and next_char == ">":
            lex.change_column()
            return RelOperatorToken("<>", starts_at_line, starts_at_column)

        if next_char == "=":
            lex.change_column()
            recognized_string += next_char
        
        return RelOperatorToken(recognized_string, starts_at_line, starts_at_column)
        
class GroupingSymbolToken(Token):
    def __init__(self, recognized_string, line_number, column_number):  
        super().__init__(recognized_string, "groupingSymbol", line_number, column_number)

    def validate(self):
        if is_groupingSymbol(self.recognized_string):
            return

        if self.recognized_string not in ["#{", "#}"]:
            IllegalHashtagUsageError.at(self.line_number, self.column_number)
    



class Lex:
    def __init__(self, file_name):  # todo: perhaps check file extension, only accept .cpy
        with open(file_name, 'r') as file:
            self.lines = file.readlines()
        self.line_number = 0
        self.column_number = 0

    def current_line(self):
        if self.is_end_of_file_reached():
            return ""
        return self.lines[self.line_number]

    def is_end_of_file_reached(self):
        return self.line_number >= len(self.lines) 
    
    def is_end_of_line_reached(self):
        return self.column_number >= len(self.current_line())

    def reset_column(self):
        self.column_number = 0

    def change_line(self):
        self.line_number += 1
        self.reset_column()

    def change_column(self):
        self.column_number += 1
        if self.is_end_of_line_reached():
            self.change_line()

    def peek_next_character(self, offset=0):
        if self.is_end_of_file_reached(): 
            return ""
        
        next_char = self.current_line()[self.column_number + offset]

        if is_character_illegal(next_char): 
            IllegalCharacterError.at(self.line_number, self.column_number + offset)
        
        return next_char
        
    def get_next_character(self):
        next_character = self.peek_next_character()
        self.change_column()
        return next_character
    
    def skip_whitespace(self):
        if self.is_end_of_file_reached(): return
        
        while True:
            next_char = self.peek_next_character()
            if next_char.isspace():
                self.change_column()
            else:
                break

    def skip_comment(self):
        if self.is_end_of_file_reached(): return

        if self.peek_next_character(0) == "#":
            if self.peek_next_character(1) != "$":
                return
            # print("comments on", self.line_number, self.column_number)
            line = self.line_number
            column = self.column_number
            self.change_column()
            self.change_column()

            while not self.is_end_of_file_reached():
                char = self.get_next_character()
                if char == "#":
                    char = self.get_next_character()
                    if char == "$":
                        # print("comments off", self.line_number, self.column_number-2)
                        return
            else:
                CommentError.at(line, column)


    
    def get_next_token(self):
        """
        Returns the next recognized token or detects an error and exits.
        Before calling it, there should be a check if the end of the file 
        has been reached.
        """
        line = self.line_number
        column = self.column_number

        while True:
            self.skip_whitespace()
            self.skip_comment()
            if line != self.line_number or column != self.column_number:
                line = self.line_number
                column = self.column_number
            else:
                break

        char = self.get_next_character()

        if is_digit(char):
            return NumberToken.create_from(self, starting_with=char, starts_at_line=line, starts_at_column=column)
        
        if is_ascii_letter(char):
            return IdentifierToken.create_from(self, starting_with=char, starts_at_line=line, starts_at_column=column)
        
        if can_be_used_in_keywords(char):
            return KeywordToken.create_from(self, starting_with=char, starts_at_line=line, starts_at_column=column)
        
        if is_delimiterSymbol(char):
            return DelimiterToken(char, line, column)
        
        if is_groupingSymbol(char):
            return GroupingSymbolToken(char, line, column)

        if is_addOperator(char):
            return AddOperatorToken(char, line, column)
        
        if is_mulOperator(char):
            return MulOperatorToken.create_from(self, char, line, column)
            
        if is_relOperator(char):
            return RelOperatorToken.create_from(self, char, line, column)
        
        return Token(char, "unidentified", line, column)

    


lex = Lex("./test1.cpy")
print(lex.lines)
while not lex.is_end_of_file_reached():
    token: Token = lex.get_next_token()
    print(f"{token.recognized_string}, family: {token.family}, line: {token.line_number+1}, column: {token.column_number+1}")

line = 0
print(line, end=" ")
while not lex.is_end_of_file_reached():
    lex.skip_whitespace()
    # print(lex.line_number, lex.column_number,lex.get_next_character(),lex.line_number, lex.column_number, end="")
    char = lex.get_next_character()
    if lex.line_number!=line:
        line = lex.line_number
        print()
        print(line, end=" ")
    print(char,end="")



