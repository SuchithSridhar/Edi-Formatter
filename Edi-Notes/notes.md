# Loops

## 1000A

Loop repeat: 1

Submitter Name
- NM1*41
- PER

## 1000B

Loop repeat: 1

Receiver Name
- NM1*40

## 2000A

Loop repeat: >1

Billing Provider Detail

- HL*01 (Billing Provider Hierarchical Level)
- PRV (situational)
- CUR (situational)

### 2010AA

Loop repeat: 1

- NM1*85 (billing provider name)
- N3
- N4
- REF
- PER (situational)

### 2010AB

Loop repeat: 1

(situational)
Pay to address name

- NM1*87 (pay to provider name)
- N3
- N4
- REF

### 2010AC

Loop repeat: 1

(situational)
Pay to plan name

- NM1*PE (Payee)
- N3
- N4
- REF
- REF

## 2000B

Loop repeat: >1

Subscriber Detail

- HL*02 (Subscriber Hierarchical Level)
- SBR (Subscriber)

### 2010BA

Loop repeat: 1

Subscriber name

- NM1*IL (insured or subscriber)
- N3
- N4
- DMG
- REF
- REF

### 2010BB-1

Loop repeat: 1

Credit/Debit card account holder
(situational)

- NM1*AO (Account Of)
- REF

### 2010BB-2

Loop repeat: 1

Payer Name

- NM1*PR (Payer Name)
- N3
- N4
- REF
- REF

### 2010BD

Loop repeat: 1

Responsible Party Name
(situational)

- NM1*QD (Responsible Party)
- N3
- N4

## 2000C

Loop repeat: >1

Patient Hierarchical Level
(Situational)

If SBR*18 (self) then patient HL is not required

- HL
- PAT (Patient)

### 2010CA

Loop repeat: 1

Patient Name
- NM1*QC (patient name)
- N3
- N4
- DMG
- REF
- REF
- REF (situational)

### 2300

Loop repeat: 100

Claim Information

- CLM 
- DTP*434 (Statement date)
- DTP*096 (Discharge hour) (Situational for inpatient)
- DTP*435 (Admission date) (Situational for inpatient)
- DTP*050 (Repricer Received date) (Situational for inpatient)
- CL1 (Institutional Claim Code)
- PWK (Claim supplemental information) (Situational)
- CN1 (contact information)
...
- HI / QTY / HCP (end of loop)

#### 2305

Loop repeat: 6

Home healthcare plan information
(Situational)

- CR7
- HSD

#### 2310A

Loop repeat: 1

Attending provider name
(Situational)

- NM1*71 (Attending physician)
- PRV
- REF

#### 2310B

Loop repeat: 1

Operating physician name
(situational)

- NM1*72 (Operating Physician)
- REF

#### 2310C-1

Loop repeat: 1

Other provider name
(situational)

- NM1*73 (Other physician)
- REF

#### 2310C-2

Loop repeat: 1

Other operating physician name
(situational)

- NM1*ZZ (Mutual defined)
- REF

#### 2310D

Loop repeat: 1

Rendering provider name
(situational)

- NM1*82 (Rendering provider)
- REF

#### 2310E

Loop repeat: 1

Service facility location name
(situational)

- NM1*77 (Service location)
- N3
- N4
- REF

#### 2310F

Loop repeat: 1

Referring provider name
(situational)

- NM1*DN (referring provider)
- REF

#### 2320

Loop repeat: 10

Other subscriber information 
(situational)

- SBR
- CAS (Claim level adjustments)
- ...
- OI / MIA / MOA

##### 2330A

Loop repeat: 1

Other subscriber name

- NM1*IL (Insured or subscriber)
- N3
- N4
- REF

##### 2330B

Loop repeat: 1

Other payer name

- NM1*PR (Payer)
- N3
- N4
- DTP*573 (Date claim payed)
- REF*4 (situational)

##### 2330C-1

Loop repeat: 1

Other Payer patient information
(situational) (deprecated)

- NM1*QC (Patient)
- REF

##### 2330C-2

Loop repeat: 1

Other Payer attending provider
(situational)

- NM1*71 (Attending provider)
- REF

##### 2330D

Other provider (refer above)

##### 2330E

Other provider (refer above)

##### 2330F

Other provider (refer above)

##### 2330G

Other provider (refer above)

##### 2330H

Other provider (refer above)

##### 2330I

Other provider (refer above)

#### 2400

Loop repeat: 999

Service Line Number

- LX (assigned number)
- SV2 (institutional service line)

(Situational segments)
- PWK
- DTP*472 (service date)
- DTP*866 (Examination date)
- REF*6R (Provider control number)
- REF*9B (Repriced line item referenced number)
- REF*9D (...)
- AMT*GT (Goods and service tax)
- AMT*N8 (Misc taxes)
- NTE*TPO (3rd party org notes)
- HCP (Line pricing/repricing information)

##### 2410

Loop repeat: 1

Drug Information
(situational)

- LIN (Drug ID)
- CTP (Drug qty)
- REF (Prescription or compound drug) (Situational)

##### 2420A-1

Loop repeat: 1

Attending physican name
(situational)

- NM1*71 
- REF

##### 2420A-2

Loop repeat: 1

Operating physician name
(situational)

- NM1*72
- REF

##### 2420B

Loop repeat: 1

Other operating physician name
(situational)

- NM1*ZZ (Mutual defined)
- REF

##### 2420C

Loop repeat: 1

Rendering provider name
(situational)

- NM1*82 
- REF

##### 2420D

Loop repeat: 1

Referring provider name
(situational)

- NM1*DN 
- REF

##### 2430

Loop repeat: 15

Line adjudication information
(situational)

- SVD (line ..)
- CAS (line adjustments)
- DTP*573 (date claim paid)
- AMT*EAF (amount owed)

