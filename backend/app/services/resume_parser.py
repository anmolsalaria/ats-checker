"""Resume parser service.

Wraps file_parser.py and adds text extraction from uploaded files
plus LinkedIn URL import (Feature 10).
"""

from __future__ import annotations

import logging
import re

from app.services.file_parser import FileParser

logger = logging.getLogger(__name__)


class ResumeParser:
    """High-level resume parsing service."""

    SUPPORTED_TYPES = FileParser.SUPPORTED_TYPES

    @staticmethod
    def extract_from_file(content: bytes, content_type: str) -> str:
        """Extract text from an uploaded file (PDF/DOCX)."""
        return FileParser.extract_text(content, content_type)

    @staticmethod
    def extract_from_linkedin_url(url: str) -> str:
        """Attempt to extract job description from a LinkedIn URL.

        LinkedIn aggressively blocks scraping, so this is best-effort.
        If extraction fails, raises ValueError with a helpful message.
        """
        if not re.match(
            r"https?://(www\.)?linkedin\.com/jobs/view/", url, re.IGNORECASE
        ):
            raise ValueError(
                "Invalid LinkedIn URL. Expected format: "
                "https://www.linkedin.com/jobs/view/<job-id>"
            )

        try:
            import httpx
            from html.parser import HTMLParser

            class _TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self._text_parts: list[str] = []
                    self._in_body = False

                def handle_starttag(self, tag, attrs):
                    if tag == "body":
                        self._in_body = True

                def handle_endtag(self, tag):
                    if tag == "body":
                        self._in_body = False

                def handle_data(self, data):
                    if self._in_body:
                        cleaned = data.strip()
                        if cleaned:
                            self._text_parts.append(cleaned)

                def get_text(self) -> str:
                    return "\n".join(self._text_parts)

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.9",
            }

            resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=10)
            resp.raise_for_status()

            parser = _TextExtractor()
            parser.feed(resp.text)
            text = parser.get_text()

            if len(text) < 100:
                raise ValueError(
                    "Could not extract enough text from this LinkedIn URL. "
                    "LinkedIn may be blocking the request. "
                    "Please copy and paste the job description manually."
                )

            return text

        except ImportError:
            raise ValueError(
                "httpx is required for LinkedIn import. "
                "Install it with: pip install httpx"
            )
        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"LinkedIn extraction failed: {e}")
            raise ValueError(
                "Could not fetch the LinkedIn job posting. "
                "LinkedIn blocks automated access. "
                "Please copy and paste the job description text directly."
            )
