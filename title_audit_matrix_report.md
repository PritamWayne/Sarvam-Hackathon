# Discrepancy & Title Audit Engine Report (Sarvam-105B)
**Audit Reference ID**: `TA-20261026-222102` | **Engine**: `Sarvam-105B Title Audit Engine v1.0`
**Execution Timestamp**: 2026-10-26 22:21:02

---

## 1. Executive Title Audit Summary

| Audit Metric | Assessment Details |
| :--- | :--- |
| **Overall Title Health** | 🔴 **CRITICAL TITLE DEFECT (ACTION REQUIRED)** |
| **Target Revenue Jurisdiction** | Hastinapur, Tehsil Mawana, District Meerut, Uttar Pradesh |
| **Khasra / Survey Parcels** | `452/1, 452/2` |
| **Total Registered Parcel Area** | `12 Bigha 0 Biswa` (30,351.42 m² / 7.5000 Acres) |
| **Claimant Name & ID** | **Amit Kumar** (`P06`) |
| **Theoretical Lawful Share (HSA)** | **`1/9`** |
| **Official Recorded Share** | **`0 (Omitted)`** |
| **Claimant Deprivation / Deficit** | **3,372.38 m²** (0.8333 Acres) |
| **Total Irregularities Detected** | **9 Defects Identified** |

> **Verdict**: TITLE CLOUD DETECTED (CRITICAL): Title is fatally defective. Illegal omission of statutory heirs without registered Haq-Tyag and unauthorized over-conveyance deprived claimant 'Amit Kumar' of 1/9 share (3,372.38 m² / 0.8333 Acres).

## 2. Statutory Succession Entitlement Ledger (Hindu Succession Act)

| Person ID | Legal Heir Name | Statutory Relationship | Class | Theoretical Share | Entitled Area (m²) | Recorded Share | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `P01` | **Ram Lal** | Ancestral Patriarch / Original Titleholder | Class I Legal Heir | `0` | 0.00 m² | `0 (Omitted)` | **Devolved to Heirs** |
| `P02` | **Suresh Kumar** | Son of Ram Lal | Class I Legal Heir | `0` | 0.00 m² | `0 (Omitted)` | **Devolved to Heirs** |
| `P03` | **Ramesh Kumar** | Son of Ram Lal | Class I Legal Heir | `1/3` | 10,117.14 m² | `1/1` | **Inflated / Surplus** |
| `P04` | **Kamla Devi** | Daughter of Ram Lal | Class I Legal Heir | `1/3` | 10,117.14 m² | `0` | **Omitted from Title** |
| `P05` | **Shanti Devi** | Widow / Spouse of Suresh Kumar | Class I Legal Heir | `1/9` | 3,372.38 m² | `0` | **Omitted from Title** |
| `P06` | **Amit Kumar** ⭐ (Claimant) | Son of Suresh Kumar | Class I Legal Heir | `1/9` | 3,372.38 m² | `0` | **Omitted from Title** |
| `P07` | **Sunita Kumari** | Daughter of Suresh Kumar | Class I Legal Heir | `1/9` | 3,372.38 m² | `0` | **Omitted from Title** |

## 3. Structured Discrepancy Matrix

