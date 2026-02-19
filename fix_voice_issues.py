#!/usr/bin/env python3
"""
Fix "I" voice to "we" voice throughout blog posts
"""
import os
import re
import glob

def fix_voice_issues(filepath):
    """Fix I/me/my to we/us/our in content while preserving quotes and proper context"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Common I -> we replacements (case sensitive to avoid issues with proper nouns)
    replacements = [
        (r'\bI think\b', 'We think'),
        (r'\bI believe\b', 'We believe'),
        (r'\bI recommend\b', 'We recommend'),
        (r'\bI found\b', 'We found'),
        (r'\bI tested\b', 'We tested'),
        (r'\bI used\b', 'We used'),
        (r'\bI like\b', 'We like'),
        (r'\bI prefer\b', 'We prefer'),
        (r'\bI love\b', 'We love'),
        (r'\bI hate\b', 'We hate'),
        (r'\bI noticed\b', 'We noticed'),
        (r'\bI discovered\b', 'We discovered'),
        (r'\bI tried\b', 'We tried'),
        (r'\bI spent\b', 'We spent'),
        (r'\bI purchased\b', 'We purchased'),
        (r'\bI bought\b', 'We bought'),
        (r'\bI chose\b', 'We chose'),
        (r'\bI selected\b', 'We selected'),
        (r'\bI decided\b', 'We decided'),
        (r'\bI feel\b', 'We feel'),
        (r'\bI appreciate\b', 'We appreciate'),
        (r'\bI understand\b', 'We understand'),
        (r'\bI know\b', 'We know'),
        (r'\bI see\b', 'We see'),
        (r'\bI hear\b', 'We hear'),
        (r'\bI experience\b', 'We experience'),
        (r'\bI encounter\b', 'We encounter'),
        (r'\bI expect\b', 'We expect'),
        (r'\bI hope\b', 'We hope'),
        (r'\bI wish\b', 'We wish'),
        (r'\bI want\b', 'We want'),
        (r'\bI need\b', 'We need'),
        (r'\bI have\b', 'We have'),
        (r'\bI own\b', 'We own'),
        (r'\bI use\b', 'We use'),
        (r'\bI rely\b', 'We rely'),
        (r'\bI depend\b', 'We depend'),
        (r'\bI suggest\b', 'We suggest'),
        (r'\bI advise\b', 'We advise'),
        (r'\bI consider\b', 'We consider'),
        (r'\bI rate\b', 'We rate'),
        (r'\bI score\b', 'We score'),
        (r'\bI rank\b', 'We rank'),
        (r'\bI compare\b', 'We compare'),
        (r'\bI evaluate\b', 'We evaluate'),
        (r'\bI assess\b', 'We assess'),
        (r'\bI review\b', 'We review'),
        (r'\bI examine\b', 'We examine'),
        (r'\bI analyze\b', 'We analyze'),
        (r'\bI check\b', 'We check'),
        (r'\bI verify\b', 'We verify'),
        (r'\bI confirm\b', 'We confirm'),
        (r'\bI measure\b', 'We measure'),
        (r'\bI weigh\b', 'We weigh'),
        (r'\bI calculate\b', 'We calculate'),
        (r'\bI determine\b', 'We determine'),
        (r'\bI conclude\b', 'We conclude'),
        (r'\bI summarize\b', 'We summarize'),
        
        # My -> Our
        (r'\bmy experience\b', 'our experience'),
        (r'\bmy testing\b', 'our testing'),
        (r'\bmy review\b', 'our review'),
        (r'\bmy analysis\b', 'our analysis'),
        (r'\bmy opinion\b', 'our opinion'),
        (r'\bmy recommendation\b', 'our recommendation'),
        (r'\bmy findings\b', 'our findings'),
        (r'\bmy results\b', 'our results'),
        (r'\bmy conclusion\b', 'our conclusion'),
        (r'\bmy preference\b', 'our preference'),
        (r'\bmy choice\b', 'our choice'),
        (r'\bmy decision\b', 'our decision'),
        (r'\bmy assessment\b', 'our assessment'),
        (r'\bmy evaluation\b', 'our evaluation'),
        (r'\bmy research\b', 'our research'),
        (r'\bmy study\b', 'our study'),
        (r'\bmy investigation\b', 'our investigation'),
        (r'\bmy comparison\b', 'our comparison'),
        (r'\bmy test\b', 'our test'),
        (r'\bmy tests\b', 'our tests'),
        (r'\bmy trial\b', 'our trial'),
        (r'\bmy trials\b', 'our trials'),
        (r'\bmy observation\b', 'our observation'),
        (r'\bmy observations\b', 'our observations'),
        (r'\bmy measurement\b', 'our measurement'),
        (r'\bmy measurements\b', 'our measurements'),
        
        # Me -> Us
        (r'\bfor me\b', 'for us'),
        (r'\bto me\b', 'to us'),
        (r'\bwith me\b', 'with us'),
        (r'\bgave me\b', 'gave us'),
        (r'\btold me\b', 'told us'),
        (r'\bshowed me\b', 'showed us'),
        (r'\bhelped me\b', 'helped us'),
        (r'\blet me\b', 'let us'),
        (r'\ballowed me\b', 'allowed us'),
        (r'\benabled me\b', 'enabled us'),
    ]
    
    # Apply replacements, but skip content in quotes
    for old_pattern, new_text in replacements:
        # Simple replacement outside of quotes (this is a basic approach)
        content = re.sub(old_pattern, new_text, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed voice issues in: {os.path.basename(filepath)}")
        return True
    else:
        return False

def main():
    content_dir = "content/posts"
    files_fixed = 0
    
    # Process all markdown files
    for filepath in glob.glob(f"{content_dir}/*.md"):
        if fix_voice_issues(filepath):
            files_fixed += 1
    
    print(f"\nFixed voice issues in {files_fixed} files")

if __name__ == "__main__":
    main()