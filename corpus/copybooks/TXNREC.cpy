      * ============================================================
      * TXNREC.CPY  -  TRANSACTION RECORD LAYOUT (SYNTHETIC)
      * VSAM KSDS: TXNFILE.  KEY: TXN-ID.
      * ============================================================
       01  TRANSACTION-RECORD.
           05  TXN-ID             PIC 9(14).
      *    TXN-ACCT-ID LINKS THIS TRANSACTION TO ACCOUNT-RECORD.
           05  TXN-ACCT-ID        PIC 9(12).
      *    TXN-DATE: FORMAT YYYYMMDD.  TXN-TIME: FORMAT HHMMSS.
           05  TXN-DATE           PIC 9(8).
           05  TXN-TIME           PIC 9(6).
      *    TXN-TYPE: DB=DEBIT, CR=CREDIT, PM=PAYMENT.
           05  TXN-TYPE           PIC X(2).
      *    TXN-AMOUNT IS COMP-3: NON-NUMERIC CONTENT ABENDS S0C7.
           05  TXN-AMOUNT         PIC S9(9)V99 COMP-3.
           05  TXN-MERCHANT       PIC X(30).
      *    TXN-CHANNEL: ATM, WEB=ONLINE, BR=BRANCH, MOB=MOBILE APP.
           05  TXN-CHANNEL        PIC X(3).
           05  FILLER             PIC X(15).