| Defect ID | Severity | Title Irregularity & Category | Statutory Ground | Evidence Citation & Bounding Box | Deprived Holding | Recommended Legal Remedy |
| :---: | :---: | :--- | :--- | :--- | :---: | :--- |
| **DEF-001** | 🟠 `HIGH` | **Omission of Legal Heir (Kamla Devi) without Registered Haq-Tyag**<br>*DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG* | Hindu Succession Act 1956, Section 6 & 8<br>Registration Act 1908, Section 17(1)(b) & Section 49<br>Transfer of Property Act 1882, Section 9 | **INT-204, Line: 'Sanctioned in favour of Suresh & Ramesh sons of Ram Lal on oral statement of Patwari.'**<br>`bbox: [115.0, 42.0, 185.0, 540.0]` | 10,117.1 m² | File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-204. Seek immediate correction of Jamabandi entries to restore Kamla Devi's lawful share. |
| **DEF-002** | 🔴 `CRITICAL` | **Omission of Legal Heir (Amit Kumar) without Registered Haq-Tyag**<br>*DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG* | Hindu Succession Act 1956, Section 6 & 8<br>Registration Act 1908, Section 17(1)(b) & Section 49<br>Transfer of Property Act 1882, Section 9 | **INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'**<br>`bbox: [225.0, 45.0, 295.0, 550.0]` | 3,372.4 m² | File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Amit Kumar's lawful share. |
| **DEF-003** | 🟠 `HIGH` | **Omission of Legal Heir (Shanti Devi) without Registered Haq-Tyag**<br>*DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG* | Hindu Succession Act 1956, Section 6 & 8<br>Registration Act 1908, Section 17(1)(b) & Section 49<br>Transfer of Property Act 1882, Section 9 | **INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'**<br>`bbox: [225.0, 45.0, 295.0, 550.0]` | 3,372.4 m² | File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Shanti Devi's lawful share. |
| **DEF-004** | 🟠 `HIGH` | **Omission of Legal Heir (Sunita Kumari) without Registered Haq-Tyag**<br>*DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG* | Hindu Succession Act 1956, Section 6 & 8<br>Registration Act 1908, Section 17(1)(b) & Section 49<br>Transfer of Property Act 1882, Section 9 | **INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'**<br>`bbox: [225.0, 45.0, 295.0, 550.0]` | 3,372.4 m² | File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Sunita Kumari's lawful share. |
| **DEF-005** | 🔴 `CRITICAL` | **Unrepresented Minor Mutation (Amit Kumar, Sunita Kumari) without HMGA Sec 8 Sanction**<br>*DefectCategory.UNREPRESENTED_MINOR_MUTATION* | Hindu Minority and Guardianship Act 1956, Section 6 & 8(2)<br>Indian Majority Act 1875, Section 3<br>Civil Procedure Code 1908, Order XXXII Rules 1-3 | **Mutation No. INT-389 (2014-08-20), Column 8/11**<br>`bbox: [225.0, 45.0, 295.0, 550.0]` | - | Institute suit for Declaration and Invalidation of Mutation No. INT-389 under Section 8(3) of the Hindu Minority and Guardianship Act, 1956 read with Section 31 of the Specific Relief Act, 1963. Limitation commences from the date of attaining majority. |
| **DEF-006** | 🟠 `HIGH` | **Total Absence of Legal Heir 'Kamla Devi' from Current Record of Rights**<br>*DefectCategory.CO_SHARER_FRACTIONAL_DILUTION* | Hindu Succession Act 1956, Section 8 & 10<br>Constitution of India, Article 300A (Right to Property) | **Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84**<br>`bbox: [40.0, 30.0, 100.0, 570.0]` | 10,117.1 m² | Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession. |
| **DEF-007** | 🟠 `HIGH` | **Total Absence of Legal Heir 'Shanti Devi' from Current Record of Rights**<br>*DefectCategory.CO_SHARER_FRACTIONAL_DILUTION* | Hindu Succession Act 1956, Section 8 & 10<br>Constitution of India, Article 300A (Right to Property) | **Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84**<br>`bbox: [40.0, 30.0, 100.0, 570.0]` | 3,372.4 m² | Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession. |
| **DEF-008** | 🔴 `CRITICAL` | **Total Absence of Legal Heir 'Amit Kumar' from Current Record of Rights**<br>*DefectCategory.CO_SHARER_FRACTIONAL_DILUTION* | Hindu Succession Act 1956, Section 8 & 10<br>Constitution of India, Article 300A (Right to Property) | **Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84**<br>`bbox: [40.0, 30.0, 100.0, 570.0]` | 3,372.4 m² | Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession. |
| **DEF-009** | 🟠 `HIGH` | **Total Absence of Legal Heir 'Sunita Kumari' from Current Record of Rights**<br>*DefectCategory.CO_SHARER_FRACTIONAL_DILUTION* | Hindu Succession Act 1956, Section 8 & 10<br>Constitution of India, Article 300A (Right to Property) | **Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84**<br>`bbox: [40.0, 30.0, 100.0, 570.0]` | 3,372.4 m² | Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession. |

