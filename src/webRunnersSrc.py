# gradio_interface.py
import sys
import io
import gradio as gr
import tempfile
import os
from lexer import tokenize
from parser import parse
from interpreter import run, Environment

def run_lava_code(code, show_tokens=False, show_ast=False):
    """Execute LAVA code and capture output/errors"""
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
    # Create a temporary file with .lava extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".lava")
    try:
        # Write code to the temporary file
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Return the file path for download
        return temp_file.name
    except Exception as e:
        # Clean up if error occurs
        os.unlink(temp_file.name)
        raise e

# Predefined examples
EXAMPLES = [
    {
        "name": "Complex Function Example",
        "code": """cook gyatt() {
  hawk_tuah("Hello World")
  hawk_tuah(1 + 2)
  sigma a = 10
  sigma b = 20 - 15
  yap i till 0 to 3 {
    hawk_tuah(i)
  }
  sigma i = 0
  flex i < 3 {
    hawk_tuah(i)
    sigma i = i + 1
  }
  rizz_check a > b {
    yeet a
  } nah_fam {
    yeet b
  }
  skibidi
}
hawk_tuah(gyatt())"""
    },
    {
        "name": "Array Functionalities",
        "code": """
        squad x = [10, 20, 30, 40, 50]
squad arr = x

on_read{// Access last element}
hawk_tuah(arr[-1])  

on_read{// Access second last element}
hawk_tuah(arr[-2])  

on_read{// Assign using negative index}
arr[-1] = 99
hawk_tuah(arr[4])   
hawk_tuah(arr)   
        """
    },
    {
        "name": "Factorial Calculator",
        "code": """cook factorial(){
    sigma n = 5
    sigma product = 1
    flex n > 0{
        sigma product = product * n
        sigma n = n - 1
    }
    yeet product
}

hawk_tuah(factorial())"""
    }
]

# Custom CSS with updated colors
custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #ff9966, #ff5e62);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.dark .gradio-container {
    background: linear-gradient(135deg, #2c3e50, #4a235a);
}
#code-input {
    font-family: 'Fira Code', monospace !important;
    font-size: 14px !important;
}
.output-text {
    font-family: monospace;
    white-space: pre;
}
.example-card {
    border: 1px solid #ff9966;
    border-radius: 8px;
    padding: 12px;
    margin: 10px 0;
    background: rgba(255, 255, 255, 0.1);
    cursor: pointer;
}
.example-card:hover {
    background: rgba(255, 255, 255, 0.2);
}
.example-name {
    font-weight: bold;
    color: #1e88e5; /* Changed to blue */
    margin-bottom: 8px;
}
.example-code {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    white-space: pre;
    background: rgba(0, 0, 0, 0.1);
    padding: 10px;
    border-radius: 4px;
    max-height: 200px;
    overflow: auto;
}
.option-group {
    background: rgba(255, 255, 255, 0.15);
    padding: 12px;
    border-radius: 8px;
    margin: 10px 0;
}
.option-title {
    font-weight: bold;
    margin-bottom: 8px;
    color: #43a047; /* Changed to green */
}
.download-btn {
    background: linear-gradient(135deg, #1e88e5, #0d47a1) !important;
    color: white !important;
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
            
            # Debug options with new color
            with gr.Group(elem_classes="option-group"):
                gr.Markdown("<div class='option-title'>Debug Options</div>")
                with gr.Row():
                    show_tokens = gr.Checkbox(label="Show Tokens", value=False)
                    show_ast = gr.Checkbox(label="Show AST", value=False)
            
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
                    
                    # Use Textbox for proper code formatting
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
    
    run_btn.click(
        fn=run_lava_code,
        inputs=[code_input, show_tokens, show_ast],
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
    app.launch(share = True)