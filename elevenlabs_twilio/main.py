import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Create session and initiate call
print("1. Initiating call...")
response = requests.post(f"{BASE_URL}/non-clinical-agent/initiate-call", json={
    "ph_no": "+917592072319",
    "request_id": "12345",
    "purposes": ["insurance_eligibility"],
    "type_of_call": "outbound",
    "details": {
        "patient_details": {
            "patient_fname": "Thomas",
            "patient_lname": "John",
            "patient_mobile": "9876543213",
            "insurance_tin": "935395737",
            "insurance_callback_num": "9876543213",
            "patient_gender": "Male",
            "patient_dob": "12/22/1985",
            "patient_dos": "12/10/2024",
            "insurance_name": "Blue Cross",
            "policy_number": "P005008",
            "service_provider": "BronxCare"
        }
    }
})

call_data = response.json()
print(f"✅ Call initiated: {call_data}")
# session_id = call_data["session_id"]
# print(f"✅ Call initiated: {call_data}")

# # 2. Check call status
# print("\n2. Checking call status...")
# status = requests.get(f"{BASE_URL}/non-clinical-agent/call-status/{session_id}")
# print(f"✅ Status: {status.json()}")

# # 3. Simulate agent requesting patient info
# print("\n3. Simulating agent requests...")
# for key in ["policy_number", "dob", "first_name", "provider_tin"]:
#     info = requests.post(f"{BASE_URL}/non-clinical-agent/get-patient-info", json={
#         "key": key,
#         "session_id": session_id
#     })
#     print(f"✅ {key}: {info.json()['value']}")

# # 4. Simulate agent submitting verification
# print("\n4. Submitting verification...")
# verification = requests.post(f"{BASE_URL}/non-clinical-agent/submit-verification-record", json={
#     "session_id": session_id,
#     "eligibility_status": "Active",
#     "coverage_start_date": "2024-01-01",
#     "coverage_end_date": "2024-12-31",
#     "reference_id": "REF123456"
# })
# print(f"✅ Verification: {verification.json()}")

# # 5. Retrieve final result
# print("\n5. Retrieving by request_id...")
# result = requests.get(f"{BASE_URL}/non-clinical-agent/get-verification/12345")
# print(f"✅ Final result: {result.json()}")