## 4. In-Depth Forensic Legal Analysis

### [DEF-001] Omission of Legal Heir (Kamla Devi) without Registered Haq-Tyag (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Visual Citation & Coordinates**: `INT-204, Line: 'Sanctioned in favour of Suresh & Ramesh sons of Ram Lal on oral statement of Patwari.'` | Bounding Box: `[115.0, 42.0, 185.0, 540.0]`
- **Parties Implicated**: `{"omitted_heir": "Kamla Devi", "deceased_predecessor": "Ram Lal", "beneficiaries": ["Suresh Kumar", "Ramesh Kumar"]}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Kamla Devi' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-204 (1996-05-14) sanctioned on the demise of 'Ram Lal'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Prescribed Judicial Action**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-204. Seek immediate correction of Jamabandi entries to restore Kamla Devi's lawful share.

### [DEF-002] Omission of Legal Heir (Amit Kumar) without Registered Haq-Tyag (Severity: `LegalSeverity.CRITICAL`)
- **Defect Category**: `DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Visual Citation & Coordinates**: `INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'` | Bounding Box: `[225.0, 45.0, 295.0, 550.0]`
- **Parties Implicated**: `{"omitted_heir": "Amit Kumar", "deceased_predecessor": "Suresh Kumar", "beneficiaries": ["Ramesh Kumar"]}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Amit Kumar' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Prescribed Judicial Action**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Amit Kumar's lawful share.

### [DEF-003] Omission of Legal Heir (Shanti Devi) without Registered Haq-Tyag (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Visual Citation & Coordinates**: `INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'` | Bounding Box: `[225.0, 45.0, 295.0, 550.0]`
- **Parties Implicated**: `{"omitted_heir": "Shanti Devi", "deceased_predecessor": "Suresh Kumar", "beneficiaries": ["Ramesh Kumar"]}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Shanti Devi' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Prescribed Judicial Action**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Shanti Devi's lawful share.

### [DEF-004] Omission of Legal Heir (Sunita Kumari) without Registered Haq-Tyag (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Visual Citation & Coordinates**: `INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.'` | Bounding Box: `[225.0, 45.0, 295.0, 550.0]`
- **Parties Implicated**: `{"omitted_heir": "Sunita Kumari", "deceased_predecessor": "Suresh Kumar", "beneficiaries": ["Ramesh Kumar"]}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Sunita Kumari' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Prescribed Judicial Action**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Sunita Kumari's lawful share.

### [DEF-005] Unrepresented Minor Mutation (Amit Kumar, Sunita Kumari) without HMGA Sec 8 Sanction (Severity: `LegalSeverity.CRITICAL`)
- **Defect Category**: `DefectCategory.UNREPRESENTED_MINOR_MUTATION`
- **Statutory Enactments Violated**: Hindu Minority and Guardianship Act 1956, Section 6 & 8(2), Indian Majority Act 1875, Section 3, Civil Procedure Code 1908, Order XXXII Rules 1-3
- **Visual Citation & Coordinates**: `Mutation No. INT-389 (2014-08-20), Column 8/11` | Bounding Box: `[225.0, 45.0, 295.0, 550.0]`
- **Parties Implicated**: `{"minors": ["Amit Kumar", "Sunita Kumari"], "transferor_or_applicant": ["Suresh Kumar (Deceased)"], "beneficiaries": ["Ramesh Kumar"]}`
- **Substantive Finding**: STATUTORY MINORITY IMPAIRMENT: Mutation No. INT-389 (2014-08-20) affected the proprietary estate of minor(s) [Amit Kumar, Sunita Kumari] without lawful guardian representation or without mandatory prior sanction from the District Court under Section 8(2) of the Hindu Minority and Guardianship Act, 1956. Any transaction or mutation adverse to a minor without court approval is voidable at the minor's option under Section 8(3) HMGA and void ab initio if completely unrepresented.
- **Prescribed Judicial Action**: Institute suit for Declaration and Invalidation of Mutation No. INT-389 under Section 8(3) of the Hindu Minority and Guardianship Act, 1956 read with Section 31 of the Specific Relief Act, 1963. Limitation commences from the date of attaining majority.

### [DEF-006] Total Absence of Legal Heir 'Kamla Devi' from Current Record of Rights (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Visual Citation & Coordinates**: `Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84` | Bounding Box: `[40.0, 30.0, 100.0, 570.0]`
- **Parties Implicated**: `{"omitted_heir": "Kamla Devi", "co_sharers_recorded": ["Ramesh Kumar"]}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Kamla Devi' (Daughter of Ram Lal) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/3 (10,117.14 m² / 2.5000 Acres). Omission creates an actionable cloud on title.
- **Prescribed Judicial Action**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

