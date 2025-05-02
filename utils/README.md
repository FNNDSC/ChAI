# 🧠 docling-batch

`docling-batch` is a flexible CLI tool for batch-converting documents from folders, files, GitHub repositories (with optional subfolders), and public URLs into Markdown, text, and structured formats like JSON/YAML — using the power of [Docling](https://github.com/docling-project/docling).

---

## 🚀 Features

Supports many input formats: `.adoc`, `.pdf`, `.docx`, `.html`, `.pptx`, `.xlsx`, `.odt`, `.rst`, etc.  
Converts GitHub repos, local folders/files, or direct URLs  
Outputs: `markdown`, `txt`, `json`, `html`, `yaml`, `doctags`  
CLI-based, pip-installable, production-ready  

---

## 📦 Installation

1. Clone or download this repo:

```bash
git clone https://github.com/FNNDSC/ChAI/tree/main
cd utils
```

2. Install the tool locally:

```bash
pip install .
```

3. You can now run:

```bash
docling-batch --help
```

---

## 🧪 Usage Examples

### 🔄 Convert a subfolder of a GitHub repo

```bash
docling-batch https://github.com/FNNDSC/chili.git:doc ./out --formats markdown txt
```

### 📂 Convert a local folder

```bash
docling-batch ./docs ./output --formats markdown json
```

### 📄 Convert a local file

```bash
docling-batch ./example.docx ./out --formats markdown
```

### 🌐 Convert a public PDF or DOCX URL

```bash
docling-batch https://arxiv.org/pdf/2408.09869 ./out --formats txt
```

---

## 🧾 Output Format Options

Use the `--formats` flag to choose one or more:

- `markdown` → `.md`
- `txt` → plain text from markdown
- `json` → structured JSON output
- `html` → converted HTML
- `yaml` → structured YAML format
- `doctags` → line-level semantic tags

---

## 🧠 Input Source Types

| Source           | Description                                      |
|------------------|--------------------------------------------------|
| Local folder      | Recursively converts all supported files         |
| Local file        | Converts a single file                           |
| GitHub repo       | Use `https://...repo.git`                        |
| GitHub subfolder  | Use `https://...repo.git:subfolder/path`         |
| Public file URL   | Works with `.pdf`, `.docx`, `.html`, etc.        |

---

## 🧼 Clean Uninstall

To remove the tool:

```bash
pip uninstall docling-batch
```

---

## ⚙️ Development

To update the code and reinstall:

```bash
pip install --upgrade .
```

---

## 📜 License

MIT License.

---

## 🤝 Acknowledgments

Powered by [Docling](https://github.com/docling-project/docling), a universal document parser designed for AI workflows.
