# 10. ERROR RECOVERY FLOW

**Circuit Breaker & Retry Logic**  
**Version:** 1.0 | **Date:** March 28, 2026

---

## 🎯 OVERVIEW

Yeh document error recovery ka complete flow explain karta hai - kaise system errors handle karta hai aur automatically recover hota hai.

---

## 📊 HIGH-LEVEL FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ERROR RECOVERY - COMPLETE FLOW                      │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   Action    │
    │   Started   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Execute   │
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│ Success │ │ Failure │
└────┬────┘ └────┬────┘
     │           │
     │           ▼
     │    ┌─────────────────┐
     │    │ Retry Logic     │
     │    │ (Max 3 tries)   │
     │    └────────┬────────┘
     │             │
     │       ┌─────┴─────┐
     │       │           │
     │       ▼           ▼
     │  ┌─────────┐ ┌───────────┐
     │  │ Success │ │  Circuit  │
     │  └────┬────┘ │   OPEN    │
     │       │      └─────┬─────┘
     │       │            │
     ▼       ▼            ▼
┌──────────────────────────────────┐
│      LOG TO Done/                │
│      (All paths converge)        │
└──────────────────────────────────┘
```

---

## 🔄 DETAILED FLOW

### Complete Error Recovery Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ERROR RECOVERY - COMPLETE FLOW                       │
└──────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │    START    │
  └──────┬──────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 1: ACTION EXECUTION                                                │
│                                                                          │
│  ┌─────────────┐                                                         │
│  │   Start     │                                                         │
│  │   Action    │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Examples:                                                        │  │
│  │  • Send email via Gmail MCP                                       │  │
│  │  • Post to Facebook                                               │  │
│  │  • Send WhatsApp message                                          │  │
│  │  • Create Odoo invoice                                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Execute    │                                                         │
│  │  Action     │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│    ┌────┴────┐                                                           │
│    │         │                                                            │
│    ▼         ▼                                                            │
│  Success  Error                                                           │
│    │         │                                                            │
│    │         ▼                                                            │
│    │    ┌────────────────┐                                                │
│    │    │ STEP 2:        │                                                │
│    │    │ ERROR HANDLING │                                                │
│    │    └────────────────┘                                                │
│    │                                                                      │
│    ▼                                                                      │
│  ┌─────────────────┐                                                      │
│  │ Log Success     │                                                      │
│  │ Go to DONE      │                                                      │
│  └─────────────────┘                                                      │
└──────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ERROR DETECTION & LOGGING                                       │
│                                                                          │
│  ┌─────────────┐                                                         │
│  │   Catch     │                                                         │
│  │   Error     │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  try:                                                             │  │
│  │      result = execute_action()                                    │  │
│  │  except Exception as e:                                           │  │
│  │      error_type = type(e).__name__                                │  │
│  │      error_message = str(e)                                       │  │
│  │      timestamp = datetime.now().isoformat()                       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Classify   │                                                         │
│  │  Error      │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Error Types:                                                     │  │
│  │                                                                   │  │
│  │  ┌──────────────────┬─────────────────────────────────┐          │  │
│  │  │ Error Type       │ Example                         │          │  │
│  │  ├──────────────────┼─────────────────────────────────┤          │  │
│  │  │ NetworkError     │ Connection timeout              │          │  │
│  │  │ AuthError        │ Session expired                 │          │  │
│  │  │ ValidationError  │ Invalid input data              │          │  │
│  │  │ RateLimitError   │ Too many requests               │          │  │
│  │  │ ServerError      │ 500 Internal Server Error       │          │  │
│  │  │ TimeoutError     │ Request timeout                 │          │  │
│  │  └──────────────────┴─────────────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Log Error  │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  log_error({                                                      │  │
│  │      "timestamp": "2026-03-28T10:30:00",                          │  │
│  │      "action": "facebook_post",                                   │  │
│  │      "error_type": "NetworkError",                                │  │
│  │      "error_message": "Connection timeout",                       │  │
│  │      "retry_count": 0                                             │  │
│  │  })                                                               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 3: RETRY LOGIC                                                     │
│                                                                          │
│  ┌─────────────┐                                                         │
│  │  Initialize │                                                         │
│  │  Retry      │                                                         │
│  │  Counter    │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  retry_count = 0                                                  │  │
│  │  max_retries = 3                                                  │  │
│  │  base_delay = 1.0  # seconds                                      │  │
│  │  max_delay = 60.0  # seconds                                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  RETRY LOOP:                                                      │  │
│  │                                                                   │  │
│  │  while retry_count < max_retries:                                 │  │
│  │      retry_count += 1                                             │  │
│  │                                                                   │  │
│  │      # Calculate delay with exponential backoff                   │  │
│  │      delay = min(base_delay * (2 ** (retry_count - 1)), max_delay)│  │
│  │                                                                   │  │
│  │      print(f"Retry {retry_count}/{max_retries} after {delay}s")   │  │
│  │      time.sleep(delay)                                            │  │
│  │                                                                   │  │
│  │      # Try again                                                  │  │
│  │      try:                                                         │  │
│  │          result = execute_action()                                │  │
│  │          return result  # Success!                                │  │
│  │      except Exception as e:                                       │  │
│  │          log_error(e, retry_count)                                │  │
│  │          # Continue to next retry                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Retry Timeline:                                                  │  │
│  │                                                                   │  │
│  │  Attempt 1 (t=0s):    ❌ Failed                                   │  │
│  │                         ↓                                          │  │
│  │  Wait 1 second                                                      │  │
│  │                         ↓                                          │  │
│  │  Attempt 2 (t=1s):    ❌ Failed                                   │  │
│  │                         ↓                                          │  │
│  │  Wait 2 seconds                                                     │  │
│  │                         ↓                                          │  │
│  │  Attempt 3 (t=3s):    ❌ Failed                                   │  │
│  │                         ↓                                          │  │
│  │  Wait 4 seconds                                                     │  │
│  │                         ↓                                          │  │
│  │  Attempt 4 (t=7s):    Final Attempt                               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│    ┌────┴────┐                                                           │
│    │         │                                                            │
│    ▼         ▼                                                            │
│  Success  All Retries                                                      │
│    │       Failed                                                          │
│    │         │                                                            │
│    │         ▼                                                            │
│    │    ┌────────────────┐                                                │
│    │    │ STEP 4:        │                                                │
│    │    │ CIRCUIT BREAKER│                                                │
│    │    └────────────────┘                                                │
│    │                                                                      │
│    ▼                                                                      │
│  ┌─────────────────┐                                                      │
│  │ Retry Successful│                                                      │
│  │ Continue Flow   │                                                      │
│  └─────────────────┘                                                      │
└──────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 4: CIRCUIT BREAKER                                                 │
│                                                                          │
│  ┌─────────────┐                                                         │
│  │  Check      │                                                         │
│  │  Circuit    │                                                         │
│  │  State      │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Circuit Breaker States:                                          │  │
│  │                                                                   │  │
│  │  ┌──────────────┐                                                 │  │
│  │  │   CLOSED     │  ← Normal operation                            │  │
│  │  │              │     Actions execute normally                    │  │
│  │  └──────────────┘                                                 │  │
│  │         │                                                         │  │
│  │         │ (failures >= threshold)                                 │  │
│  │         ▼                                                         │  │
│  │  ┌──────────────┐                                                 │  │
│  │  │    OPEN      │  ← Circuit broken                              │  │
│  │  │              │     Actions blocked                           │  │
│  │  └──────────────┘                                                 │  │
│  │         │                                                         │  │
│  │         │ (after recovery_timeout)                                │  │
│  │         ▼                                                         │  │
│  │  ┌──────────────┐                                                 │  │
│  │  │  HALF_OPEN   │  ← Testing recovery                            │  │
│  │  │              │     One action allowed                        │  │
│  │  └──────────────┘                                                 │  │
│  │         │                                                         │  │
│  │    ┌────┴────┐                                                    │  │
│  │    │         │                                                    │  │
│  │    ▼         ▼                                                    │  │
│  │  Success   Failure                                                │  │
│  │    │         │                                                    │  │
│  │    │         └──────────┐                                         │  │
│  │    │                    │                                         │  │
│  │    ▼                    ▼                                         │  │
│  │  CLOSED              OPEN                                         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  class CircuitBreaker:                                            │  │
│  │      def __init__(self):                                          │  │
│  │          self.failure_count = 0                                   │  │
│  │          self.failure_threshold = 5                               │  │
│  │          self.recovery_timeout = 60  # seconds                    │  │
│  │          self.state = 'CLOSED'                                    │  │
│  │          self.last_failure_time = None                            │  │
│  │                                                                   │  │
│  │      def can_execute(self):                                       │  │
│  │          if self.state == 'OPEN':                                 │  │
│  │              # Check if recovery timeout passed                   │  │
│  │              if time.time() - self.last_failure_time >            │  │
│  │                 self.recovery_timeout:                            │  │
│  │                  self.state = 'HALF_OPEN'                         │  │
│  │                  return True                                      │  │
│  │              return False                                         │  │
│  │          return True                                              │  │
│  │                                                                   │  │
│  │      def record_success(self):                                    │  │
│  │          self.failure_count = 0                                   │  │
│  │          self.state = 'CLOSED'                                    │  │
│  │                                                                   │  │
│  │      def record_failure(self):                                    │  │
│  │          self.failure_count += 1                                  │  │
│  │          self.last_failure_time = time.time()                     │  │
│  │          if self.failure_count >= self.failure_threshold:         │  │
│  │              self.state = 'OPEN'                                  │  │
│  │              print("⚠️ CIRCUIT OPEN!")                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│    ┌────┴────┐                                                           │
│    │         │                                                            │
│    ▼         ▼                                                            │
│  Circuit   Circuit                                                        │
│  CLOSED    OPEN                                                           │
│    │         │                                                            │
│    │         ▼                                                            │
│    │    ┌────────────────┐                                                │
│    │    │ STEP 5:        │                                                │
│    │    │ FALLBACK       │                                                │
│    │    │ ACTION         │                                                │
│    │    └────────────────┘                                                │
│    │                                                                      │
│    ▼                                                                      │
│  ┌─────────────────┐                                                      │
│  │ Execute Action  │                                                      │
│  │ Continue Flow   │                                                      │
│  └─────────────────┘                                                      │
└──────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 5: FALLBACK ACTION                                                 │
│                                                                          │
│  ┌─────────────┐                                                         │
│  │  Circuit    │                                                         │
│  │  OPEN       │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Cannot     │                                                         │
│  │  Execute    │                                                         │
│  │  Action     │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Trigger    │                                                         │
│  │  Fallback   │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Fallback Options:                                                │  │
│  │                                                                   │  │
│  │  ┌──────────────────┬─────────────────────────────────┐          │  │
│  │  │ Fallback Type    │ Action                          │          │  │
│  │  ├──────────────────┼─────────────────────────────────┤          │  │
│  │  │ Queue for Later  │ Save to pending/ folder         │          │  │
│  │  │ Alert User       │ Send notification/email         │          │  │
│  │  │ Log Critical     │ Write to errors.log             │          │  │
│  │  │ Skip & Continue  │ Mark as failed, move on         │          │  │
│  │  │ Manual Review    │ Move to inbox/ for approval     │          │  │
│  │  └──────────────────┴─────────────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Example: Alert User                                              │  │
│  │                                                                   │  │
│  │  def fallback_alert_user(error, action):                          │  │
│  │      # Send email to admin                                        │  │
│  │      send_email(                                                  │  │
│  │          to='admin@example.com',                                  │  │
│  │          subject='⚠️ Gold Tier: Action Failed',                   │  │
│  │          body=f'''                                                │  │
│  │  Action Failed: {action}                                          │  │
│  │  Error: {error}                                                   │  │
│  │  Circuit Breaker: OPEN                                            │  │
│  │  Time: {datetime.now()}                                           │  │
│  │                                                                   │  │
│  │  Please check the system.                                         │  │
│  │  '''                                                              │  │
│  │      )                                                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  Fallback   │                                                         │
│  │  Executed   │                                                         │
│  └──────┬──────┘                                                         │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────────┐                                                      │
│  │    COMPLETED    │                                                      │
│  │  (With Fallback)│                                                      │
│  └─────────────────┘                                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 ERROR RECOVERY EXAMPLES

### Example 1: Network Timeout

```
┌──────────────────────────────────────────────────────────────────────┐
│                  EXAMPLE: NETWORK TIMEOUT                            │
└──────────────────────────────────────────────────────────────────────┘

  Timeline:
  
  t=0s:   Send email request
          ❌ ERROR: Connection timeout
  
  t=0s:   Retry #1 scheduled
          Waiting 1 second...
  
  t=1s:   Retry #1
          ❌ ERROR: Connection timeout
  
  t=1s:   Retry #2 scheduled
          Waiting 2 seconds...
  
  t=3s:   Retry #2
          ❌ ERROR: Connection timeout
  
  t=3s:   Retry #3 scheduled
          Waiting 4 seconds...
  
  t=7s:   Retry #3 (Final)
          ✅ SUCCESS: Email sent!
  
  Result: Email sent after 3 retries