### [DEF-007] Total Absence of Legal Heir 'Shanti Devi' from Current Record of Rights (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Visual Citation & Coordinates**: `Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84` | Bounding Box: `[40.0, 30.0, 100.0, 570.0]`
- **Parties Implicated**: `{"omitted_heir": "Shanti Devi", "co_sharers_recorded": ["Ramesh Kumar"]}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Shanti Devi' (Widow / Spouse of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Prescribed Judicial Action**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

### [DEF-008] Total Absence of Legal Heir 'Amit Kumar' from Current Record of Rights (Severity: `LegalSeverity.CRITICAL`)
- **Defect Category**: `DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Visual Citation & Coordinates**: `Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84` | Bounding Box: `[40.0, 30.0, 100.0, 570.0]`
- **Parties Implicated**: `{"omitted_heir": "Amit Kumar", "co_sharers_recorded": ["Ramesh Kumar"]}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Amit Kumar' (Son of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Prescribed Judicial Action**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

### [DEF-009] Total Absence of Legal Heir 'Sunita Kumari' from Current Record of Rights (Severity: `LegalSeverity.HIGH`)
- **Defect Category**: `DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`
- **Statutory Enactments Violated**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Visual Citation & Coordinates**: `Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84` | Bounding Box: `[40.0, 30.0, 100.0, 570.0]`
- **Parties Implicated**: `{"omitted_heir": "Sunita Kumari", "co_sharers_recorded": ["Ramesh Kumar"]}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Sunita Kumari' (Daughter of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Prescribed Judicial Action**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

## 5. Sarvam-105B Jurisprudential Opinion

### Sarvam-105B Title Audit Jurisprudential Opinion
**Subject**: Title Audit & Statutory Succession Discrepancy Matrix for Khasra `452/1, 452/2`, Village `Hastinapur`.
**Claimant**: Amit Kumar (Son of Suresh Kumar) | **Theoretical Lawful Share**: `1/9` | **Recorded Share**: `0 (Omitted)`.

#### 1. Executive Title Health Summary
The official revenue record chain for parcel `12 Bigha 0 Biswa` in Village `Hastinapur` is infected with severe statutory infirmities. A cross-examination of the reconstructed Vanshavali against the Jamabandi and Mutation (Intiqal) history reveals that the title has been illegally diluted and fragmented in direct defiance of mandatory Indian succession and property statutes. The overall title risk is categorized as **CRITICAL / DEFECTIVE**.

#### 2. Statutory Succession & Claimant Entitlement Evaluation
Under the **Hindu Succession Act, 1956** read with the **Hindu Succession (Amendment) Act, 2005** and the landmark Supreme Court ruling in *Vineeta Sharma v. Rakesh Sharma (2020) 9 SCC 1*, the claimant `Amit Kumar` is a statutory Class I legal heir / coparcener with an inviolable inherent entitlement of `1/9`. The omission or reduction of the claimant's share on the revenue record is *ultra vires* and legally untenable.

#### 3. Forensic Defect Analysis
**Defect #1: [HIGH] Omission of Legal Heir (Kamla Devi) without Registered Haq-Tyag** (`DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Evidence Location**: INT-204, Line: 'Sanctioned in favour of Suresh & Ramesh sons of Ram Lal on oral statement of Patwari.' | Bounding Box: `{'ymin': 115.0, 'xmin': 42.0, 'ymax': 185.0, 'xmax': 540.0}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Kamla Devi' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-204 (1996-05-14) sanctioned on the demise of 'Ram Lal'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Judicial Remedy**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-204. Seek immediate correction of Jamabandi entries to restore Kamla Devi's lawful share.

