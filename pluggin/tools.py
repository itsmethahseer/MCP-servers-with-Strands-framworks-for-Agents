import os
import json
import requests
from typing import Optional, Literal
from langchain_core.tools import tool
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from datetime import datetime, date

from dotenv import load_dotenv
load_dotenv()

ENV = {
    **os.environ,
}

API_URL = f"{ENV.get('CORE_APP_API_URL')}api"

# --- Helper Functions ---
def split_patient_name(name: str):
    """Splits a full name into first and last names."""
    parts = name.split()
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]

def filter_patient_list(payload, header):
    print("header", header)
    """Helper to search for patients based on provided criteria."""
    url = f"{API_URL}/plug-in/patients/field-search/mrn"
    search_payload = {
        "mrn_number": payload.get("mrn_number", ""),
        "first_name": payload.get("first_name", ""),
        "last_name": payload.get("last_name", ""),
        "dob": payload.get("dob", ""),
        "limit": payload.get("limit", 10),
        "offset": payload.get("offset", 0),
    }
    print("Filtering patient list with payload:", search_payload)
    try:
        res = requests.post(url, json=search_payload, headers=header, timeout=10)
        res.raise_for_status()
        return res.json()["data"]["details"]
    except requests.exceptions.RequestException as e:
        print(f"Error filtering patient list: {e}")
        return {"error": f"API request failed: {e}"}
    

