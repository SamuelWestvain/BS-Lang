import re

token_specification = [
    ('COMMENT_START', r'on_read\{'),
    ('NUMBER',     r'-?\d+(\.\d+)?'),
    ('STRING',     r'"[^"\n]*"'),
    ('COMPARE',     r'==|!=|<=|>='),
    ('ASSIGN',      r'='),
    ('OPERATOR',    r'[\+\-\*/<>!]'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('LBRACKET',   r'\['),
    ('RBRACKET',   r'\]'),
    ('COMMA',      r','),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NEWLINE',    r'\n'),
    ('SKIP',       r'[ \t]+'),
    ('MISMATCH',   r'.'),
]

keywords = {
    'cook': 'COOK',
    'sigma': 'SIGMA',
    'tweet': 'TWEET',
    'squad': 'SQUAD',
    'hawk_tuah': 'HAWK_TUAH',
    'yap': 'YAP',
    'flex': 'FLEX',
    'rizz_check': 'RIZZ_CHECK',
    'nah_fam': 'NAH_FAM',
    'yeet': 'YEET',
    'skibidi': 'SKIBIDI',
    'slay': 'TRUE',
    'cap': 'FALSE',
    'frfr': 'AND',
    'maybe': 'OR',
    'nah': 'NOT',
    'nvm': 'NULL',
    'delulu': 'UNDECIDED',
    'sus': 'SUS',
    'panik': 'PANIK',
    'till': 'TILL',
    'to': 'TO',
    # Removed gimme from keywords - treat as regular identifier
}

def tokenize(code):
    tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    line = code

    while pos < len(line):
        match = get_token(line, pos)
        if not match:
            raise SyntaxError(f"Unexpected character: {line[pos]}")
        typ = match.lastgroup
        val = match.group()

        if typ == 'NEWLINE' or typ == 'SKIP':
            pass
        elif typ == 'COMMENT_START':
            comment_end = line.find('}', pos)
            if comment_end == -1:
                raise SyntaxError("Unclosed comment")
            pos = comment_end + 1
            continue
        elif typ == 'MISMATCH':
            raise SyntaxError(f"Unexpected token: {val}")
        elif typ == 'IDENTIFIER':
            if val in keywords:
                tokens.append((keywords[val], val))
            else:
                tokens.append((typ, val))
        else:
            tokens.append((typ, val))

        pos = match.end()

    return tokens