**Defect #2: [CRITICAL] Omission of Legal Heir (Amit Kumar) without Registered Haq-Tyag** (`DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Evidence Location**: INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.' | Bounding Box: `{'ymin': 225.0, 'xmin': 45.0, 'ymax': 295.0, 'xmax': 550.0}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Amit Kumar' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Judicial Remedy**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Amit Kumar's lawful share.

**Defect #3: [HIGH] Omission of Legal Heir (Shanti Devi) without Registered Haq-Tyag** (`DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Evidence Location**: INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.' | Bounding Box: `{'ymin': 225.0, 'xmin': 45.0, 'ymax': 295.0, 'xmax': 550.0}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Shanti Devi' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Judicial Remedy**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Shanti Devi's lawful share.

**Defect #4: [HIGH] Omission of Legal Heir (Sunita Kumari) without Registered Haq-Tyag** (`DefectCategory.OMITTED_LEGAL_HEIR_NO_HAQ_TYAG`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 6 & 8, Registration Act 1908, Section 17(1)(b) & Section 49, Transfer of Property Act 1882, Section 9
- **Evidence Location**: INT-389, Line: 'Transferred to Ramesh Kumar brother of deceased; minor children not represented.' | Bounding Box: `{'ymin': 225.0, 'xmin': 45.0, 'ymax': 295.0, 'xmax': 550.0}`
- **Substantive Finding**: FATAL SUCCESSION DEFECT: Legal heir 'Sunita Kumari' (entitled under Hindu Succession Act) was omitted from Inheritance Mutation No. INT-389 (2014-08-20) sanctioned on the demise of 'Suresh Kumar'. No registered Relinquishment Deed (Haq-Tyag) was executed or registered under Section 17(1)(b) of the Registration Act, 1908. An oral relinquishment or exclusion before the revenue officer is void ab initio (Yellapu Uma Maheswari v. Buddha Jagadheeswararao, (2015) 16 SCC 787).
- **Judicial Remedy**: File Statutory Revenue Appeal under State Land Revenue Act to set aside Mutation No. INT-389. Seek immediate correction of Jamabandi entries to restore Sunita Kumari's lawful share.

**Defect #5: [CRITICAL] Unrepresented Minor Mutation (Amit Kumar, Sunita Kumari) without HMGA Sec 8 Sanction** (`DefectCategory.UNREPRESENTED_MINOR_MUTATION`)
- **Statutory Violation**: Hindu Minority and Guardianship Act 1956, Section 6 & 8(2), Indian Majority Act 1875, Section 3, Civil Procedure Code 1908, Order XXXII Rules 1-3
- **Evidence Location**: Mutation No. INT-389 (2014-08-20), Column 8/11 | Bounding Box: `{'ymin': 225.0, 'xmin': 45.0, 'ymax': 295.0, 'xmax': 550.0}`
- **Substantive Finding**: STATUTORY MINORITY IMPAIRMENT: Mutation No. INT-389 (2014-08-20) affected the proprietary estate of minor(s) [Amit Kumar, Sunita Kumari] without lawful guardian representation or without mandatory prior sanction from the District Court under Section 8(2) of the Hindu Minority and Guardianship Act, 1956. Any transaction or mutation adverse to a minor without court approval is voidable at the minor's option under Section 8(3) HMGA and void ab initio if completely unrepresented.
- **Judicial Remedy**: Institute suit for Declaration and Invalidation of Mutation No. INT-389 under Section 8(3) of the Hindu Minority and Guardianship Act, 1956 read with Section 31 of the Specific Relief Act, 1963. Limitation commences from the date of attaining majority.

**Defect #6: [HIGH] Total Absence of Legal Heir 'Kamla Devi' from Current Record of Rights** (`DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Evidence Location**: Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84 | Bounding Box: `{'ymin': 40.0, 'xmin': 30.0, 'ymax': 100.0, 'xmax': 570.0}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Kamla Devi' (Daughter of Ram Lal) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/3 (10,117.14 m² / 2.5000 Acres). Omission creates an actionable cloud on title.
- **Judicial Remedy**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

