import nbformat

nb = nbformat.read("pizarra1MA(1).ipynb", as_version=4)

nb.metadata.pop("title", None)
nb.metadata.pop("authors", None)
nb.metadata.pop("date", None)

nbformat.write(nb, "pizarra1MA(1).ipynb")
