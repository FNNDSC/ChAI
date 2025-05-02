import argparse
import logging
import tempfile
import shutil
import subprocess
import yaml
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from docling.document_converter import DocumentConverter

SUPPORTED_INPUT_EXTS = {
    ".md", ".adoc", ".pdf", ".docx", ".html", ".htm", ".txt", ".pptx",
    ".xls", ".xlsx", ".odt", ".ods", ".odp", ".tex", ".rst"
}


def is_url(path_or_url: str) -> bool:
    return path_or_url.startswith("http://") or path_or_url.startswith("https://")


def is_git_repo_url(url: str) -> bool:
    return url.endswith(".git") or "github.com" in url


def clone_git_repo(repo_url: str, subdir: str = "") -> Path:
    temp_dir = Path(tempfile.mkdtemp())
    subprocess.run(["git", "clone", repo_url, str(temp_dir)], check=True)
    repo_path = temp_dir / subdir if subdir else temp_dir
    if not repo_path.exists():
        raise FileNotFoundError(f"Subdirectory '{subdir}' not found in repo {repo_url}")
    return repo_path


def export_docling_outputs(document, doc_name: str, output_dir: Path, formats: List[str]):
    output_dir.mkdir(parents=True, exist_ok=True)

    if "json" in formats:
        document.save_as_json(output_dir / f"{doc_name}.json")

    if "html" in formats:
        document.save_as_html(output_dir / f"{doc_name}.html")

    if "markdown" in formats or "md" in formats:
        document.save_as_markdown(output_dir / f"{doc_name}.md")

    if "txt" in formats:
        document.save_as_markdown(output_dir / f"{doc_name}.txt", strict_text=True)

    if "yaml" in formats:
        with open(output_dir / f"{doc_name}.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(document.export_to_dict(), f)

    if "doctags" in formats:
        with open(output_dir / f"{doc_name}.doctags.txt", "w", encoding="utf-8") as f:
            f.write(document.export_to_document_tokens())


def convert_all_supported_files(input_dir: Path, output_dir: Path, formats: List[str]):
    logger = logging.getLogger("docling_batch")
    converter = DocumentConverter()

    all_files = [f for f in input_dir.rglob("*") if f.suffix.lower() in SUPPORTED_INPUT_EXTS]
    logger.info(f"🔍 Found {len(all_files)} supported input files.")

    for input_file in all_files:
        try:
            result = converter.convert(str(input_file))
            if hasattr(result, "document"):
                relative_path = input_file.relative_to(input_dir).parent
                output_subdir = output_dir / relative_path
                export_docling_outputs(result.document, input_file.stem, output_subdir, formats)
            else:
                logger.warning(f"⚠️ No document generated for {input_file}")
        except Exception as e:
            logger.error(f"💥 Exception while converting {input_file}: {e}")


def convert_single_url(input_url: str, output_dir: Path, formats: List[str]):
    logger = logging.getLogger("docling_batch")
    converter = DocumentConverter()

    try:
        result = converter.convert(input_url)
        if hasattr(result, "document"):
            name = Path(urlparse(input_url).path).stem or "document"
            export_docling_outputs(result.document, name, output_dir, formats)
        else:
            logger.warning(f"⚠️ No document returned for URL: {input_url}")
    except Exception as e:
        logger.error(f"💥 Error converting URL {input_url}: {e}")


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("docling_batch")

    parser = argparse.ArgumentParser(description="Convert any supported input (folder, repo, URL) using Docling.")
    parser.add_argument("input", help="Local path, repo URL, or document URL")
    parser.add_argument("output_dir", type=Path, help="Directory to write outputs")
    parser.add_argument("--formats", nargs="+", default=["markdown"], choices=["markdown", "txt", "json", "html", "yaml", "doctags"],
                        help="Output formats to generate")
    args = parser.parse_args()

    input_arg = args.input
    output_dir = args.output_dir
    formats = args.formats

    if is_url(input_arg):
        if is_git_repo_url(input_arg):
            # ✅ Split only at the last colon to support URLs with ':' in them
            repo_url, subdir = input_arg.rsplit(":", 1) if ".git:" in input_arg else (input_arg, "")
            logger.info(f"📥 Cloning Git repo: {repo_url} subdir: {subdir}")
            repo_path = clone_git_repo(repo_url, subdir)
            convert_all_supported_files(repo_path, output_dir, formats)
            shutil.rmtree(repo_path.parent)  # cleanup temp clone
        else:
            logger.info(f"🌐 Converting remote document/website: {input_arg}")
            convert_single_url(input_arg, output_dir, formats)
    else:
        input_path = Path(input_arg)
        if input_path.is_dir():
            logger.info(f"📂 Converting local folder: {input_path}")
            convert_all_supported_files(input_path, output_dir, formats)
        elif input_path.is_file():
            logger.info(f"📄 Converting local file: {input_path}")
            convert_single_url(str(input_path.resolve()), output_dir, formats)
        else:
            raise FileNotFoundError(f"Invalid input path: {input_arg}")


if __name__ == "__main__":
    main()
