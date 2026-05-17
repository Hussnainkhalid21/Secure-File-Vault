"""
obfuscated_checker.py
---------------------
Analyses a filename for obfuscation and spoofing techniques.

Checks for:
  • Executable extensions (.exe, .bat, .cmd, etc.)
  • Double extensions masquerading as harmless files (document.pdf.exe)
  • Very long filenames (> 100 chars)
  • Unicode / homoglyph characters in the name
  • Base64-like or hex-encoded names
  • Right-to-left override (RTLO) Unicode trick
  • Spaces before extension to hide the real extension

Risk levels: Low | Medium | High
"""

import os
import re
import unicodedata


EXECUTABLE_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".scr", ".vbs", ".js", ".ps1",
    ".sh", ".msi", ".dll", ".com", ".hta", ".jar", ".py",
    ".rb", ".pl", ".php", ".wsf", ".pif",
}

HARMLESS_LOOKING = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".txt", ".mp3", ".mp4"}

# RTLO Unicode character used to reverse displayed filename
RTLO_CHAR = "\u202e"

# Regex for base64-like patterns (long strings of base64 chars)
BASE64_RE = re.compile(r"^[A-Za-z0-9+/]{20,}={0,2}$")
HEX_RE = re.compile(r"^[0-9a-fA-F]{16,}$")


def _has_unicode_tricks(name: str) -> list:
    """Detect homoglyphs, RTLO, and non-ASCII control characters."""
    issues = []
    if RTLO_CHAR in name:
        issues.append("Right-to-left override (RTLO) character detected — filename is visually reversed!")
    for ch in name:
        cat = unicodedata.category(ch)
        # Cf = Format characters (invisible), Cc = Control characters
        if cat in ("Cf", "Cc") and ch not in ("\t", "\n", "\r"):
            issues.append(f"Hidden Unicode control character (U+{ord(ch):04X}) in filename.")
            break
    return issues


def check_obfuscated(filename: str) -> dict:
    """
    Analyse the filename and return an obfuscation risk report.

    Returns:
        {
            "filename":    str,
            "risk_level":  "Low" | "Medium" | "High",
            "score":       int,      # cumulative risk points
            "flags":       [ str ],  # list of detected issues
            "recommendation": str,
        }
    """
    flags = []
    score = 0  # Each detected issue adds points; total determines risk level

    name_only = os.path.basename(filename)
    parts = name_only.split(".")
    # All extensions (last element is the final extension)
    all_exts = ["." + p.lower() for p in parts[1:]] if len(parts) > 1 else []
    final_ext = all_exts[-1] if all_exts else ""

    # 1. Executable final extension
    if final_ext in EXECUTABLE_EXTENSIONS:
        flags.append(f"Executable extension detected: '{final_ext}'")
        score += 40

    # 2. Double extension — harmless ext followed by executable ext
    if len(all_exts) >= 2 and all_exts[-2] in HARMLESS_LOOKING and final_ext in EXECUTABLE_EXTENSIONS:
        flags.append(
            f"Double-extension spoofing: appears to be '{all_exts[-2]}' but is actually '{final_ext}'"
        )
        score += 30  # already counted executable above; this adds context

    # 3. Very long filename
    if len(name_only) > 100:
        flags.append(f"Very long filename ({len(name_only)} characters) — may be used to hide the real extension.")
        score += 20

    # 4. Spaces before extension (e.g. "invoice.pdf          .exe")
    if "  " in name_only or name_only != name_only.rstrip():
        flags.append("Excessive whitespace in filename — possible extension hiding attempt.")
        score += 25

    # 5. Unicode tricks
    unicode_issues = _has_unicode_tricks(name_only)
    for issue in unicode_issues:
        flags.append(issue)
        score += 35

    # 6. Base64 or hex-encoded name (excluding extension)
    stem = parts[0] if parts else name_only
    if BASE64_RE.match(stem):
        flags.append("Filename stem looks like a Base64-encoded string — may be obfuscated.")
        score += 15
    elif HEX_RE.match(stem):
        flags.append("Filename stem looks like a hex-encoded string.")
        score += 10

    # 7. No extension at all — can hide file type
    if not final_ext:
        flags.append("No file extension — file type is unknown.")
        score += 10

    # Determine risk level from cumulative score
    if score >= 50:
        risk_level = "High"
        recommendation = "Do NOT open or execute this file. It shows strong signs of malicious obfuscation."
    elif score >= 20:
        risk_level = "Medium"
        recommendation = "Exercise caution. Scan this file with an antivirus before opening."
    else:
        risk_level = "Low"
        recommendation = "Filename appears normal. Always verify content before executing."

    if not flags:
        flags.append("No suspicious patterns detected in the filename.")

    return {
        "filename": name_only,
        "risk_level": risk_level,
        "score": score,
        "flags": flags,
        "recommendation": recommendation,
    }
