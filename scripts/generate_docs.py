"""
CRESTLINE TECHNOLOGIES — DOCUMENT GENERATOR
Run: python scripts/generate_docs.py
"""

import os

DOCS_BASE = "docs"

def create_dirs():
    for folder in ["hr", "marketing", "product"]:
        os.makedirs(os.path.join(DOCS_BASE, folder), exist_ok=True)
    print("✅ Directory structure created")

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ Created: {path}")

PTO_POLICY = """
CRESTLINE TECHNOLOGIES — PTO POLICY
Last Updated: January 2024 | Version: 3.1
HR Department

1. OVERVIEW
Crestline Technologies provides competitive paid time off to support work-life balance.

2. PTO ACCRUAL BY TENURE
- 0 to 1 year:     10 days per year
- 1 to 3 years:    15 days per year
- 3 to 5 years:    20 days per year
- 5 or more years: 25 days per year

3. ADDITIONAL TIME OFF
- Sick Days:        10 days per year
- Personal Days:    3 days per year
- Bereavement:      5 days for immediate family
- Jury Duty:        Fully paid, unlimited
- Parental Leave:   16 weeks fully paid (primary caregiver)
                    6 weeks fully paid (secondary caregiver)

4. HOW TO REQUEST PTO
Step 1: Log into hr.crestline.com
Step 2: Navigate to Time Off > New Request
Step 3: Select dates and leave type
Step 4: Submit — manager must approve within 48 hours
Rules: 3 or more consecutive days require 2 weeks advance notice.
Same-day requests allowed for sick leave only.

5. PTO CARRYOVER POLICY
- Maximum carryover: 10 days into new calendar year
- Unused days above 10 are forfeited on January 1st

6. FEDERAL HOLIDAYS
11 federal holidays plus 2 floating holidays per year.
Employees may swap federal holidays for cultural or religious observances.

7. CONTACT
hr@crestline.com | hr.crestline.com
"""

REMOTE_WORK_POLICY = """
CRESTLINE TECHNOLOGIES — REMOTE WORK POLICY
Last Updated: March 2024 | Version: 2.4
People Operations

1. HYBRID SCHEDULE BY TEAM
Standard roles:          3 days remote, 2 days in-office per week
Engineering teams:       4 days remote, 1 day in-office (Wednesdays)
Sales and client-facing: 3 days in-office minimum per week
Fully remote roles:      Approved case-by-case at VP level

2. CORE HOURS
All employees must be available 10:00 AM to 3:00 PM Eastern Time, Monday through Friday.
No mandatory meetings outside these hours.

3. HOME OFFICE STIPEND
New hire stipend:              $1,500 one-time (first 30 days)
Annual refresh allowance:      $500 per year
Monthly internet reimbursement: $75 per month
Ergonomic assessment:          Available on request

4. EQUIPMENT REQUIREMENTS
- All employees receive a Crestline Pro laptop on Day 1
- Crestline OS required on all company devices
- CrestSecure VPN mandatory for all remote sessions
- Personal devices not permitted for confidential data

5. SECURITY REQUIREMENTS
- Two-factor authentication mandatory on all accounts
- CrestSecure VPN must be active for all remote work
- Public Wi-Fi prohibited without VPN
- Screen auto-lock required after 5 minutes

6. INTERNATIONAL REMOTE WORK
Up to 30 consecutive days per year working abroad.
HR and Legal approval required 30 days in advance.

7. CONTACT
remote-work@crestline.com | People Operations
"""