def get_patient_care_plan(payload, header):
    url = f"{API_URL}/plug-in/patients/care-plan"
    print("Fetching patient careplan for ID:", payload)
    try:
        res = requests.post(url, json=payload, headers=header, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting patient details: {e}")
        return {"error": f"API request failed: {e}"}


def get_patient_claim_fact(payload, header):
    print("header", header)
    """Helper to search for patients based on provided criteria."""
    url = f"{API_URL}/plug-in/patient_claims_fact_data"
    payload = {
        "patientID": payload.get("patientID", ""),
        "groupID": payload.get("groupID", "")
    }
    print("get_patient_claim_fact payload:", payload)
    try:
        res = requests.post(url, json=payload, headers=header, timeout=10)
        res.raise_for_status()
        return res.json()["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error get_patient_claim_fact: {e}")
        return {"error": f"API request failed: {e}"}
    

def get_patient_details_by_id(payload, header):
    """Helper to fetch details for a specific patient by ID."""
    url = f"{API_URL}/plug-in/patients/over-view"
   
    print("Fetching patient details for ID:", payload)
    try:
        res = requests.post(url, json=payload, headers=header)
        res.raise_for_status()
        result = res.json()
        care_plan_res = get_patient_care_plan(payload, header)
        claim_fact_res = get_patient_claim_fact(payload, header)
        result["data"]["care_gap"] = result["data"]["details"].get("description", "")
        result["data"]["care_gap_count"] = result["data"]["details"].get("opportunity", "")
        result["data"]["details"].pop("description", None)
        result["data"]["details"].pop("opportunity", None)
        
        # Care plan
        result["data"]["care_plan"] = care_plan_res

        # Claim fact
        result["data"]["claim_fact"] = claim_fact_res
        result["data"]["Visits (Last 12 months)"] = claim_fact_res["last_12_months"]
        result["data"]["Part B Utilization"] = claim_fact_res["other_metrics"]
        result["data"]["MER"] = claim_fact_res["mer"]
        result["data"]["Enrolled Services"] = claim_fact_res["programs"]
        result["data"]["claim_fact"].pop("last_12_months", None)
        result["data"]["claim_fact"].pop("other_metrics", None)
        result["data"]["claim_fact"].pop("mer", None)
        result["data"]["claim_fact"].pop("programs", None)

        print("Patient details fetched successfully.")
        print("Full patient details", result)
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error getting patient details: {e}")
        return {"error": f"API request failed: {e}"}

def find_unique_patient(header: dict, identifiers: dict, id: Optional[str] = None, nav=True):
    """Finds a unique patient, returning their ID or an action dictionary.
    If id is provided, filter the result locally for that id.
    """
    patient_list = filter_patient_list(payload=identifiers, header=header)
    print("Patient list from filter:", patient_list)
    if "error" in patient_list:
        return {
            "action": "speak",
            "message": f"An error occurred while searching for the patient: {patient_list['error']}",
        }

    # If id is provided, filter locally
    if id:
        patient = next((p for p in patient_list if str(p.get("id")) == str(id)), None)
        if patient:
            return patient
        else:
            return {
                "action": "speak",
                "message": "No patient found with the given ID.",
            }

    if patient_list and len(patient_list) == 1:
        return patient_list[0]  # Return the single patient found
    elif patient_list and len(patient_list) > 1:
        if nav:
            return {
                "message": "Multiple patients found. Please provide more specific information.",
                "action": "navigate",
                "path": "patient-table",
                "params": identifiers
            }
        return {
            "action": "speak",
            "message": "Multiple patients found. Please provide more specific information.",
            "data": patient_list,
        }
    else:
        return {
            "action": "speak",
            "message": "No patient found with the given information.",
            "params": identifiers
        }
    
profile_sections = Literal[
    "visits",
    "care_gap",
    "care_plan",
    "enrolled_services",
    "opportunities",
    "risk",
    "mer",
    "utilization",
]

# --- Tools Definition ---
@tool
def navigate_to_home():
    """Navigates to the home screen of the application."""
    return json.dumps({
        "action": "navigate",
        "path": "home",
        "params": {},
    })

@tool
def navigate_to_patient_search(
    mrn_number: Optional[str] = None, 
    name: Optional[str] = None, 
    dob: Annotated[Optional[date], "Patient's date of birth in YYYY-MM-DD format."] = None,
):
    """
    Navigates to the patient search screen, optionally pre-filling search fields.
    All parameters are optional: mrn_number, name, dob.
    """

    first_name, last_name = split_patient_name(name) if name else ("", "")
    return json.dumps({
        "action": "navigate",
        "path": "patient-table",
        "params": {
            "mrn_number": mrn_number,
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob.isoformat() if dob else None,
        },
    })

@tool
def navigate_to_patient_detail(
    state: Annotated[dict, InjectedState],
    mrn_number: Optional[str] = "",
    name: Optional[str] = "",
    dob: Annotated[Optional[date], "Patient's date of birth in YYYY-MM-DD format."] = None,
    patient_id: Optional[str] = "",
    group_id: Optional[str] = "",
    section: Optional[profile_sections] = None
):
    """Navigates to the detail screen for a specific patient.

    Finds a patient using identifiers like MRN, name, or date of birth.
    You can also use `patient_id` and `group_id`. If you use `patient_id`,
    `group_id` is required.

    The `section` parameter allows you to navigate to a specific part of the
    patient's profile. Possible values are: 'visits', 'care_gap', 'care_plan',
    'enrolled_services', 'opportunities', 'risk', 'mer (Medical Expense Ratio)', or 'utilization'.
    """

    context = state["context"]
    if patient_id:
        detail_payload = {
            "patientID": patient_id,
            "groupID": group_id,
            "subscriptionPlanID": context.get("subscription_plan_id", ""),
            "year": context.get("year", ""),
        }
        details = get_patient_details_by_id(detail_payload, header)
        result = details["data"]["details"]
        return json.dumps({
            "action": "navigate",
            "path": "patient-details", 
            "params": result,
            "data": details,
            "section": section
        })
    header = state["header"]
    first_name, last_name = split_patient_name(name) if name else ("", "")
    
    # Format DOB before passing to find_unique_patient
    formatted_dob = dob.strftime("%Y-%m-%d") if dob else None

    patient_identifiers = {
        "mrn_number": mrn_number,
        "first_name": first_name,
        "last_name": last_name,
        "dob": formatted_dob,
    }
    result = find_unique_patient(header, patient_identifiers, nav=True)

    if "id" in result:
        return json.dumps({
            "action": "navigate",
            "path": "patient-details",
            "params": result,  # Assuming result contains the patient ID and group ID 
            "section": section
        })
    return json.dumps(result)

@tool(description="Fetches and returns detailed information about a specific patient.")
def get_patient_details(
    state: Annotated[dict, InjectedState],
    mrn_number: Optional[str] = None,
    name: Optional[str] = None,
    dob: Optional[date] = None,
    patient_id: Optional[str] = None,  # None default is safer
    group_id: Optional[str] = None,
    section: Optional[profile_sections] = None
):
    """Fetches details for a patient using patient_id, context, or identifiers.
       Falls back to a friendly response if no patient information is provided."""

    header = state.get("header", {})
    context = state.get("context", {})

    # Extract context values safely
    current_patient_id = context.get("current_patient_id")
    current_group_id = context.get("group_id")
    current_subscription_plan_id = context.get("subscription_plan_id")
    current_year = context.get("year")

    # # --- Fallback for non-patient queries ---
    # if not patient_id and not current_patient_id and not (mrn_number or name or dob):
    #     return json.dumps({
    #         "action": "speak",
    #         "message": "Hello! How can I help you today?",
    #         "params": {},
    #         "section": section,
    #         "data": {}
    #     })

    # --- Step 1: Use patient_id if provided by user ---
    if patient_id:
        print(f"Using patient ID from user: {patient_id}")
        detail_payload = {
            "patientID": patient_id,
            "groupID": group_id or current_group_id,
            "subscriptionPlanID": current_subscription_plan_id,
            "year": current_year,
        }
        details = get_patient_details_by_id(detail_payload, header)
        result = details.get("data", {}).get("details", {})
        return json.dumps({
            "action": "navigate",
            "message": f"Here is the information for patient ID {patient_id}",
            "path": "patient-details",
            "params": result,
            "section": section,
            "data": details,
        })

    # --- Step 2: Use current_patient_id from context if patient_id not provided ---
    if current_patient_id:
        print(f"Using current patient from context: {current_patient_id}")
        detail_payload = {
            "patientID": current_patient_id,
            "groupID": current_group_id,
            "subscriptionPlanID": current_subscription_plan_id,
            "year": current_year,
        }
        details = get_patient_details_by_id(detail_payload, header)
        result = details.get("data", {}).get("details", {})
        return json.dumps({
            "action": "navigate",
            "message": f"Here is the information for patient ID {current_patient_id}",
            "path": "patient-details",
            "params": result,
            "section": section,
            "data": details,
        })

    # --- Step 3: Search by MRN / Name / DOB ---
    first_name, last_name = split_patient_name(name) if name else ("", "")
    formatted_dob = dob.strftime("%Y-%m-%d") if dob else None
    patient_identifiers = {
        "mrn_number": mrn_number,
        "first_name": first_name,
        "last_name": last_name,
        "dob": formatted_dob,
    }
    print("Finding patient with identifiers:", patient_identifiers)
    result = find_unique_patient(header, patient_identifiers, patient_id)

    if "id" in result:
        detail_payload = {
            "patientID": result["id"],
            "groupID": result.get("group_id") or current_group_id or group_id,
            "subscriptionPlanID": current_subscription_plan_id,
            "year": current_year,
        }
        details = get_patient_details_by_id(detail_payload, header)
        result_data = details.get("data", {}).get("details", {})
    else:
        # Patient not found or ambiguous
        return json.dumps(result)

    return json.dumps({
        "action": "navigate",
        "message": f"Here is the information for patient {detail_payload}",
        "path": "patient-details",
        "params": result_data,
        "section": section,
        "data": details,
    })


@tool
def get_current_time():
    """Returns the current time."""
    return f"The current time is {datetime.now()}."
