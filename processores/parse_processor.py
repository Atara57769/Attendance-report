import re
from typing import Optional


def extract_total_hours( text: str) -> Optional[float]:
        """Extract total hours from text."""
        match = re.search(r'total\s+hours?\s*:?\s*([\d.]+)', text, re.IGNORECASE)
        return float(match.group(1)) if match else None
    
def extract_total_days( text: str) -> Optional[int]:
    """Extract total days from text."""
    match = re.search(r'total\s+days?\s*:?\s*(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else None