ONBOARDING_GUIDE = """
CRESTLINE TECHNOLOGIES — NEW EMPLOYEE ONBOARDING GUIDE
Last Updated: February 2024 | People Operations

WELCOME
Congratulations on joining Crestline Technologies!
We build hardware, software, and cloud solutions for businesses worldwide.

DAY 1 CHECKLIST
- Check in with Reception — collect badge and access card
- 90-minute HR session: benefits enrollment and policy overview
- IT Setup: collect Crestline Pro laptop from IT desk (Floor 3)
- Install: Crestline OS, CrestSecure VPN, Slack, Notion, Okta
- Set up your @crestline.com email account
- Meet your manager — welcome lunch is fully expensed

WEEK 1: ORIENTATION
- New Hire Orientation every Monday 9:00 to 11:00 AM EST
- Mandatory compliance training (3 courses, approx 4 hours):
    Course 1: Data Privacy and Security (must complete by Day 5)
    Course 2: Code of Conduct and Ethics
    Course 3: Workplace Safety and Harassment Prevention
- Product Deep Dive: 3-hour overview of all 5 Crestline products
- Shadow your team for 3 days before independent work begins

MONTH 1: RAMP UP
- Complete 30-day goals document with manager (due Day 10)
- Attend 2 to 3 team meetings as observer
- Complete product certification for your core product area
- Day 30 check-in with manager

MONTHS 2 AND 3: INDEPENDENCE
- Own at least 1 project independently
- Present to your team at a weekly sync
- Day 60: Mid-point review with HR and manager
- Day 90: Full performance assessment

KEY TOOLS
- Slack:     crestline.slack.com
- Notion:    notion.crestline.com
- GitHub:    github.com/crestline-tech
- Workday:   workday.crestline.com (PTO, payroll, benefits)
- Okta:      okta.crestline.com (single sign-on)

BENEFITS ENROLLMENT
Deadline: 30 days from start date. No exceptions.
Health, dental, vision, and 401k available from Day 1.
Company 401k match: 4% with 3-year vesting.
Wellness stipend: $100 per month (gym, therapy, meditation apps).

KEY CONTACTS
IT Help:  it-support@crestline.com  Ext. 1001
HR:       hr@crestline.com          Ext. 1002
Security: security@crestline.com    Ext. 1003
Payroll:  payroll@crestline.com     Ext. 1004
"""

CRESTLINE_X_LAUNCH = """
CRESTLINE X — PRODUCT LAUNCH STRATEGY 2024
Campaign: Power Meets Simplicity
Marketing Department | Q1 to Q2 2024

1. PRODUCT OVERVIEW
Crestline X is our flagship smartphone for working professionals.
Price: $499 | Launch date: March 15, 2024
Key features: CrestChip M3, 48MP camera, 5G, Crestline OS native sync, 72-hour battery.

2. TARGET AUDIENCE
Primary:   Working professionals aged 25 to 40, income $75K+, urban markets
Secondary: Small business owners aged 35 to 55 integrating with Crestline Cloud
Tertiary:  College students aged 18 to 24 (aspirational segment)

3. KEY MESSAGES
Primary:       The phone that works as hard as you do
Secondary:     Seamlessly connected to your entire Crestline ecosystem
Proof point 1: 72-hour battery — longest in its price class
Proof point 2: CrestChip M3 — 40% faster than previous generation

4. CHANNEL STRATEGY AND BUDGET
Total budget: $2,100,000
Instagram (Stories and Reels):   $630,000 (30%)
YouTube (Pre-roll and Sponsored): $420,000 (20%)
LinkedIn (Sponsored posts):       $315,000 (15%)
Google Search:                    $420,000 (20%)
PR and Launch Events:             $210,000 (10%)
Retail and Partner Marketing:     $105,000 (5%)

5. LAUNCH TIMELINE
January 15:  Press briefings begin under NDA
February 1:  Influencer seeding — devices shipped
March 1:     Embargo lift — reviews go live
March 15:    Global launch — NYC event at Hudson Yards (500 attendees)
April 1:     Retargeting campaigns launch

6. Q1 2024 ACTUAL RESULTS
Impressions: 52.3 million (target 50M — exceeded)
Units sold:  26,800 (target 25,000 — plus 7.2%)
Google CTR:  4.8% (industry benchmark 2.1%)
NPS Day 90:  61 (target 55 — exceeded)
"""

CRESTLINE_WATCH_CAMPAIGN = """
CRESTLINE WATCH — CAMPAIGN BRIEF Q3 2024
Campaign: Time Redefined
Marketing Department | Q3 2024

1. PRODUCT OVERVIEW
Crestline Watch is our premium smartwatch for health and productivity.
Price: $299 | Launch date: September 10, 2024
Key features: 7-day battery, FDA-cleared ECG, blood oxygen monitoring,
sleep tracking, stress monitoring, CrestPay, Crestline OS native sync.

2. TARGET AUDIENCE
Primary:   Health-conscious professionals aged 30 to 50, income $90K+
Secondary: Corporate wellness program buyers (HR and benefits managers)
Tertiary:  Medical monitoring users aged 50 to 65

3. KEY MESSAGES
Primary:       Your health. Your time. Redefined.
Secondary:     The only watch that connects your health to your work
Proof point 1: FDA-cleared ECG — clinically validated
Proof point 2: 7-day battery — no daily charging needed

4. CHANNEL STRATEGY AND BUDGET
Total budget: $1,800,000
Instagram and TikTok:         $540,000 (30%)
YouTube health creators:      $360,000 (20%)
Fitness app partnerships:     $270,000 (15%) — Peloton, Strava, MyFitnessPal
Corporate wellness B2B:       $360,000 (20%)
NYC Launch Event Sept 10:     $180,000 (10%) — The Vessel, Hudson Yards
Print WSJ and health magazines: $90,000 (5%)

5. B2B CORPORATE WELLNESS PROGRAM
Minimum order: 50 units
Corporate discount: 20% off for 50 plus units, 25% off for 200 plus units
HR dashboard: aggregated anonymized health trends
Integrations: Workday and BambooHR
Pilot confirmed: 3 Fortune 500 companies for Q3 2024

6. Q3 TARGETS
Pre-orders before launch:  8,000 units
Units sold Q3:             18,000 units
Units sold Q4 holiday:     28,000 units
Total impressions:         35 million in 60 days
"""

