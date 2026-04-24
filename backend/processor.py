from datetime import datetime
import time
from typing import Dict, Any, Tuple
import ijson

def process_dataset(file_path: str) -> Tuple[Dict[str, Any], str]:
    # Returns the processed results and dataset id
    
    # wait to simulate work (15s)
    time.sleep(15)
    
    categs = {}
    total_val = 0.0
    valid_categ = 0
    inval_categ = 0
    record_count = 0
    dataset_id = "unknown"
    
    try:
        with open(file_path, "rb") as f:
            parser = ijson.parse(f)
            for prefix, event, value in parser:
                if prefix == 'dataset_id':
                    dataset_id = value
                    break
    except Exception:
        pass
        
    try:
        with open(file_path, "rb") as f:
            records = ijson.items(f, 'records.item')
            for r in records:
                record_count += 1
                if type(r) is not dict:
                    inval_categ += 1
                    continue
                    
                # Check required fields
                if not all(k in r for k in ("id", "timestamp", "value", "category")):
                    inval_categ += 1
                    continue
                    
                try:
                    # Check if timestamp is a valid ISO string
                    datetime.fromisoformat(str(r["timestamp"]))
                    
                    val = float(r["value"])
                    cat = str(r["category"])
                    
                    categs[cat] = categs.get(cat, 0) + 1
                    total_val += val
                    valid_categ += 1
                except Exception:
                    inval_categ += 1
    except Exception:
        pass
            
    avg_val = total_val / valid_categ if valid_categ > 0 else 0.0
    
    res = {
        "record_count": record_count,
        "category_summary": categs,
        "average_value": round(avg_val, 2),
        "invalid_records": inval_categ
    }
    
    return res, dataset_id
