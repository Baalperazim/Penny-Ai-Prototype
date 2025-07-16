import json
import os
import re
from penny import Transaction

class SMSReader:
    """Processes bank SMS messages into transactions"""
    
    def __init__(self, sms_file='data/mock_sms.json', log_file='data/processed_sms_ids.json'):
        """Initialize SMS processor"""
        self.sms_file = sms_file
        self.log_file = log_file
        self._ensure_data_dir()
        self.processed_ids = self._load_processed_ids()

    def _ensure_data_dir(self):
        """Create data directory if missing"""
        try:
            os.makedirs('data', exist_ok=True)
        except Exception as e:
            print(f"Error creating data directory: {e}")
            raise

    def _load_processed_ids(self):
        """Load set of already processed SMS IDs"""
        if not os.path.exists(self.log_file):
            return set()
        
        try:
            with open(self.log_file, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Error loading processed IDs: {e}")
            return set()

    def _save_processed_ids(self):
        """Save processed IDs to JSON file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(list(self.processed_ids), f, indent=4)
        except Exception as e:
            print(f"Error saving processed IDs: {e}")
            raise

    def reset_processed_ids(self):
        """Clear processing history completely"""
        self.processed_ids = set()
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
        except Exception as e:
            print(f"Error resetting processed IDs: {e}")
            raise

    def read_sms(self):
        """
        Processes and returns exactly one new debit transaction
        Returns: List containing one Transaction object or empty list if none found
        """
        if not os.path.exists(self.sms_file):
            return []

        try:
            with open(self.sms_file, 'r') as f:
                sms_data = json.load(f)
        except Exception as e:
            print(f"Error reading SMS file: {e}")
            return []

        # Process in consistent order
        for sms in sorted(sms_data, key=lambda x: str(x.get('id', ''))):
            try:
                sms_id = str(sms.get('id'))
                if not sms_id or sms_id in self.processed_ids:
                    continue

                if "debit" in sms["message"].lower():
                    amount = self._extract_amount(sms["message"])
                    if amount is not None:
                        transaction = Transaction(
                            amount=amount,
                            trans_type="debit",
                            date=sms.get("date", "2025-07-10"),
                            source=sms.get("source", "Unknown")
                        )
                        self.processed_ids.add(sms_id)
                        self._save_processed_ids()
                        return [transaction]
            except Exception as e:
                print(f"Error processing SMS {sms.get('id')}: {e}")
                continue

        return []

    def _extract_amount(self, message):
        """
        Extracts numeric amount from SMS text
        Returns: float amount or None if not found
        """
        patterns = [
            # Standard formats (₦1,234.56 or NGN 1,234.56)
            r'(?:NGN|₦|N)\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Debit alert formats
            r'debited.*?(?:NGN|₦|N)\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Amount before currency (1,234.56 NGN)
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s?(?:NGN|₦|N)',
            
            # No decimal (₦1200)
            r'(?:NGN|₦|N)(\d+)',
            
            # Plain numbers
            r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b'
        ]

        for pattern in patterns:
            try:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    return float(amount_str)
            except Exception:
                continue

        return None