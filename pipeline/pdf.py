"""Shared utilities: MinerU API, LLM calls, JSON parsing, markdown chunking."""

import json
import os
import re
import time
import zipfile
import io

import pymupdf
import requests
from openai import OpenAI

from .config import Config


# ── MinerU API ──

# MinerU's hosted API rejects any single file over this many pages, so larger
# books are split into chunks of this size before upload.
MINERU_PAGE_LIMIT = 200

def mineru_upload_and_parse(pdf_path: str, config: Config) -> str:
    """Upload PDF to MinerU API, wait for result, return markdown."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.mineru_token}",
    }
    body = {
        "files": [{"name": os.path.basename(pdf_path), "is_ocr": False}],
        "enable_formula": True,
        "enable_table": True,
    }

    resp = requests.post(f"{config.mineru_api_url}/file-urls/batch", headers=headers, json=body)
    resp.raise_for_status()
    data = resp.json()["data"]
    batch_id = data["batch_id"]

    with open(pdf_path, "rb") as f:
        requests.put(data["file_urls"][0], data=f).raise_for_status()

    print(f"  Uploaded, batch_id={batch_id}, waiting...", end=" ", flush=True)

    result_url = f"{config.mineru_api_url}/extract-results/batch/{batch_id}"
    for _ in range(120):
        time.sleep(5)
        r = requests.get(result_url, headers=headers)
        r.raise_for_status()
        result = r.json()["data"]["extract_result"][0]
        if result["state"] == "done":
            print("done.")
            # The CDN occasionally drops the connection mid-download; one transient
            # blip should not waste the whole (already-parsed) chunk, so retry.
            for attempt in range(4):
                try:
                    zip_resp = requests.get(result["full_zip_url"], timeout=120)
                    zip_resp.raise_for_status()
                    break
                except requests.exceptions.RequestException:
                    if attempt == 3:
                        raise
                    time.sleep(3 * (attempt + 1))
            with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as zf:
                for name in zf.namelist():
                    if name.endswith(".md"):
                        return zf.read(name).decode("utf-8")
            return ""
        elif result["state"] == "failed":
            print(f"failed: {result.get('err_msg', 'unknown')}")
            return ""
        print(".", end="", flush=True)

    print("timeout")
    return ""


def pdf_to_markdown(pdf_path: str, config: Config, cache_dir: str) -> str:
    """Convert PDF to markdown via MinerU API. Splits large PDFs. Caches results."""
    os.makedirs(cache_dir, exist_ok=True)
    base_name = os.path.basename(pdf_path).replace(".pdf", "")
    md_cache = os.path.join(cache_dir, f"{base_name}.md")

    if os.path.exists(md_cache):
        with open(md_cache) as f:
            md = f.read()
        print(f"  [cached] {base_name}: {len(md)} chars")
        return md

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    if total_pages <= MINERU_PAGE_LIMIT:
        print(f"  [MinerU] Parsing {base_name} ({total_pages} pages)...")
        md = mineru_upload_and_parse(pdf_path, config)
    else:
        split_dir = os.path.join(cache_dir, "splits")
        os.makedirs(split_dir, exist_ok=True)
        chunk_pages = MINERU_PAGE_LIMIT
        doc = pymupdf.open(pdf_path)
        parts_md = []

        for start in range(0, total_pages, chunk_pages):
            end = min(start + chunk_pages, total_pages)
            part_name = f"{base_name}_p{start + 1}_{end}"
            part_cache = os.path.join(cache_dir, f"{part_name}.md")

            if os.path.exists(part_cache):
                with open(part_cache) as f:
                    part_md = f.read()
                print(f"  [cached] {part_name}: {len(part_md)} chars")
            else:
                split_path = os.path.join(split_dir, f"{part_name}.pdf")
                if not os.path.exists(split_path):
                    split_doc = pymupdf.open()
                    split_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
                    split_doc.save(split_path)
                    split_doc.close()

                print(f"  [MinerU] Parsing {part_name}...")
                part_md = mineru_upload_and_parse(split_path, config)
                if part_md:
                    with open(part_cache, "w") as f:
                        f.write(part_md)

            if part_md:
                parts_md.append(part_md)

        doc.close()
        md = "\n".join(parts_md)

    if md:
        with open(md_cache, "w") as f:
            f.write(md)
        print(f"  [MinerU] Total: {len(md)} chars")
    return md or ""


# ── LLM ──

def call_llm(client: OpenAI, config: Config, system: str, user: str) -> str:
    """Call LLM with retry."""
    for attempt in range(config.max_retries):
        try:
            resp = client.chat.completions.create(
                model=config.model_id,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            content = resp.choices[0].message.content
            if content:
                return content
        except Exception as e:
            print(f"  LLM error (attempt {attempt + 1}): {e}")
            if attempt < config.max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return "[]"


# ── JSON parsing ──

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return text


def parse_json_array(text: str) -> list:
    """Parse JSON array from LLM response."""
    text = _strip_fences(text)
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    print("  Warning: failed to parse JSON array, skipping")
    return []


def parse_json_object(text: str) -> dict:
    """Parse JSON object from LLM response."""
    text = _strip_fences(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {}


# ── Markdown chunking ──

def chunk_by_lines(md: str, lines_per_chunk: int = 300) -> list[tuple[str, str]]:
    """Split markdown by line count. Returns [(label, content), ...]."""
    lines = md.split("\n")
    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        content = "\n".join(lines[i : i + lines_per_chunk])
        if len(content.strip()) < 200:
            continue
        label = f"lines {i + 1}-{min(i + lines_per_chunk, len(lines))}"
        chunks.append((label, content))
    return chunks


def chunk_by_sections(md: str, max_chars: int = 10000) -> list[str]:
    """Split markdown on section boundaries."""
    if len(md) <= max_chars:
        return [md]

    parts = re.split(r'\n(?=#+\s|\d+\.\s*\d+\s)', md)
    chunks, current = [], ""
    for part in parts:
        if len(current) + len(part) > max_chars and current:
            chunks.append(current)
            current = part
        else:
            current += ("\n" if current else "") + part
    if current:
        chunks.append(current)
    return chunks
