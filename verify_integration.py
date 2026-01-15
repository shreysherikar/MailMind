import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_step(msg):
    print(f"\n[STEP] {msg}")

def verify():
    # 1. Simulate an incoming email (Score it -> Prevents to DB)
    print_step("Sending email to be scored and stored...")
    email_payload = {
        "email": {
            "id": f"test_msg_{int(time.time())}",
            "subject": "Urgent: Project Update Required",
            "sender_email": "boss@company.com",
            "recipients": ["me@company.com"],
            "body": "Please send me the status report by EOD.",
            "timestamp": "2023-10-27T10:00:00Z"
        }
    }
    
    try:
        res = requests.post(f"{BASE_URL}/emails/score", json=email_payload)
        res.raise_for_status()
        print("✅ Email scored and stored successfully.")
        email_id = email_payload["email"]["id"]
    except Exception as e:
        print(f"❌ Failed to score email: {e}")
        return

    # 2. Verify it's in the 'Inbox'
    print_step("Checking Inbox for the new email...")
    res = requests.get(f"{BASE_URL}/emails", params={"status": "inbox"})
    emails = res.json()
    if any(e['id'] == email_id for e in emails):
        print("✅ Email found in Inbox.")
    else:
        print("❌ Email NOT found in Inbox.")
        return

    # 3. Mark as Done
    print_step("Marking email as 'Done'...")
    res = requests.patch(f"{BASE_URL}/emails/{email_id}/status", params={"status": "done"})
    if res.status_code == 200:
        print("✅ Status update successful.")
    else:
        print(f"❌ Status update failed: {res.text}")
        return

    # 4. Verify it's GONE from Inbox
    print_step("Verifying email is removed from Inbox...")
    res = requests.get(f"{BASE_URL}/emails", params={"status": "inbox"})
    emails = res.json()
    if not any(e['id'] == email_id for e in emails):
        print("✅ Email successfully removed from Inbox.")
    else:
        print("❌ Email still present in Inbox (Fail).")
        return

    # 5. Verify it's in Done list (if we could filter by done, or just check DB indirectly?)
    # The list endpoint supports status filter!
    print_step("Verifying email appears in 'Done' list...")
    res = requests.get(f"{BASE_URL}/emails", params={"status": "done"})
    emails = res.json()
    if any(e['id'] == email_id for e in emails):
        print("✅ Email found in 'Done' list.")
    else:
        print("❌ Email NOT found in 'Done' list.")
        return

    print("\n🎉 BACKEND VERIFICATION SUCCESSFUL!")

if __name__ == "__main__":
    verify()
