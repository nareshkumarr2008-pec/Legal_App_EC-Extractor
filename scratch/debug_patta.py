import sys
sys.path.insert(0, '.')

from app.extractors.patta_extractor import PattaExtractor

raw_text = """1. குப்புசாமி மகன் ஜானிகிராமன் -"""
ext = PattaExtractor()
clean = ext.clean_text_artifacts(raw_text)
print("Clean:", repr(clean))
owner_res = ext._format_patta_owner_bilingual(clean)
print("Owner res:", repr(owner_res))
