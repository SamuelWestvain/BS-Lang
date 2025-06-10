import sys
import io
import gradio as gr
import tempfile
import os
from lexer import tokenize
from parser import parse
from interpreter import run, Environment

class InputManager:
    def __init__(self):
        self.input_queue = []
        self.current_input = None
    
    def add_input(self, value):
        self.input_queue.append(value)
    
    def get_input(self, prompt=""):
        if self.input_queue:
            return self.input_queue.pop(0)
        raise RuntimeError("No input available in queue")

input_manager = InputManager()

def run_lava_code(code, show_tokens=False, show_ast=False, *inputs):
    """Execute LAVA code and capture output/errors"""
    # Clear previous inputs and add new ones
    input_manager.input_queue = list(inputs)
    
    env = Environment()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = buffer = io.StringIO()
    sys.stderr = buffer

    tokens = None
    ast = None
    
    try:
        # Tokenize and parse regardless to capture tokens/ast
        tokens = tokenize(code)
        ast = parse(tokens)
        
        # Run the code
        run(ast, env)
    except SyntaxError as se:
        print(f"Syntax Error: {se}")
    except Exception as e:
        print(f"Runtime Error: {e}")
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    # Start building output
    output_parts = []
    execution_output = buffer.getvalue()
    
    if execution_output:
        output_parts.append(f"🔥 EXECUTION OUTPUT 🔥\n{execution_output}")
    
    # Conditionally add tokens and AST
    if show_tokens and tokens:
        token_output = "\n".join([str(tok) for tok in tokens])
        output_parts.append(f"\n\n🧪 TOKENS 🧪\n{token_output}")
    
    if show_ast and ast:
        ast_output = "\n".join([str(node) for node in ast])
        output_parts.append(f"\n\n🌳 ABSTRACT SYNTAX TREE 🌳\n{ast_output}")
    
    return "\n".join(output_parts)

def download_code(code):
    """Create a temporary .lava file for download"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".lava")
    try:
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(code)
        return temp_file.name
    except Exception as e:
        os.unlink(temp_file.name)
        raise e

# Update the interpreter.py to use input_manager
# Add this to your interpreter.py (in the eval_expression function)
"""
elif etype == 'CALL':
    func_name = expr[1]
    args = expr[2]
    if func_name == 'gimme':
        if not args:
            return input_manager.get_input()
        prompt = eval_expression(args[0], env)
        return input_manager.get_input(prompt)
    return call_function(func_name, args, env)
"""

EXAMPLES = [
    {
        "name": "Basic Input Example",
        "code": """sigma name = gimme("Enter your name: ")
hawk_tuah("Hello, " + name)"""
    },
    {
        "name": "Complex Function Example",
        "code": """cook gyatt() {
  hawk_tuah("Hello World")
  hawk_tuah(1 + 2)
  sigma a = gimme("Enter a number: ")
  sigma b = gimme("Enter another number: ")
  yap i till 0 to 3 {
    hawk_tuah(i)
  }
  rizz_check a > b {
    yeet a
  } nah_fam {
    yeet b
  }
}
hawk_tuah(gyatt())"""
    },
    {
        "name": "Calculator",
        "code": """sigma a = gimme("Enter first number: ")
sigma b = gimme("Enter second number: ")
sigma op = gimme("Enter operation (+, -, *, /): ")

rizz_check op == "+" {
    hawk_tuah(a + b)
} nah_fam rizz_check op == "-" {
    hawk_tuah(a - b)
} nah_fam rizz_check op == "*" {
    hawk_tuah(a * b)
} nah_fam rizz_check op == "/" {
    hawk_tuah(a / b)
} nah_fam {
    hawk_tuah("Invalid operation")
}"""
    }
]

custom_css = """
/* ... (keep your existing CSS) ... */
.input-group {
    background: rgba(255, 255, 255, 0.15);
    padding: 12px;
    border-radius: 8px;
    margin: 10px 0;
}
.input-title {
    font-weight: bold;
    margin-bottom: 8px;
    color: #ff9800;
}
"""

with gr.Blocks(css=custom_css, title="🔥 LAVA Playground") as app:
    gr.Markdown("""
    <div style="text-align: center">
        <h1>🔥 LAVA Script Playground</h1>
        <p><i>Run and test your LAVA code in this interactive environment</i></p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=7):
            code_input = gr.Code(
                label="LAVA Code",
                language="python",
                lines=20,
                value=EXAMPLES[0]["code"],
                elem_id="code-input"
            )
            
            with gr.Row():
                run_btn = gr.Button("Run Code 🔥", variant="primary")
                clear_btn = gr.Button("Clear Output")
                download_btn = gr.Button("Download .lava", elem_classes="download-btn")
            
            with gr.Group(elem_classes="option-group"):
                gr.Markdown("<div class='option-title'>Debug Options</div>")
                with gr.Row():
                    show_tokens = gr.Checkbox(label="Show Tokens", value=False)
                    show_ast = gr.Checkbox(label="Show AST", value=False)
            
            # Dynamic input fields will be added here by the analysis
            input_fields = []
            
            output = gr.Textbox(
                label="Execution Output",
                lines=8,
                elem_classes="output-text"
            )
        
        with gr.Column(scale=3):
            gr.Markdown("## Example Programs")
            for example in EXAMPLES:
                with gr.Group(elem_classes="example-card"):
                    gr.Markdown(f"""
                    <div class="example-name">{example['name']}</div>
                    """)
                    gr.Textbox(
                        value=example['code'],
                        lines=min(10, example['code'].count('\n') + 1),
                        interactive=False,
                        elem_classes="example-code",
                        show_label=False
                    )
                    example_btn = gr.Button(f"Load: {example['name']}", size="sm")
                    example_btn.click(
                        fn=lambda code=example['code']: code,
                        inputs=[],
                        outputs=code_input
                    )
    
    def analyze_code(code):
        """Analyze code to determine needed inputs"""
        try:
            tokens = tokenize(code)
            ast = parse(tokens)
            input_count = count_inputs(ast)
            
            # Create input components
            inputs = []
            for i in range(input_count):
                inputs.append(gr.Textbox(label=f"Input {i+1}", visible=True))
            
            # Pad with hidden inputs if needed
            while len(inputs) < 5:  # Show at least 5 input fields
                inputs.append(gr.Textbox(visible=False))
            
            return inputs
        except:
            # Return default hidden inputs if analysis fails
            return [gr.Textbox(visible=False) for _ in range(5)]
    
    def count_inputs(ast):
        """Count gimme calls in AST"""
        count = 0
        for node in ast:
            count += _count_inputs_in_node(node)
        return count
    
    def _count_inputs_in_node(node):
        if not isinstance(node, (list, tuple)):
            return 0
        
        count = 0
        if node[0] == 'CALL' and node[1] == 'gimme':
            count += 1
        
        for item in node:
            count += _count_inputs_in_node(item)
        
        return count
    
    code_input.change(
        fn=analyze_code,
        inputs=code_input,
        outputs=[input_fields]
    )
    
    run_btn.click(
        fn=run_lava_code,
        inputs=[code_input, show_tokens, show_ast] + input_fields,
        outputs=output
    )
    
    clear_btn.click(
        fn=lambda: "",
        inputs=[],
        outputs=output
    )
    
    download_btn.click(
        fn=download_code,
        inputs=code_input,
        outputs=gr.File(label="Download LAVA File")
    )

if __name__ == "__main__":
    app.launch(share=False)