import copy

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        # Add built-in functions to global environment
        if parent is None:
            self.set('gimme', ('BUILTIN_FUNCTION', 'gimme', builtin_gimme))

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not defined")

    def set(self, name, value, update_existing=False):
        if update_existing:
            if name in self.vars:
                self.vars[name] = value
            elif self.parent:
                self.parent.set(name, value, update_existing=True)
            else:
                raise NameError(f"Variable '{name}' not defined")
        else:
            self.vars[name] = value

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

def builtin_gimme(args):
    """Built-in input function"""
    prompt = args[0] if len(args) > 0 else ""
    try:
        return input(prompt)
    except EOFError:
        return ""  # Return empty string on EOF

def is_array(value):
    return isinstance(value, list)

def resolve_index(array, index):
    if not isinstance(index, int):
        raise RuntimeError(f"Array index must be integer, got {type(index).__name__}")
    
    # Handle negative indexing
    if index < 0:
        index = len(array) + index
        
    # Bounds checking
    if index < 0 or index >= len(array):
        raise RuntimeError(f"Index {index} out of bounds for array of length {len(array)}")
    
    return index

def to_number(value):
    """Convert value to number if possible"""
    if not isinstance(value, str):
        return value
        
    try:
        # Try converting to float first to handle decimals
        return float(value)
    except ValueError:
        try:
            # If float fails, try int
            return int(value)
        except ValueError:
            return value

def eval_expression(expr, env):
    etype = expr[0]

    if etype == 'NUMBER':
        return expr[1]
    elif etype == 'STRING':
        return expr[1][1:-1]  # Strip quotes
    elif etype == 'BOOLEAN':
        return 'slay' if expr[1] else 'cap'
    elif etype == 'NULL':
        return 'nvm'
    elif etype == 'UNDECIDED':
        return 'delulu'
    elif etype == 'IDENTIFIER':
        val = env.get(expr[1])
        return val
    elif etype == 'ARRAY':
        return [eval_expression(e, env) for e in expr[1]]
    elif etype == 'INDEX':
        array = env.get(expr[1])
        if not is_array(array):
            raise RuntimeError(f"'{expr[1]}' is not an array")
        
        index = eval_expression(expr[2], env)
        resolved_index = resolve_index(array, index)
        return array[resolved_index]
    elif etype == 'UNARY_OP':
        op, right_expr = expr[1], expr[2]
        right = eval_expression(right_expr, env)
        if op == 'nah':  # NOT operator
            return 'cap' if right == 'slay' else 'slay'
    elif etype == 'LOGIC_OP':
        left = eval_expression(expr[1], env)
        op = expr[2]
        right = eval_expression(expr[3], env)
        
        if op == 'frfr':  # AND
            return 'slay' if left == 'slay' and right == 'slay' else 'cap'
        elif op == 'maybe':  # OR
            return 'slay' if left == 'slay' or right == 'slay' else 'cap'
    elif etype == 'BIN_OP':
        left = eval_expression(expr[1], env)
        op = expr[2]
        right = eval_expression(expr[3], env)
        
        # Convert booleans to numbers for arithmetic operations
        if isinstance(left, str) and left in ['slay', 'cap']:
            left = 1 if left == 'slay' else 0
        if isinstance(right, str) and right in ['slay', 'cap']:
            right = 1 if right == 'slay' else 0
        
        if op == '+': 
            return left + right
        if op == '-': 
            return left - right
        if op == '*': 
            return left * right
        if op == '/': 
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        if op == '>': 
            return 'slay' if left > right else 'cap'
        if op == '<': 
            return 'slay' if left < right else 'cap'
        if op == '==': 
            return 'slay' if left == right else 'cap'
        if op == '!=': 
            return 'slay' if left != right else 'cap'
        if op == '<=': 
            return 'slay' if left <= right else 'cap'
        if op == '>=': 
            return 'slay' if left >= right else 'cap'
        raise RuntimeError(f"Unknown operator {op}")
    elif etype == 'CALL':
        func_name = expr[1]
        args = [eval_expression(arg, env) for arg in expr[2]]
        return call_function(func_name, args, env)
    else:
        raise RuntimeError(f"Unknown expression type: {etype}")
    