CRESTLINE_PRO_CAMPAIGN = """
CRESTLINE PRO — B2B ENTERPRISE CAMPAIGN 2024
Campaign: Work Without Limits
Marketing Department | Full Year 2024

1. PRODUCT OVERVIEW
Crestline Pro is our flagship business laptop for enterprise customers.
Base price: $1,999 | Pro Max: $2,499
Key features: CrestChip M3 Pro, 18-hour battery, Crestline OS Enterprise,
military-grade durability, CrestSecure hardware encryption, Crestline Cloud integration.

2. TARGET AUDIENCE
Primary:   IT Directors and CIOs at companies with 200 to 5,000 employees
Secondary: Procurement managers at mid-market companies seeking Windows and Mac alternatives
Tertiary:  Power users — developers, designers, data analysts

3. KEY MESSAGES
Primary:       Enterprise-grade security. Consumer-grade experience.
Secondary:     The laptop your IT team will actually love managing
Proof point 1: CrestSecure hardware encryption — zero IT overhead
Proof point 2: 18-hour battery — full workday on one charge
Financial ROI: $420 saved per device per year vs comparable Windows (TCO study available)

4. SALES MOTION
Inbound (30%):      LinkedIn thought leadership, Google Search, case studies
Outbound (50%):     SDR cold outreach, ABM for top 200 accounts, executive roundtables
Partner-led (20%):  CDW, Insight Direct, Deloitte Digital, Accenture

5. SALES CYCLE
Average deal size:  $180,000 (approximately 90 units at $2,000)
SMB cycle:          45 days
Enterprise cycle:   90 days

6. FULL YEAR 2024 RESULTS (YTD Q3)
Pipeline generated:       $45 million
Revenue closed YTD:       $22 million
Win rate vs Mac:          48%
Win rate vs Windows:      61%
Net revenue retention:    118%
Enterprise clients Q2:    340 companies
IT admin NPS:             72 (industry average 38)
"""

CRESTLINE_OS_CHANGELOG = """
CRESTLINE OS — VERSION HISTORY AND RELEASE NOTES
Engineering and Product Team | Last Updated: June 2024

CRESTLINE OS v3.2 — Released May 15, 2024
Status: STABLE — Recommended for all devices

NEW FEATURES
Focus Mode 2.0:
  AI-suggested focus schedules based on calendar and work patterns.
  Reduces context switching by estimated 40%.

CrestSync Ultra:
  Zero-latency clipboard and handoff across all Crestline devices.
  Copy on Watch, paste on Pro in under 200 milliseconds.

Smart Notifications:
  ML-powered notification batching reduces interruptions by 60%.

Crestline Cloud Sync v2:
  New delta-sync protocol reduces sync time by 40%.
  Background sync uses under 50MB RAM.

BUG FIXES
CRITICAL: Fixed battery drain on Crestline Pro 2023 models.
  Affected 12% of devices. Idle drain reduced from 18% to under 2% per hour.
  Root cause: background CrestSync process not releasing CPU.
Fixed Bluetooth audio dropout on Crestline X with third-party headphones.
Resolved memory leak in CrestMail on devices with 8GB RAM.
Fixed Wi-Fi reconnection delay after sleep — reduced from 30 seconds to under 1 second.
Corrected time zone handling for calendar events created offline.

SECURITY PATCHES
CVE-2024-1891 — CRITICAL: Privilege escalation in CrestSecure daemon.
CVE-2024-1823 — MEDIUM: Bluetooth pairing spoofing vulnerability.
CVE-2024-1756 — LOW: Browser cache exposure on shared devices.

PERFORMANCE
App launch time:  18% faster on CrestChip M3 devices
Boot time:        Reduced from 8.2 seconds to 5.1 seconds
RAM efficiency:   22% improvement in background task management

CRESTLINE OS v3.1 — Released February 8, 2024
Status: DEPRECATED — upgrade to v3.2 strongly recommended

NEW FEATURES
Focus Mode original version.
Redesigned Notification Center with grouped categories.
CrestPay contactless payments via Watch (US only).
Voice Control 3.0 with 40 new commands.

BUG FIXES
Fixed crash in CrestCloud sync for files larger than 2GB.
Resolved incorrect battery percentage on Watch.
Fixed keyboard layout switching for multilingual users.

CRESTLINE OS v3.0 — Released October 3, 2023
Status: DEPRECATED — no support, immediate upgrade required

MAJOR RELEASE: Complete platform redesign.
New CrestUI design language.
Unified control center across all Crestline devices.
CrestAI assistant integrated at OS level.
Third-party developer ecosystem opened — App Store launched.
Enterprise MDM built directly into OS.

SUPPORT POLICY
v3.2: Full support (current)
v3.1: Security patches only until November 2024
v3.0 and below: No support — upgrade immediately

HOW TO UPDATE
Settings > System > Software Update
Time: 8 to 12 minutes. Device restart required.
"""

