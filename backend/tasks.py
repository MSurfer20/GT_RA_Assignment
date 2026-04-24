import logging
from typing import Dict, Any
from .celery_app import app
from .database import SessionLocal
from .models import Task
from .processor import process_dataset
import os
import json
import ijson

log = logging.getLogger(__name__)

@app.task(bind=True)
def process_data_task(self, t_id: str):
    sess = SessionLocal()
    
    try:
        current_task = sess.query(Task).filter(Task.id == t_id).first()
        if not current_task:
            log.error(f"Task {t_id} missing!")
            return
            
        current_task.status = "Processing"
        sess.commit()
        
        file_path = f"data/{t_id}.json"
        
        dataset_id = "unknown"
        try:
            with open(file_path, "rb") as f:
                parser = ijson.parse(f)
                for prefix, event, value in parser:
                    if prefix == 'dataset_id':
                        dataset_id = value
                        break
        except FileNotFoundError:
            raise ValueError("Failed to read JSON payload from disk")
        except Exception:
            pass # Invalid JSON or other error, handled later
            
        current_task.dataset_id = dataset_id
        sess.commit()
        
        # run processing
        res, ds_id = process_dataset(file_path)
        
        # save results
        current_task = sess.query(Task).filter(Task.id == t_id).first()
        current_task.status = "Completed"
        current_task.dataset_id = ds_id
        current_task.record_count = res["record_count"]
        current_task.category_summary = res["category_summary"]
        current_task.average_value = res["average_value"]
        current_task.invalid_records = res["invalid_records"]
        sess.commit()
        
        return res
        
    except Exception as e:
        sess.rollback()
        log.error(f"Failed task {t_id}: {str(e)}")
        current_task = sess.query(Task).filter(Task.id == t_id).first()
        if current_task:
            current_task.status = "Failed"
            current_task.error_message = str(e)
            sess.commit()
        raise e
    finally:
        # Clean up the file from disk after it has been processed
        if os.path.exists(file_path):
            os.remove(file_path)
        sess.close()
