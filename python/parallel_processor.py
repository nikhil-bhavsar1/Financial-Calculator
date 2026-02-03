"""
Multiprocessing wrapper for parallel PDF processing.
This module provides parallel processing capabilities to utilize multiple CPU cores.
"""

import multiprocessing as mp
from typing import Dict, Any, List, Optional, Tuple, Callable
import logging
import re

# Configure multiprocessing
mp.set_start_method('spawn', force=True)

logger = logging.getLogger(__name__)


def process_page_worker(args):
    """
    Worker function to process a single page.

    Args:
        args: Tuple of (page_num, page_text, config)

    Returns:
        Dictionary with page data including text, tables, items
    """
    page_num, page_text, config = args

    result = {
        'page_num': page_num,
        'text': page_text,
        'tables': [],
        'items': []
    }

    try:
        # Extract tables from page text
        if config.get('extract_tables', True):
            # Simple table detection based on alignment patterns
            lines = page_text.split('\n')
            tables = []

            for i, line in enumerate(lines):
                # Detect potential table rows (multiple numbers, aligned)
                numbers = re.findall(r'[\d,]+\.?\d*', line)
                if len(numbers) >= 2:
                    # This looks like a table row
                    tables.append({
                        'page': page_num,
                        'row': i,
                        'content': line
                    })

            result['tables'] = tables

        # Extract financial items
        if config.get('extract_items', True):
            # Basic item extraction logic
            lines = page_text.split('\n')
            for line in lines:
                if line.strip():
                    result['items'].append({
                        'page': page_num,
                        'text': line.strip()
                    })

    except Exception as e:
        logger.warning(f"Error processing page {page_num}: {e}")
        result['error'] = str(e)

    return result


def parallel_pdf_processor(pages_data, config, max_workers=None):
    """
    Process PDF pages in parallel using multiprocessing.

    Args:
        pages_data: List of (page_num, page_text) tuples
        config: Configuration dict for processing options
        max_workers: Maximum number of worker processes (defaults to CPU count)

    Returns:
        List of processed page results
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), 8)  # Cap at 8 workers to avoid memory issues

    logger.info(f"Starting parallel processing with {max_workers} workers for {len(pages_data)} pages")

    # Create pool of workers
    with mp.Pool(processes=max_workers) as pool:
        # Prepare arguments for each worker
        worker_args = [(page_num, page_text, config)
                       for page_num, page_text in pages_data]

        # Process pages in parallel
        results = pool.map(process_page_worker, worker_args)

    return results


class ParallelPDFParser:
    """Wrapper for parallel PDF parsing with progress tracking."""

    def __init__(self, config=None):
        self.config = config or {}
        self.max_workers = self.config.get('max_workers', min(mp.cpu_count(), 8))

    def process_pdf(self, pdf_path, progress_callback=None):
        """
        Process entire PDF in parallel with progress tracking.

        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback function for progress updates

        Returns:
            Dict with all extracted data
        """
        try:
            import fitz
        except ImportError:
            return {
                'status': 'error',
                'message': 'PyMuPDF not installed. Run: pip install PyMuPDF'
            }

        # Open PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        logger.info(f"Processing PDF with {total_pages} pages using {self.max_workers} workers")

        # Extract text from all pages first (this is fast)
        pages_data = []
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            pages_data.append((page_num, text))

            # Send initial progress for text extraction
            if progress_callback:
                progress = int((page_num + 1) / total_pages * 20)  # First 20% is text extraction
                progress_callback(
                    page_num + 1,
                    total_pages,
                    f'Extracted text from page {page_num + 1}/{total_pages}'
                )

        # Process pages in parallel
        if progress_callback:
            progress_callback(0, total_pages, 'Starting parallel analysis...')

        parallel_results = parallel_pdf_processor(
            pages_data,
            self.config,
            self.max_workers
        )

        # Combine results
        all_text = ""
        all_tables = []
        all_items = []

        for i, result in enumerate(parallel_results):
            # Update progress (80-100% range)
            if progress_callback:
                progress = 20 + int((i + 1) / len(parallel_results) * 80)
                progress_callback(
                    i + 1,
                    total_pages,
                    f'Processed {i + 1}/{len(parallel_results)} pages (analyzing data...)'
                )

            all_text += f"\n--- Page {result['page_num'] + 1} ---\n{result['text']}\n"
            all_tables.extend(result.get('tables', []))
            all_items.extend(result.get('items', []))

        # Close PDF
        doc.close()

        return {
            'status': 'success',
            'text': all_text,
            'tables': all_tables,
            'items': all_items,
            'total_pages': total_pages,
            'metadata': {
                'parallel_workers': self.max_workers,
                'processing_mode': 'parallel'
            }
        }


if __name__ == '__main__':
    # Test parallel processing
    import sys
    if len(sys.argv) > 1:
        parser = ParallelPDFParser()
        result = parser.process_pdf(sys.argv[1])
        print(f"Processed {result['total_pages']} pages")
        print(f"Found {len(result['items'])} items")
        print(f"Found {len(result['tables'])} tables")