CLOUD_API_DOCS = """
CRESTLINE CLOUD — API DOCUMENTATION
API Version: v2 | Last Updated: April 2024

BASE URL
https://api.crestlinecloud.com/v2

AUTHENTICATION
Method: Bearer Token (OAuth 2.0)

Get access token:
POST https://auth.crestlinecloud.com/oauth/token
Body: client_id, client_secret, grant_type: client_credentials

Include in all requests:
Authorization: Bearer {access_token}
Token expiry: 3,600 seconds (1 hour).

RATE LIMITS
Free Tier:
  100 requests per hour
  1 GB storage
  Max file size: 100 MB
  No SLA

Starter ($29 per month):
  2,000 requests per hour
  100 GB storage
  Max file size: 1 GB
  99.5% uptime SLA

Business ($149 per month):
  10,000 requests per hour
  5 TB storage
  Max file size: 50 GB
  99.9% uptime SLA
  Priority support

Enterprise (custom pricing):
  Unlimited requests
  Unlimited storage
  99.99% uptime SLA
  Dedicated infrastructure
  24/7 dedicated support

Rate limit headers on every response:
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9847
X-RateLimit-Reset: 1717200000

CORE ENDPOINTS
POST   /v2/storage/upload              Upload a file
GET    /v2/storage/files               List all files
GET    /v2/storage/files/{id}          Get file metadata
GET    /v2/storage/files/{id}/download Download file content
DELETE /v2/storage/files/{id}          Delete a file
PATCH  /v2/storage/files/{id}          Update file metadata
POST   /v2/storage/folders             Create folder
GET    /v2/storage/folders/{id}        Get folder contents
GET    /v2/users                       List organization users (admin only)
POST   /v2/users/invite                Invite new user (admin only)
GET    /v2/analytics/storage           Storage usage breakdown
GET    /v2/analytics/requests          API request history

ERROR CODES
400: Bad Request — invalid parameters
401: Unauthorized — invalid or expired token
403: Forbidden — insufficient permissions
404: Not Found — resource does not exist
413: Payload Too Large — file exceeds plan limit
429: Too Many Requests — rate limit exceeded
500: Internal Error — retry with exponential backoff
503: Service Unavailable — check status.crestlinecloud.com

WEBHOOKS
POST /v2/webhooks
Supported events: file.uploaded, file.deleted, file.shared,
user.invited, user.removed, storage.quota_warning

SDKS AVAILABLE
Python:     pip install crestline-cloud-sdk
JavaScript: npm install @crestline/cloud-sdk
Java:       Available via Maven Central
Go:         go get github.com/crestline/cloud-go

Support: api-support@crestline.com
Docs:    docs.crestlinecloud.com
Status:  status.crestlinecloud.com
"""

