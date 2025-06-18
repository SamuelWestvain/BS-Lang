from lexer import tokenize

tokens = []
current = 0

def peek(offset=0):
    return tokens[current + offset] if current + offset < len(tokens) else ('EOF', '')

def advance():
    global current
    current += 1
    return tokens[current - 1]

def match(*expected):
    if peek()[0] in expected:
        return advance()
    return None

def consume(expected_type):
    token = peek()
    if token[0] == expected_type:
        return advance()
    raise SyntaxError(f"Expected {expected_type}, got {token[0]}")

def parse_primary():
    token = advance()
    if token[0] == 'NUMBER':
        # Handle both integers and floats
        num_str = token[1]
        if '.' in num_str:
            return ('NUMBER', float(num_str))
        return ('NUMBER', int(num_str))
    elif token[0] == 'STRING':
        return ('STRING', token[1])
    elif token[0] == 'IDENTIFIER':
        if peek()[0] == 'DOT':
            consume('DOT')
            method = consume('IDENTIFIER')[1]
            if method != 'scooch':
                raise SyntaxError(f"Unknown method '{method}'")
            consume('LPAREN')
            method_args = []
            while peek()[0] != 'RPAREN':
                method_args.append(parse_expression())
                if peek()[0] == 'COMMA':
                    consume('COMMA')
                else:
                    break
            consume('RPAREN')
            return ('METHOD_CALL', token[1], 'scooch', method_args)
        elif peek()[0] == 'LPAREN':
            func_name = token[1]
            consume('LPAREN')
            args = []
            while peek()[0] != 'RPAREN':
                args.append(parse_expression())
                if peek()[0] == 'COMMA':
                    consume('COMMA')
                else:
                    break
            consume('RPAREN')
            return ('CALL', func_name, args)
        elif peek()[0] == 'LBRACKET':
            consume('LBRACKET')
            index_expr = parse_expression()
            consume('RBRACKET')
            return ('INDEX', token[1], index_expr)
        else:
            return ('IDENTIFIER', token[1])
    elif token[0] == 'TRUE':
        return ('BOOLEAN', True)
    elif token[0] == 'FALSE':
        return ('BOOLEAN', False)
    elif token[0] == 'NULL':
        return ('NULL',)
    elif token[0] == 'UNDECIDED':
        return ('UNDECIDED',)
    elif token[0] == 'LBRACKET':  # Array literal
        elements = []
        while peek()[0] != 'RBRACKET' and peek()[0] != 'EOF':
            elements.append(parse_expression())
            if not match('COMMA'):
                break
        consume('RBRACKET')
        return ('ARRAY', elements)
    elif token[0] == 'LPAREN':
        expr = parse_expression()
        consume('RPAREN')
        return expr
    raise SyntaxError(f"Unexpected token: {token}")

def parse_comparison():
    left = parse_primary()
    
    while peek()[0] in ['OPERATOR', 'COMPARE']:
        op = advance()[1]
        right = parse_primary()
        left = ('BIN_OP', left, op, right)
    
    return left

def parse_expression():
    if match('NOT'):
        expr = parse_expression()
        return ('UNARY_OP', 'nah', expr)
    
    if match('OPERATOR') and peek()[0] == 'NUMBER' and tokens[current-1][1] == '-':
        number = advance()
        num_val = float(number[1]) if '.' in number[1] else int(number[1])
        return ('NUMBER', -num_val)
    
    left = parse_comparison()
    
    while peek()[0] in ['AND', 'OR']:
        op = advance()[1]
        right = parse_comparison()
        left = ('LOGIC_OP', left, op, right)
    
    return left

def parse_control_condition():
    if peek()[0] == 'LPAREN':
        consume('LPAREN')
        expr = parse_expression()
        consume('RPAREN')
        return expr
    return parse_expression()

