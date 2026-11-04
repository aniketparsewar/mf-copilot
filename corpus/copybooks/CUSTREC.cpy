      * ============================================================
      * CUSTREC.CPY  -  CUSTOMER MASTER RECORD LAYOUT (SYNTHETIC)
      * VSAM KSDS: CUSTFILE.  KEY: CUST-ID.
      * ============================================================
       01  CUSTOMER-RECORD.
           05  CUST-ID            PIC 9(10).
           05  CUST-NAME          PIC X(40).
           05  CUST-ADDRESS.
               10  CUST-STREET    PIC X(30).
               10  CUST-CITY      PIC X(20).
               10  CUST-PROVINCE  PIC X(2).
               10  CUST-POSTAL    PIC X(6).
           05  CUST-PHONE         PIC X(12).
           05  CUST-EMAIL         PIC X(50).
      *    CUST-SINCE: CUSTOMER SINCE DATE, FORMAT YYYYMMDD.
           05  CUST-SINCE         PIC 9(8).
      *    CUST-STATUS: A=ACTIVE, I=INACTIVE, C=CLOSED.
           05  CUST-STATUS        PIC X(1).
           05  FILLER             PIC X(21).
