"""Validate bilingual guide structure and Python snippets without network or session access."""

import ast
import inspect
import json
from pathlib import Path
import subprocess

import fncbale

ROOT = Path(__file__).resolve().parents[1]


def main():
    script = "global.window={}; require('./docs/site/content.js'); process.stdout.write(JSON.stringify(window.FNC_DOCS));"
    output = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True)
    docs = json.loads(output.stdout)
    assert docs["version"] == fncbale.__version__, "Guide and SDK release versions differ"
    ids = {page["id"] for page in docs["pages"]}
    assert len(ids) == len(docs["pages"])
    examples = 0
    sections = 0

    def bilingual(value):
        if isinstance(value, dict):
            if "fa" in value or "en" in value:
                assert value.get("fa", "").strip() and value.get("en", "").strip(), "Missing translation"
            for item in value.values():
                bilingual(item)
        elif isinstance(value, list):
            for item in value:
                bilingual(item)

    bilingual(docs)
    for page in docs["pages"]:
        anchors = [section["id"] for section in page["sections"]]
        assert len(anchors) == len(set(anchors))
        sections += len(anchors)
        for section in page["sections"]:
            for block in section["blocks"]:
                if block["type"] == "cards":
                    assert all(item["route"] in ids for item in block["items"])
                if block["type"] != "code" or block["language"] != "python":
                    continue
                source = block["source"]
                compile(
                    source,
                    f"{page['id']}/{section['id']}/{block['label']}",
                    "exec",
                    ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                )
                examples += 1
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module == "fncbale":
                        assert all(hasattr(fncbale, item.name) for item in node.names)
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "client"
                    ):
                        method = getattr(fncbale.Client, node.func.attr)
                        args = [None] * (1 + len(node.args))
                        kwargs = {item.arg: None for item in node.keywords if item.arg}
                        inspect.signature(method).bind(*args, **kwargs)
    for font in ("Manrope", "Vazirmatn"):
        assert (ROOT / f"docs/site/assets/{font}.woff2").read_bytes()[:4] == b"wOF2"
        assert (ROOT / f"docs/site/assets/{font}-OFL.txt").is_file()
    print(
        json.dumps(
            {
                "pass": True,
                "pages": len(ids),
                "languages": ["fa", "en"],
                "sections": sections,
                "python_examples": examples,
                "sdk_signatures_checked": True,
            }
        )
    )


if __name__ == "__main__":
    main()
