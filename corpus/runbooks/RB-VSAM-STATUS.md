# RB-VSAM-STATUS — VSAM File Status Codes (SYNTHETIC)

## Overview
Every VSAM file operation returns a two-character file status. Batch
programs check it after each OPEN, READ, and WRITE. This runbook covers
the four codes the nightly batch actually hits.

## Status 35: File Not Found on OPEN
OPEN failed because the file does not exist or the cluster was never
defined. Check the job's DD statement points at the right cluster and
that the IDCAMS DEFINE ran. An empty, never-loaded cluster can also
return 35 on an input OPEN.

## Status 39: File Attribute Conflict on OPEN
OPEN failed because the file's attributes in the program conflict with
the attributes of the actual file — almost always a **record length
mismatch**: the copybook changed (a field was added or widened) but the
VSAM cluster still has the old definition. Redefine the cluster to
match the current copybook, reload, and rerun.

## Status 23: Record Not Found on READ
A keyed READ found no record with that key. The record was never
written, or the key was built incorrectly (check for spaces or a
partially moved key field). This is a data problem, not a file problem.

## Status 22: Duplicate Key on WRITE
A WRITE tried to add a record whose key already exists in the file.
Usually a restarted job re-processing records it already wrote — see
RB-JOB-RESTART on why restarts begin at checkpoints.

## Escalation
Statuses 35 and 39 are definition problems: involve the systems
programmer. Statuses 22 and 23 are data problems: involve the
application team first.
