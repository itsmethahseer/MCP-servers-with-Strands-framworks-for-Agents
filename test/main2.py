from datetime import datetime

admission = "2025-12-26 10:25:42"
discharge = "2025-12-26 23:59:00"

format_str = "%Y-%m-%d %H:%M:%S"

admission_date = datetime.strptime(admission, format_str)
discharge_date = datetime.strptime(discharge, format_str)

los = (discharge_date - admission_date).days

print("Length of Stay:", los, "days")
