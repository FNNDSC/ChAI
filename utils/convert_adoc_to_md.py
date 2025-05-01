#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
import logging
from pathlib import Path

from docling.document_converter import DocumentConverter


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )


def clone_repo(repo_url, clone_path):
    logging.info(f"Cloning repository: {repo_url}")
    subprocess.run(["git", "clone", repo_url, str(clone_path)], check=True)
    logging.info(f"Repository cloned to: {clone_path}")


def find_adoc_files(repo_path, file_filter):
    logging.info(f"Searching for .adoc files with pattern: {file_filter}")
    return list(repo_path.rglob(file_filter))


def convert_file_to_md(adoc_file, base_path, output_dir, converter):
    relative_path = adoc_file.relative_to(base_path).with_suffix(".md")
    output_path = output_dir / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = converter.convert(str(adoc_file))
        output_path.write_text(result.document.export_to_markdown(), encoding="utf-8")
        logging.info(f"✅ Converted: {adoc_file} -> {output_path}")
    except Exception as e:
        logging.error(f"❌ Failed to convert {adoc_file}: {e}")


def convert_repo(repo_url, file_filter, output_dir):
    converter = DocumentConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        clone_path = Path(tmpdir) / "repo"
        clone_repo(repo_url, clone_path)

        adoc_files = find_adoc_files(clone_path, file_filter)
        if not adoc_files:
            logging.warning("No matching .adoc files found.")
            return

        for adoc_file in adoc_files:
            convert_file_to_md(adoc_file, clone_path, Path(output_dir), converter)


def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Convert AsciiDoc files in a Git repo to Markdown using Docling.")
    parser.add_argument("repo_url", help="URL of the Git repository")
    parser.add_argument("--file-filter", default="*.adoc", help="Glob pattern to match files (default: *.adoc)")
    parser.add_argument("--output-dir", default="converted_markdown", help="Directory to save Markdown output")

    args = parser.parse_args()
    convert_repo(args.repo_url, args.file_filter, args.output_dir)


if __name__ == "__main__":
    main()
