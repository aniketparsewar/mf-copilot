# RB-ABEND-S0C7 — Handling S0C7 Abends (SYNTHETIC)

## Symptom
A batch job terminates with completion code S0C7 and no output file.
The job log shows the abend in a MOVE or arithmetic statement.

## Cause
S0C7 is a **data exception**: the program tried to use a field as a
number when the field does not contain valid numeric data. The usual
case here is a COMP-3 (packed decimal) field — most often TXN-AMOUNT —
containing spaces or text sent by an upstream channel.

## Diagnosis
Check **TXN-AMOUNT first**: it is the field involved in nearly every
S0C7 in the nightly batch. Read the dump to find the failing record's
TXN-ID, then inspect that record's raw bytes. Spaces (X'40') in a
COMP-3 field confirm bad source data rather than a program bug.

## Resolution
Correct or reject the bad source records with the sending channel,
then restart the job from its last checkpoint (see RB-JOB-RESTART).
Never edit packed-decimal fields by hand in a hex editor to "make the
job pass" — the posted amounts will be wrong.

## Prevention
JOBLD01 validates TXN-AMOUNT is numeric before loading TXNFILE.
Channels must not send spaces in numeric fields; a channel that does
is patched at the source, not worked around in the batch.
