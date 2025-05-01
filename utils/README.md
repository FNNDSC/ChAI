# 📝 convert_adoc_to_md.py

This script clones a Git repository, finds `.adoc` (AsciiDoc) files, and converts them into `.md` (Markdown) using the [Docling](https://github.com/docling-project/docling) document parser. It's ideal for preparing content for Retrieval-Augmented Generation (RAG) pipelines.

---

## 🔧 Requirements

- Python 3.10
- `git` installed on your system
- Internet access to clone the Git repo

---

## 🚀 Setup and Usage (with `venv`)

### 1. Clone or download this script

```bash
git clone https://github.com/YOUR_ORG/your-repo.git
cd your-repo/utils  # or wherever convert_adoc_to_md.py is located
```

### 2. Create a Python virtual environment (recommended)

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install docling
```

### 4. Run the script

```bash
python convert_adoc_to_md.py https://github.com/FNNDSC/chili.git \
  --file-filter "doc/**/*.adoc" \
  --output-dir "./rag_markdown"
```

---

## 🗂 Output

Converted `.md` files will be saved in the specified `--output-dir`, maintaining the original folder structure.

Example output structure:

```
rag_markdown/
├── doc/
│   ├── intro.md
│   └── usage.md
```

---

## 🛠️ CLI Options

| Option          | Description                                | Default               |
|-----------------|--------------------------------------------|------------------------|
| `repo_url`      | Git URL of the repo to clone               | **(required)**         |
| `--file-filter` | Glob pattern to find `.adoc` files         | `*.adoc`               |
| `--output-dir`  | Folder where converted `.md` files go      | `converted_markdown/`  |

---

## ✅ Example Use Case

Convert only files inside the `doc/` folder of a repo:

```bash
python convert_adoc_to_md.py https://github.com/FNNDSC/chili.git \
  --file-filter "doc/**/*.adoc" \
  --output-dir "./rag_markdown"
```

---

## 🧹 Clean Up

To deactivate the virtual environment:

```bash
deactivate
```

To remove the virtual environment:

```bash
rm -rf .venv
```

---

## 📄 License

MIT License

---

## ✨ Credits

Built with ❤️ using [Docling](https://github.com/docling-project/docling).

