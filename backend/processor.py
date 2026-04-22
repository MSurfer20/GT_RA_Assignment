import time
from typing import Dict, Any, Tuple

def process_dataset(data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    # Returns the processed results and dataset id
    dataset_id = data.get("dataset_id", "unknown")
    records = data.get("records", [])
    
    # wait to simulate work (15s)
    time.sleep(15)
    
    categs = {}
    total_val = 0.0
    valid_categ = 0
    inval_categ = 0
    
    for r in records:
        if type(r) is not dict:
            inval_categ += 1
            continue
            
        # Check required fields
        if not all(k in r for k in ("id", "timestamp", "value", "category")):
            inval_categ += 1
            continue
            
        try:
            val = float(r["value"])
            cat = str(r["category"])
            
            categs[cat] = categs.get(cat, 0) + 1
            total_val += val
            valid_categ += 1
        except Exception:
            inval_categ += 1
            
    avg_val = total_val / valid_categ if valid_categ > 0 else 0.0
    
    res = {
        "record_count": len(records),
        "category_summary": categs,
        "average_value": round(avg_val, 2),
        "invalid_records": inval_categ
    }
    
    return res, dataset_id
