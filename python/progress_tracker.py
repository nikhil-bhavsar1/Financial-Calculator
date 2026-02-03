"""
Progress callback module for streaming partial results during parsing.
"""

import sys
import json
from typing import Optional, Callable, Any, List

# Global callback for progress updates
_progress_callback: Optional[Callable] = None

def set_progress_callback(callback: Optional[Callable]):
    """Set the global progress callback for streaming results."""
    global _progress_callback
    _progress_callback = callback

def send_progress(current_page: int, total_pages: int, status_message: str = "",
                partial_items: Optional[List[Any]] = None,
                partial_text: Optional[str] = None):
    """Send progress update with optional partial data."""
    global _progress_callback

    # Call callback if set
    if _progress_callback:
        try:
            _progress_callback(total_pages, current_page, status_message, partial_items, partial_text)
        except Exception as e:
            print(f"[Progress] Callback error: {e}", file=sys.stderr)

    # Also emit to stdout for Rust bridge
    percentage = int((current_page / total_pages) * 100) if total_pages > 0 else 0
    progress_data = {
        'status': 'progress',
        'currentPage': current_page,
        'totalPages': total_pages,
        'percentage': percentage,
        'message': status_message or f'Processing page {current_page} of {total_pages}'
    }

    if partial_items is not None:
        progress_data['partialItems'] = partial_items
    if partial_text is not None:
        progress_data['partialText'] = partial_text

    print(json.dumps(progress_data))
    sys.stdout.flush()

def clear_callback():
    """Clear the progress callback."""
    global _progress_callback
    _progress_callback = None