def parse_statement():
    if match('HAWK_TUAH'):
        consume('LPAREN')
        expr = parse_expression()
        consume('RPAREN')
        return ('PRINT', expr)

    if match('SQUAD'):  # Array declaration
        var_name = consume('IDENTIFIER')[1]
        consume('ASSIGN')
        if peek()[0] == 'LBRACKET':  # Array literal
            expr = parse_primary()
        else:
            expr = parse_expression()
        return ('SQUAD_DECL', var_name, expr)
    
    if match('SIGMA'):  # Numeric variable declaration
        var_name = consume('IDENTIFIER')[1]
        consume('ASSIGN')
        expr = parse_expression()
        return ('SIGMA_DECL', var_name, expr)
    
    if match('TWEET'):  # String variable declaration
        var_name = consume('IDENTIFIER')[1]
        consume('ASSIGN')
        expr = parse_expression()
        return ('TWEET_DECL', var_name, expr)
    
    if (peek()[0] == 'IDENTIFIER' and 
        peek(1)[0] == 'LBRACKET' and 
        peek(2)[0] != 'ASSIGN'):
        # Array index assignment: arr[index] = value
        array_name = consume('IDENTIFIER')[1]
        consume('LBRACKET')
        index_expr = parse_expression()
        consume('RBRACKET')
        consume('ASSIGN')
        value_expr = parse_expression()
        return ('INDEX_ASSIGN', array_name, index_expr, value_expr)
    
    if peek()[0] == 'IDENTIFIER' and peek(1)[0] == 'ASSIGN':
        var_name = consume('IDENTIFIER')[1]
        consume('ASSIGN')
        expr = parse_expression()
        return ('VAR_ASSIGN', var_name, expr)
    
    if peek()[0] == 'IDENTIFIER' and peek(1)[0] == 'LPAREN':
        func_name = advance()[1]
        consume('LPAREN')
        args = []
        while peek()[0] != 'RPAREN':
            args.append(parse_expression())
            if peek()[0] == 'COMMA':
                consume('COMMA')
        consume('RPAREN')
        return ('CALL_STMT', func_name, args)

    if match('YAP'):
        var_name = consume('IDENTIFIER')[1]
        consume('TILL')
        start = consume('NUMBER')[1]
        consume('TO')
        end = consume('NUMBER')[1]
        consume('LBRACE')
        body = []
        while peek()[0] != 'RBRACE':
            body.append(parse_statement())
        consume('RBRACE')
        return ('FOR', var_name, int(start), int(end), body)

    if match('FLEX'):
        condition = parse_control_condition()
        consume('LBRACE')
        body = []
        while peek()[0] != 'RBRACE':
            body.append(parse_statement())
        consume('RBRACE')
        return ('WHILE', condition, body)

    if match('RIZZ_CHECK'):
        condition = parse_control_condition()
        consume('LBRACE')
        then_body = []
        while peek()[0] != 'RBRACE':
            then_body.append(parse_statement())
        consume('RBRACE')

        else_body = []
        if match('NAH_FAM'):
            consume('LBRACE')
            while peek()[0] != 'RBRACE':
                else_body.append(parse_statement())
            consume('RBRACE')
        return ('IF_ELSE', condition, then_body, else_body)

    if match('YEET'):
        value = consume('IDENTIFIER')[1]
        return ('RETURN', value)

    if match('SKIBIDI'):
        return ('EXIT',)
    
    if match('SUS'):
        consume('LBRACE')
        try_body = []
        while peek()[0] != 'RBRACE' and peek()[0] != 'EOF':
            try_body.append(parse_statement())
        consume('RBRACE')
        
        # Parse panik block
        if not match('PANIK'):
            raise SyntaxError("Expected 'panik' after 'sus' block")
        consume('LBRACE')
        catch_body = []
        while peek()[0] != 'RBRACE' and peek()[0] != 'EOF':
            catch_body.append(parse_statement())
        consume('RBRACE')
        
        return ('TRY_CATCH', try_body, catch_body)
    
    raise SyntaxError(f"Unknown statement at token {peek()}")

def parse_function():
    consume('COOK')
    name = consume('IDENTIFIER')[1]
    consume('LPAREN')
    params = []
    while peek()[0] != 'RPAREN':
        param = consume('IDENTIFIER')[1]
        params.append(param)
        if not match('COMMA'):
            break
    consume('RPAREN')
    consume('LBRACE')
    body = []
    while peek()[0] != 'RBRACE':
        body.append(parse_statement())
    consume('RBRACE')
    return ('FUNCTION', name, params, body)

def parse(tokens_input):
    global tokens, current
    tokens = tokens_input
    current = 0

    ast = []
    while peek()[0] != 'EOF':
        try:
            if peek()[0] == 'COOK':
                ast.append(parse_function())
            else:
                stmt = parse_statement()
                ast.append(stmt)
        except SyntaxError as e:
            while (peek()[0] not in ['EOF', 'HAWK_TUAH', 'SIGMA', 'TWEET', 'SQUAD', 'YAP', 'FLEX', 
                                    'RIZZ_CHECK', 'YEET', 'SKIBIDI', 'COOK', 'RBRACE']):
                advance()
            print(f"Syntax Error: {e}")
    return ast