def call_function(name, args, env):
    func = env.get(name)
    if not func:
        raise RuntimeError(f"Function '{name}' not found")
    
    if func[0] == 'FUNCTION':
        _, func_name, params, body = func
        func_env = Environment(parent=env)
        
        # Bind parameters
        if len(params) != len(args):
            raise RuntimeError(f"Function '{name}' expects {len(params)} arguments, got {len(args)}")
        for param, arg in zip(params, args):
            func_env.set(param, arg)

        try:
            for stmt in body:
                exec_statement(stmt, func_env)
            return 'nvm'  # Default return value
        except ReturnValue as ret:
            return ret.value
            
    elif func[0] == 'BUILTIN_FUNCTION':
        # Call built-in function
        return func[2](args)
    
    else:
        raise RuntimeError(f"'{name}' is not a function")

def exec_statement(stmt, env):
    stype = stmt[0]

    if stype == 'PRINT':
        val = eval_expression(stmt[1], env)
        print(val)
        
    elif stype == 'CALL_STMT':
        func_name = stmt[1]
        args = [eval_expression(arg, env) for arg in stmt[2]]
        call_function(func_name, args, env)

    elif stype == 'SQUAD_DECL':
        _, var_name, expr = stmt
        val = eval_expression(expr, env)
        
        # Create deep copy when assigning one squad to another
        if is_array(val):
            val = copy.deepcopy(val)
        # For strings, we don't need to copy as they're immutable
        elif not isinstance(val, str):
            raise RuntimeError(f"Cannot assign non-array to squad variable '{var_name}'")
        
        env.set(var_name, val)

    elif stype == 'SIGMA_DECL':  # Numeric variable declaration
        _, var_name, expr = stmt
        val = eval_expression(expr, env)
        
        # Convert input to number for sigma variables
        if isinstance(val, str):
            val = to_number(val)
        
        # Enforce sigma cannot be assigned to arrays
        if is_array(val):
            raise RuntimeError(f"Cannot assign array to sigma variable '{var_name}'")
        
        env.set(var_name, val)
        
    elif stype == 'TWEET_DECL':  # String variable declaration
        _, var_name, expr = stmt
        val = eval_expression(expr, env)
        
        # Convert to string for tweet variables
        if isinstance(val, (int, float, bool)):
            val = str(val)
        
        # Enforce tweet cannot be assigned to arrays
        if is_array(val):
            raise RuntimeError(f"Cannot assign array to tweet variable '{var_name}'")
        
        env.set(var_name, val)
        
    elif stype == 'VAR_ASSIGN':
        _, var_name, expr = stmt
        val = eval_expression(expr, env)
        
        # Handle type-specific assignments
        existing_val = env.get(var_name)
        
        # For sigma variables, convert strings to numbers
        if isinstance(existing_val, (int, float)) and isinstance(val, str):
            val = to_number(val)
        
        # For tweet variables, convert numbers to strings
        elif isinstance(existing_val, str) and isinstance(val, (int, float, bool)):
            val = str(val)
            
        env.set(var_name, val, update_existing=True)
        
    elif stype == 'INDEX_ASSIGN':
        _, array_name, index_expr, value_expr = stmt
        array = env.get(array_name)
        
        if not is_array(array):
            raise RuntimeError(f"'{array_name}' is not an array")
            
        index = eval_expression(index_expr, env)
        resolved_index = resolve_index(array, index)
        value = eval_expression(value_expr, env)
        
        array[resolved_index] = value

    elif stype == 'FOR':
        _, var_name, start, end, body = stmt
        for i in range(start, end + 1):
            env.set(var_name, i)
            for s in body:
                exec_statement(s, env)

    elif stype == 'WHILE':
        _, condition, body = stmt
        while eval_expression(condition, env) == 'slay':
            for s in body:
                exec_statement(s, env)

    elif stype == 'IF_ELSE':
        _, condition, then_body, else_body = stmt
        result = eval_expression(condition, env)
        if result == 'slay':
            for s in then_body:
                exec_statement(s, env)
        else:
            for s in else_body:
                exec_statement(s, env)

    elif stype == 'RETURN':
        val = env.get(stmt[1])
        raise ReturnValue(val)

    elif stype == 'EXIT':
        exit(0)

    elif stype == 'FUNCTION':
        env.set(stmt[1], stmt)

    else:
        raise RuntimeError(f"Unknown statement type: {stype}")

def run(ast, env=None):
    if env is None:
        env = Environment()

    for node in ast:
        exec_statement(node, env)