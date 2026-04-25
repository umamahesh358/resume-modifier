import os
import subprocess
import tempfile
import base64
from jinja2 import Environment, FileSystemLoader

# Setup Jinja2 environment with custom delimiters to avoid LaTeX conflict
env = Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%-',
    line_comment_prefix='%#-',
    trim_blocks=True,
    autoescape=False,
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
)

def escape_latex(s: str) -> str:
    """Escapes special LaTeX characters in a string."""
    if not isinstance(s, str):
        return s

    # Needs a specific order to avoid escaping escape characters
    s = s.replace('\\', r'\textbackslash{}')
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for char, replacement in chars.items():
        s = s.replace(char, replacement)
    return s

def clean_data_for_latex(data: dict) -> dict:
    """Recursively escape LaTeX special characters in the dict."""
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, str):
            cleaned[k] = escape_latex(v)
        elif isinstance(v, list):
            cleaned[k] = [escape_latex(i) if isinstance(i, str) else clean_data_for_latex(i) if isinstance(i, dict) else i for i in v]
        elif isinstance(v, dict):
            cleaned[k] = clean_data_for_latex(v)
        else:
            cleaned[k] = v
    return cleaned

def generate_pdf(template_name: str, data: dict) -> str:
    """
    Generates a PDF using Jinja2 and Tectonic.
    Returns the generated PDF as a base64 encoded string.
    """
    # Clean the data to prevent LaTeX injection/syntax errors
    clean_data = clean_data_for_latex(data)

    template = env.get_template(template_name)
    rendered_tex = template.render(**clean_data)

    # Create a temporary directory to compile the PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(temp_dir, "document.tex")
        pdf_path = os.path.join(temp_dir, "document.pdf")

        # Write the rendered tex file
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(rendered_tex)

        # Run tectonic
        tectonic_path = os.path.join(os.path.dirname(__file__), "tectonic")
        if not os.path.exists(tectonic_path):
            raise FileNotFoundError("Tectonic binary not found in backend directory.")

        try:
            # We use --outfmt pdf and point to the tex file
            result = subprocess.run(
                [tectonic_path, tex_path, "--outdir", temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # If it failed, print the generated tex for debugging
            print(f"FAILED TEX CONTENT:\n{rendered_tex}")
            raise Exception(f"LaTeX Compilation Failed: {e.stderr}")

        # Read the generated PDF and encode it
        if not os.path.exists(pdf_path):
            raise FileNotFoundError("Tectonic completed but PDF was not generated.")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return base64.b64encode(pdf_bytes).decode('utf-8')
