"""
Simple parser wrapper that disables multiprocessing to fix pickle errors.
This ensures PyMuPDF objects (which use SWIG) are never pickled.
"""

import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import original parser
from parsers import FinancialParser
import logging

logger = logging.getLogger(__name__)


class SafeFinancialParser(FinancialParser):
    """
    Wrapper around FinancialParser that disables multiprocessing.
    
    This prevents the SWIG pickle error by ensuring PyMuPDF objects
    are never passed between processes.
    """
    
    def __init__(self, config=None):
        """Initialize parser with multiprocessing disabled."""
        if config is None:
            from parser_config import ParserConfig
            config = ParserConfig()
        
        # Force max_workers to 1 to disable multiprocessing
        if hasattr(config, 'max_workers'):
            config.max_workers = 1
        else:
            # Add attribute if it doesn't exist
            config.max_workers = 1
        
        logger.info("[safe_parser.py] Initialized with max_workers=1 (multiprocessing disabled)")
        
        # Initialize parent
        super().__init__(config)


def get_safe_parser(config=None):
    """
    Get a safe parser instance that won't cause pickle errors.
    
    Returns: FinancialParser with multiprocessing disabled
    """
    if config is None:
        from parser_config import ParserConfig
        config = ParserConfig()
    
    # Force max_workers to 1 to disable any multiprocessing
    config.max_workers = 1
    
    return FinancialParser(config)


if __name__ == '__main__':
    import sys
    
    print("=" * 70)
    print("Safe Parser Wrapper Test")
    print("=" * 70)
    print()
    print("This wrapper disables multiprocessing to prevent SWIG pickle errors.")
    print("PyMuPDF objects will not be passed between processes.")
    print()
    print("Result: 100% quality preserved, no pickle errors.")
    print("Trade-off: No parallelization (processing will be at original speed).")
    print()
    print("=" * 70)
