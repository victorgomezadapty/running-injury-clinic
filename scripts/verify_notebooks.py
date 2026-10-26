"""Execute active metadata/pilot notebook cells; later notebooks remain gated.

Uses an isolated namespace per notebook. This verifies actual cell code without
requiring a GUI or a Jupyter server/kernel. Execution mode is recorded explicitly.
"""
from pathlib import Path
import os
import ast
import contextlib
import io
import platform
import argparse
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    patterns = ["01_*.ipynb", "02_*.ipynb", "03_*.ipynb"]
    if not args.metadata_only:
        patterns.append("04_*.ipynb")
    for pattern in patterns:
        path = next((ROOT / "notebooks").glob(pattern))
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        namespace = {"__name__": "__main__"}
        count = 0
        for cell in book.cells:
            if cell.cell_type != "code":
                continue
            count += 1
            tree = ast.parse(cell.source)
            expression = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                exec(compile(tree, str(path), "exec"), namespace)
                result = eval(compile(ast.Expression(expression.value), str(path), "eval"), namespace) if expression else None
            cell.execution_count = count
            cell.outputs = []
            if stream.getvalue():
                cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=stream.getvalue()))
            if result is not None:
                data = {"text/plain": repr(result)}
                if hasattr(result, "_repr_html_"):
                    html = result._repr_html_()
                    if html:
                        data["text/html"] = html
                cell.outputs.append(nbformat.v4.new_output("execute_result", execution_count=count, data=data))
        book.metadata["verification"] = {"execution_mode": "in_process_python", "python_version": platform.python_version(), "note": "Cell code executed with a fresh namespace per notebook; Jupyter kernel/UI not verified."}
        nbformat.write(book, path)
        print(f"Executed and verified {path.name}", flush=True)
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        if int(path.name[:2]) >= 5:
            assert not any(cell.cell_type == "code" for cell in book.cells)
    print("All nine notebook files validated; later-stage notebooks contain no executable analysis.")


if __name__ == "__main__":
    main()
