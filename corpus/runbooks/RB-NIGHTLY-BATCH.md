# RB-NIGHTLY-BATCH — Nightly Batch Cycle Runbook (SYNTHETIC)

## Overview
The nightly batch processes the day's transactions, calculates interest,
posts to account records, and produces statements data. All jobs run on
LPAR PROD1. A failed night must be resolved before the 06:00 online
window opens.

## Schedule
Batch window: **21:00 to 05:00 ET**. JOBLD01 is triggered at 21:00 by
the scheduler (Control-M). Each later job starts on the successful
completion of the previous one.

## Job Sequence
1. **JOBLD01** — LOAD. Reads the day's transaction extract, validates
   TXN-AMOUNT and TXN-CHANNEL, and loads records into TXNFILE.
2. **JOBCALC02** — CALCULATE. Computes daily interest on ACCOUNT-RECORD
   balances using ACCT-INT-RATE and writes interest records.
3. **JOBPOST03** — POST. Applies TXNFILE records to ACCTFILE, updating
   ACCT-BALANCE. This is the only job that updates ACCTFILE.
4. **JOBRPT04** — REPORT. Produces the daily balance and exception
   reports from ACCTFILE and TXNFILE.

## Dependencies
- JOBCALC02 cannot start until JOBLD01 completes with return code 0.
- JOBPOST03 cannot start until JOBCALC02 completes; posting before
  interest calculation understates ACCT-BALANCE.
- JOBRPT04 runs only after JOBPOST03 posts successfully.

## Escalation
Two consecutive failed nights page the batch support lead. Do not open
the online window with unposted transactions.
