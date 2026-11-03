from pathlib import Path

import nbformat
from nbclient import NotebookClient

p = Path("tutorial.ipynb")
nb = nbformat.read(p, as_version=4)
nbformat.validate(nb)
client = NotebookClient(
    nb, timeout=60, kernel_name="python3", resources={"metadata": {"path": str(Path.cwd())}}
)
client.execute()
print("Notebook 離線執行通過：", Path.cwd().name, len(nb.cells), "個區塊")
