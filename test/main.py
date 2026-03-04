from datetime import datetime

def calculate_age(dob_str, admission_str):
    date_format = "%Y-%m-%d %H:%M:%S"
    
    dob = datetime.strptime(dob_str, date_format)
    admission_date = datetime.strptime(admission_str, date_format)
    
    age = admission_date.year - dob.year
    
    # Adjust if birthday hasn't occurred yet
    if (admission_date.month, admission_date.day) < (dob.month, dob.day):
        age -= 1
        
    return age


# Example
dob = "1960-12-12 00:00:00"
admission_date = "2026-01-13 06:36:00"

print("Age:", calculate_age(dob, admission_date))
