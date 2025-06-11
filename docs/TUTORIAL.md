Here's a complete `tutorial.md` draft for **BS-Lang** with instructions to launch the web interface using Gradio, what features it supports, and setup guidance:

---

# 🐂 BS-Lang: Getting Started Tutorial

Welcome to **BS-Lang**, a meme-inspired programming language with Gen Z slang syntax!
This tutorial will guide you through running the **web-based editor** where you can write, run, and test BS-Lang code.

---

## 🚀 Running the Web Interface

To launch the BS-Lang web interface and start coding:

### 📦 Step 1: Install Dependencies

Make sure you have **Python 3.8+** installed.
Then install **Gradio** (used to power the web interface):

```bash
pip install gradio
```

### 🧠 Step 2: Launch the Editor

Navigate to the following directory in your terminal:

```bash
cd src/
```

Then run the editor with:

```bash
python webRunnersSrc.py
```

This will launch a local Gradio-based web interface in your browser.

---

## 🖥️ Editor Features

Once the BS-Lang web interface is running, here’s what you can do:

### ✅ Supported Features

* **🧠 AST Viewer**
  Get the full Abstract Syntax Tree of your BS-Lang program.

* **🧾 Token Inspector**
  View the tokenized breakdown of your code.

* **🚀 Code Execution (no REPL)**
  Runs the entire BS-Lang program with an output window for results.

* **💻 Online Code Editor**
  Write and edit code directly in your browser.

* **📂 Load Examples**
  Load built-in example programs to explore BS-Lang features.

* **💾 Download Your Code**
  Save your written code locally with the click of a button.

* **⌨️ Input Handler**
  Supports `input()` equivalent in BS-Lang — if your code requests input, the editor prompts accordingly.

---

## 🧪 Example

You can load examples from the dropdown and hit **Run** to see how BS-Lang works.

Example snippet:

```bs
cook main() {
  sigma a = 5
  sigma b = 6
  hawk_tuah("Sum is:", a + b)
}
```

---

## 🛠️ Notes

* The interface **does not support REPL-style input**, but all `input()` functions in BS-Lang are handled by a custom prompt.
* Make sure Gradio is installed and up to date for smooth functioning.

---

## 🤖 Contribution & Issues

Want to add more Gen Z slang? Found a bug?
Feel free to contribute or open issues in the repository.

---

Let me know when your `webRunnersSrc.py` is ready or if you want the markdown updated with live preview screenshots, buttons, or contributor info. it is adviced to add the changes into the `garage` directory
