# User review dates

## Definitions

- One user means one row in `profiles`.
- `approval_status` is the current state. `unsubmitted` means the user has not submitted; `pending` means submitted and awaiting review.
- `submitted_at` is the earliest `profile_completed` analytics event for the user. The current status does not record the time it changed.
- `approved_at` is the earliest `APPROVAL_GRANTED` governance event targeting the user. This is when a verifier approved the user.
- A missing matching event produces a null date. Do not substitute profile creation or update timestamps.

## Query convention

- For users with submission and approval dates, query `users_with_review_dates`.
- Timestamps are UTC unless the requester specifies another time zone.
