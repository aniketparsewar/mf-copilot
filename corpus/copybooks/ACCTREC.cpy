      * ============================================================
      * ACCTREC.CPY  -  ACCOUNT RECORD LAYOUT (SYNTHETIC)
      * VSAM KSDS: ACCTFILE.  KEY: ACCT-ID.
      * RECORD LENGTH NOW 69 BYTES (SEE ACCT-OVERDRAFT-LIMIT NOTE).
      * ============================================================
       01  ACCOUNT-RECORD.
           05  ACCT-ID            PIC 9(12).
      *    ACCT-CUST-ID LINKS THIS ACCOUNT TO CUSTOMER-RECORD.
           05  ACCT-CUST-ID       PIC 9(10).
      *    ACCT-TYPE: CH=CHEQUING, SV=SAVINGS, CC=CREDIT CARD.
           05  ACCT-TYPE          PIC X(2).
           05  ACCT-BALANCE       PIC S9(9)V99 COMP-3.
           05  ACCT-OPEN-DATE     PIC 9(8).
      *    ACCT-STATUS: O=OPEN, F=FROZEN, C=CLOSED.
           05  ACCT-STATUS        PIC X(1).
           05  ACCT-INT-RATE      PIC S9(3)V9(4) COMP-3.
      *    ACCT-OVERDRAFT-LIMIT ADDED 2025-05-30, SEE INC-2025-021.
      *    RECORD LENGTH GREW FROM 64 TO 69 BYTES WHEN ADDED.
           05  ACCT-OVERDRAFT-LIMIT
                                  PIC S9(7)V99 COMP-3.
           05  FILLER             PIC X(10).