SYSTEM_REQUIREMENTS = """
CRESTLINE OS v3.2 — SYSTEM REQUIREMENTS
Engineering and Product Team | May 2024

CRESTLINE PRO (LAPTOP)

Minimum requirements:
  Processor:    CrestChip M2 or M2 Pro
  RAM:          8 GB unified memory
  Storage:      256 GB NVMe SSD
  Display:      1440p, 60Hz
  Battery:      60 Wh (12-hour rated life)
  Connectivity: Wi-Fi 6, Bluetooth 5.2, USB-C Thunderbolt 3

Recommended requirements:
  Processor:    CrestChip M3 or M3 Pro
  RAM:          16 GB unified memory
  Storage:      512 GB NVMe SSD
  Display:      2560x1600 Liquid Retina, 120Hz ProMotion
  Battery:      80 Wh (18-hour rated life)
  Connectivity: Wi-Fi 6E, Bluetooth 5.3, USB-C Thunderbolt 4 x3

Enterprise and power user:
  Processor:    CrestChip M3 Max
  RAM:          32 to 64 GB unified memory
  Storage:      1 to 2 TB NVMe SSD
  External:     Dual 4K display support

CRESTLINE X (SMARTPHONE)

Minimum:
  Processor: CrestChip M2 Mobile
  RAM:       6 GB
  Storage:   128 GB
  Battery:   4,500 mAh

Recommended:
  Processor: CrestChip M3 Mobile
  RAM:       8 GB
  Storage:   256 GB or 512 GB
  Battery:   5,200 mAh (72-hour rated life)
  Connectivity: 5G, Wi-Fi 6E, Bluetooth 5.3, NFC for CrestPay

CRESTLINE WATCH

Minimum:
  Processor:    CrestChip W1
  RAM:          1 GB
  Storage:      16 GB
  Paired device: Crestline X 2022 or newer, or Crestline Pro running OS 3.1+

Recommended:
  Processor:    CrestChip W2
  RAM:          2 GB
  Storage:      32 GB
  Paired device: Crestline X running OS 3.2

Health sensors:
  ECG: FDA cleared, CE marked
  Blood oxygen SpO2: accuracy plus or minus 2%
  Heart rate: optical, continuous 24/7
  Accelerometer and gyroscope: 6-axis
  Skin temperature sensor
  GPS: Crestline Watch Ultra only

CRESTLINE CLOUD (BROWSER AND APP)

Browser requirements:
  Chrome 110+, Firefox 115+, Safari 16+, Edge 110+
  Minimum resolution: 1280x720

Internet connection:
  Minimum: 25 Mbps for smooth operation
  Recommended: 100 Mbps for large file uploads

Native app on Crestline OS:
  Auto-installed with Crestline OS 3.0 and above
  Background sync uses less than 50 MB RAM
  Default local cache: 2 GB (configurable 0 to 20 GB)

Third-party OS support (manual install):
  Windows 10 and 11
  macOS 13 Ventura and newer
  Ubuntu 22.04 LTS and newer

ENTERPRISE DEPLOYMENT

MDM requirements:
  CrestMDM native (recommended) or Apple DEP compatible
  Ports 443 and 8443 open to *.crestlinecloud.com
  PAC files and explicit proxy configurations supported

Supported identity providers:
  Okta (recommended)
  Microsoft Azure AD and Entra ID
  Google Workspace
  Any SAML 2.0 compatible provider

COMPATIBILITY WITH CRESTLINE OS 3.2

Fully supported:
  Crestline Pro 2022, 2023, 2024 (M2 and M3 chips)
  Crestline X 2022, 2023, 2024
  Crestline Watch Series 2 and 3

Not supported (end of life):
  Crestline Pro 2020 and older
  Crestline X 2020 and older
  Crestline Watch Series 1

Check compatibility: Settings > System > Check Compatibility
Or visit: support.crestline.com/compatibility
"""

def generate_all_docs():
    create_dirs()
    write_file(os.path.join(DOCS_BASE, "hr", "pto_policy.txt"), PTO_POLICY)
    write_file(os.path.join(DOCS_BASE, "hr", "remote_work_policy.txt"), REMOTE_WORK_POLICY)
    write_file(os.path.join(DOCS_BASE, "hr", "onboarding_guide.txt"), ONBOARDING_GUIDE)
    write_file(os.path.join(DOCS_BASE, "marketing", "crestline_x_launch.txt"), CRESTLINE_X_LAUNCH)
    write_file(os.path.join(DOCS_BASE, "marketing", "crestline_watch_campaign.txt"), CRESTLINE_WATCH_CAMPAIGN)
    write_file(os.path.join(DOCS_BASE, "marketing", "crestline_pro_campaign.txt"), CRESTLINE_PRO_CAMPAIGN)
    write_file(os.path.join(DOCS_BASE, "product", "crestline_os_changelog.txt"), CRESTLINE_OS_CHANGELOG)
    write_file(os.path.join(DOCS_BASE, "product", "cloud_api_docs.txt"), CLOUD_API_DOCS)
    write_file(os.path.join(DOCS_BASE, "product", "system_requirements.txt"), SYSTEM_REQUIREMENTS)
    print(f"\n✅ All 9 documents generated under ./{DOCS_BASE}/")

if __name__ == "__main__":
    print("📝 Crestline Content Engineer — Generating Qdrant Documents")
    print("=" * 55)
    generate_all_docs()
    print("=" * 55)
    