```

### Example 2: Circuit Breaker Open

```
┌──────────────────────────────────────────────────────────────────────┐
│               EXAMPLE: CIRCUIT BREAKER OPEN                          │
└──────────────────────────────────────────────────────────────────────┘

  Timeline:
  
  t=0s:   Action #1 - Failed
  t=1s:   Action #2 - Failed
  t=2s:   Action #3 - Failed
  t=3s:   Action #4 - Failed
  t=4s:   Action #5 - Failed
  
          ⚠️ FAILURE THRESHOLD REACHED (5)
          🔴 CIRCUIT BREAKER: OPEN
  
  t=5s:   Action #6 - BLOCKED (Circuit is OPEN)
          → Fallback: Queue for later
  
  t=6s:   Action #7 - BLOCKED (Circuit is OPEN)
          → Fallback: Queue for later
  
  ... Wait 60 seconds ...
  
  t=65s:  Circuit checks recovery timeout
          🟡 CIRCUIT BREAKER: HALF_OPEN
  
  t=66s:  Action #8 - Test execution
          ✅ SUCCESS!
          🟢 CIRCUIT BREAKER: CLOSED
  
  Result: System recovered automatically
```

---

## 🔧 CONFIGURATION

### Error Recovery Settings

```python
# error_recovery.py configuration

