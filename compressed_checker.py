"""
compressed_checker.py
---------------------
Inspects ZIP and TAR archives without extracting them.
Detects:
  • Nested archives (archive within archive)
  • Double-extension files (e.g. document.pdf.exe)
  • Executable extensions hiding inside archives
  • Path traversal attempts (../ in file names)

Does NOT extract files — inspection only.
"""

import zipfile
import tarfile
import os


# Extensions that are executable / potentially dangerous
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".scr", ".vbs", ".js", ".ps1",
    ".sh", ".msi", ".dll", ".com", ".hta", ".jar",
}

# Archive-within-archive extensions
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".rar", ".7z"}


def _analyse_entry(name: str) -> dict:
    """Return analysis flags for a single archive entry name."""
    lower = name.lower()
    _, ext = os.path.splitext(lower)
    parts = lower.split(".")

    # Double extension: e.g.  report.pdf.exe  → ['report', 'pdf', 'exe']
    has_double_ext = len(parts) > 2 and parts[-1] in [e.lstrip(".") for e in DANGEROUS_EXTENSIONS]
    is_dangerous = ext in DANGEROUS_EXTENSIONS
    is_nested_archive = ext in ARCHIVE_EXTENSIONS
    has_path_traversal = ".." in name

    risks = []
    if has_double_ext:
        risks.append("double extension")
    if is_dangerous:
        risks.append("executable extension")
    if is_nested_archive:
        risks.append("nested archive")
    if has_path_traversal:
        risks.append("path traversal")

    return {
        "name": name,
        "extension": ext,
        "risks": risks,
        "suspicious": bool(risks),
    }


def check_compressed(file_path: str) -> dict:
    """
    Inspect a ZIP or TAR archive and return a safety report.

    Returns:
        {
            "format":         "zip" | "tar",
            "total_files":    int,
            "entries":        [ { name, extension, risks, suspicious }, ... ],
            "suspicious_count": int,
            "warnings":       [ str, ... ],
            "safe_to_extract": bool,
        }
    Raises ValueError for unsupported or unreadable archives.
    """
    entries = []
    warnings = []
    archive_format = None

    if zipfile.is_zipfile(file_path):
        archive_format = "zip"
        with zipfile.ZipFile(file_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                entry = _analyse_entry(info.filename)
                entry["compressed_size"] = info.compress_size
                entry["original_size"] = info.file_size
                entries.append(entry)

    elif tarfile.is_tarfile(file_path):
        archive_format = "tar"
        with tarfile.open(file_path, "r:*") as tf:
            for member in tf.getmembers():
                if member.isdir():
                    continue
                entry = _analyse_entry(member.name)
                entry["compressed_size"] = member.size
                entry["original_size"] = member.size
                entries.append(entry)
    else:
        raise ValueError(
            "Unsupported archive format. Please upload a ZIP or TAR file."
        )

    suspicious_entries = [e for e in entries if e["suspicious"]]
    suspicious_count = len(suspicious_entries)

    if suspicious_count > 0:
        warnings.append(
            f"{suspicious_count} suspicious file(s) detected inside the archive."
        )
    if any("path traversal" in e["risks"] for e in entries):
        warnings.append(
            "Path traversal detected — extracting this archive could overwrite system files!"
        )
    if any("nested archive" in e["risks"] for e in entries):
        warnings.append(
            "Nested archive(s) found — recursive extraction may hide malicious content."
        )

    safe_to_extract = suspicious_count == 0

    return {
        "format": archive_format,
        "total_files": len(entries),
        "entries": entries,
        "suspicious_count": suspicious_count,
        "warnings": warnings,
        "safe_to_extract": safe_to_extract,
    }
