import json
from collections import defaultdict
from pathlib import Path

def get_top_key(d: dict, minimize: bool = False) -> str:
    """Get the key with max value (or min if minimize=True)."""
    if not d:
        return None
    # Filter out 'other' and 'other_text' keys
    filtered = {k: v for k, v in d.items() if k not in ('other', 'other_text') and v is not None}
    if not filtered:
        return None
    if minimize:
        return min(filtered, key=lambda k: filtered[k])
    return max(filtered, key=lambda k: filtered[k])

def main():
    survey_path = Path(__file__).parent / "prism" / "survey.jsonl"
    output_path = Path(__file__).parent / "prism" / "attributes.json"
    
    # Track all unique values for each attribute
    attributes = defaultdict(set)
    
    with open(survey_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            entry = json.loads(line)
            
            # Simple top-level attributes
            for attr in ['age', 'gender', 'employment_status', 'education', 
                         'marital_status', 'english_proficiency']:
                if attr in entry and entry[attr] is not None:
                    attributes[attr].add(entry[attr])
            
            # Nested attributes
            if 'religion' in entry and entry['religion']:
                val = entry['religion'].get('simplified')
                if val is not None:
                    attributes['religion_simplified'].add(val)
            
            if 'ethnicity' in entry and entry['ethnicity']:
                val = entry['ethnicity'].get('simplified')
                if val is not None:
                    attributes['ethnicity_simplified'].add(val)
            
            if 'location' in entry and entry['location']:
                loc = entry['location']
                if loc.get('reside_country') is not None:
                    attributes['location_reside_country'].add(loc['reside_country'])
                if loc.get('reside_region') is not None:
                    attributes['location_reside_region'].add(loc['reside_region'])
            
            # TOP values - stated_prefs has highest value = top preference
            if 'stated_prefs' in entry and entry['stated_prefs']:
                top = get_top_key(entry['stated_prefs'], minimize=False)
                if top:
                    attributes['stated_prefs_TOP'].add(top)
            
            # TOP values - order_lm_usecases has lowest value = top (rank 1 is best)
            if 'order_lm_usecases' in entry and entry['order_lm_usecases']:
                top = get_top_key(entry['order_lm_usecases'], minimize=True)
                if top:
                    attributes['order_lm_usecases_TOP'].add(top)
    
    # Convert sets to sorted lists for JSON output
    output = {attr: sorted(list(values)) for attr, values in attributes.items()}
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"Scanned survey.jsonl and wrote {len(attributes)} attributes to {output_path}")
    for attr, values in output.items():
        print(f"  {attr}: {len(values)} unique values")

if __name__ == "__main__":
    main()