**Defect #7: [HIGH] Total Absence of Legal Heir 'Shanti Devi' from Current Record of Rights** (`DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Evidence Location**: Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84 | Bounding Box: `{'ymin': 40.0, 'xmin': 30.0, 'ymax': 100.0, 'xmax': 570.0}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Shanti Devi' (Widow / Spouse of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Judicial Remedy**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

**Defect #8: [CRITICAL] Total Absence of Legal Heir 'Amit Kumar' from Current Record of Rights** (`DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Evidence Location**: Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84 | Bounding Box: `{'ymin': 40.0, 'xmin': 30.0, 'ymax': 100.0, 'xmax': 570.0}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Amit Kumar' (Son of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Judicial Remedy**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

**Defect #9: [HIGH] Total Absence of Legal Heir 'Sunita Kumari' from Current Record of Rights** (`DefectCategory.CO_SHARER_FRACTIONAL_DILUTION`)
- **Statutory Violation**: Hindu Succession Act 1956, Section 8 & 10, Constitution of India, Article 300A (Right to Property)
- **Evidence Location**: Khatauni / Jamabandi (1425 Fasli (2018-2019)), Khatauni/Khewat Khatauni No. 84 | Bounding Box: `{'ymin': 40.0, 'xmin': 30.0, 'ymax': 100.0, 'xmax': 570.0}`
- **Substantive Finding**: TITLE REGISTER OMISSION: Statutory Class I heir 'Sunita Kumari' (Daughter of Suresh Kumar) is totally absent from the ownership column of official Khatauni / Jamabandi (1425 Fasli (2018-2019)). Heir's theoretical entitlement is 1/9 (3,372.38 m² / 0.8333 Acres). Omission creates an actionable cloud on title.
- **Judicial Remedy**: Submit Application for Correction of Revenue Entries (Tarseem-e-Record / Fard-Badar) under Section 38 of the UP Revenue Code, 2006 / Section 37 Punjab Land Revenue Act. Concurrently institute a Civil Suit for Partition & Separate Possession.

#### 4. Actionable Judicial Strategy & Recommended Remedies
1. **Revenue Appeal / Revision**: File an appeal under the relevant State Land Revenue Act (e.g., Sec 13 of the Punjab Land Revenue Act, 1887 or Sec 35(2) of the UP Revenue Code, 2006) to quash the impugned mutation orders as void *ab initio*.
2. **Civil Suit for Declaration & Partition**: Institute a suit before the Senior Civil Judge / Sub-Divisional Officer seeking a Declaration of Title for claimant's theoretical share, with a consequential decree for metes-and-bounds physical partition.
3. **Deed Cancellation**: Where third-party conveyances exceeded lawful shares, invoke Section 31 of the Specific Relief Act, 1963 to cancel the registered sale deeds to the extent of over-alienation.
4. **Interim Injunction**: Move an urgent application under Order XXXIX Rules 1 & 2 CPC restraining the adverse parties from alienating, encumbering, or changing the nature of the suit land during pendency of litigation.

## 6. Actionable Legal Roadmap & Litigation Strategy

1. **Caveat & Urgent Interim Injunction**: File caveat petitions under Section 148A CPC and seek status-quo injunction under Order XXXIX Rules 1 & 2 CPC against any further alienation of the suit Khasras.
2. **Statutory Revenue Appeal**: Challenge the fraudulent/omissive Mutation orders before the Collector/Sub-Divisional Officer under the State Land Revenue Act.
3. **Civil Suit for Partition & Declaration**: Institute a comprehensive Title Suit before the Senior Civil Judge seeking a declaration of Amit Kumar's 1/9 statutory share and physical demarcation by metes and bounds.
4. **Cancellation of Ultra-Vires Sale Deeds**: Seek decree of cancellation under Section 31 of Specific Relief Act 1963 for any conveyances executed beyond the transferors' legitimate holdings.
5. **Revenue Register Rectification**: Apply for Fard-Badar / Tarseem-e-Record to update the official Record of Rights reflecting the true Vanshavali.