RETRY_CONFIG = {
    'max_retries': 3,           # Maximum retry attempts
    'base_delay': 1.0,          # Initial delay (seconds)
    'max_delay': 60.0,          # Maximum delay (seconds)
    'exponential_backoff': True # Use exponential backoff
}

CIRCUIT_BREAKER_CONFIG = {
    'failure_threshold': 5,     # Failures before opening
    'recovery_timeout': 60,     # Seconds before half-open
    'expected_exception': Exception
}
```

---

## 📊 FLOW SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   ERROR RECOVERY FLOW SUMMARY                           │
└─────────────────────────────────────────────────────────────────────────┘

  COMPLETE FLOW:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Error → Log → Retry (x3) → [Success OR Circuit Open]              │
  │                                                                    │
  │  If Circuit Open → Fallback → Alert User → Log                     │
  └─────────────────────────────────────────────────────────────────────┘


  RETRY TIMELINE:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Attempt 1 → Wait 1s → Attempt 2 → Wait 2s → Attempt 3 → Wait 4s   │
  │  → Attempt 4 (Final)                                               │
  └─────────────────────────────────────────────────────────────────────┘


  CIRCUIT STATES:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  CLOSED → (5 failures) → OPEN → (60s timeout) → HALF_OPEN          │
  │  → (1 success) → CLOSED                                            │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 RELATED FLOWS

| Flow | Document |
|------|----------|
| System Overview | [01_system_overview_flow.md](01_system_overview_flow.md) |
| Email Flow | [05_email_automation_flow.md](05_email_automation_flow.md) |
| Facebook Flow | [07_facebook_automation_flow.md](07_facebook_automation_flow.md) |
| Audit Logging | [11_audit_logging_flow.md](11_audit_logging_flow.md) |

---

**Document Version:** 1.0  
**Created:** March 28, 2026  
**Status:** ✅ COMPLETE
