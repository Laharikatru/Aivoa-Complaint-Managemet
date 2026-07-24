## SOP: AI-Powered Customer Complaint Intake, Analysis, and Review Workflow

### Objective

This SOP explains how to capture a customer complaint, extract key complaint details using AI, review and correct the extracted data, run deeper complaint analysis, and commit the complaint for human-reviewed quality management follow-up. The process is designed to help a team member work efficiently while keeping human oversight as the final approval step.

### Key Steps

**1. Open the complaint intake screen and enter the complaint text** [0:40](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=40)

![generated-image-at-00:00:40](https://loom.com/i/278285ee677c4ababb17140a90432b83?workflows_screenshot=true)

- Launch the complaint management application.
- Navigate to the **Customer Complaint** screen.
- Paste or type the full complaint narrative into the intake field.
- Confirm the complaint text is complete before submitting for AI extraction.

**2. Review the AI-extracted complaint fields** [1:23](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=83)

![generated-image-at-00:01:23](https://loom.com/i/71ce3480eac04f729b2247c75d8d5ea0?workflows_screenshot=true)

- After submission, review the AI-generated extraction results.
- Verify that the system has identified key fields such as: 
  - Product name
  - Batch number
  - Affected quantity
  - Summary of the reported issue
- Check that the extracted information matches the original complaint text.

**3. Correct any inaccurate extracted data** [2:34](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=154)

![generated-image-at-00:02:34](https://loom.com/i/7183b4b734474477ae9648af4792b0df?workflows_screenshot=true)

- If the AI extracts an incorrect value, enter a correction message.
- Clearly state the correct value and the field that needs updating.
- Recheck the updated record after the system applies the correction.
- Confirm the corrected field now reflects the intended value.

**4. Validate complaint status and commit the complaint** [3:22](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=202)

![generated-image-at-00:03:22](https://loom.com/i/1077531b6c6948239f4049ae5d2f7e0c?workflows_screenshot=true)

- Review the complaint status before finalizing it.
- Confirm the record is in the correct state for submission.
- Click **Commit Complaint** to lock the complaint record.
- Verify the status/flag changes to show the complaint has been committed.

**5. Confirm database storage and record structure** [4:07](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=247)

![generated-image-at-00:04:07](https://loom.com/i/d3aee42070534a61a79afb90769b8ee4?workflows_screenshot=true)

- Check that the complaint is stored in the database.
- Verify the system includes the required database components such as: 
  - Tables
  - Functions
  - Triggers
  - SQL editor/table editor support
- Ensure the complaint record is saved in the expected table structure for downstream processing.

**6. Understand the application architecture and data model** [4:48](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=288)

![generated-image-at-00:04:48](https://loom.com/i/a751199d350c4a89ada90e4e3d99f783?workflows_screenshot=true)

- Review the FastAPI entry point and confirm it registers the required routers.
- Verify the application automatically creates database tables on startup.
- Confirm the complaint model is the central table used by the system.
- Ensure the model includes both intake fields and AI-extracted fields needed for complaint handling.

**7. Populate the complaint record with extracted and intake details** [6:00](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=360)

![generated-image-at-00:06:00](https://loom.com/i/6cd2c561f6324ef4a32df26c14ced388?workflows_screenshot=true)

- Ensure the complaint form is populated with all extracted details.
- Confirm the record includes relevant fields such as: 
  - Source/customer
  - Product details
  - Batch/lot information
  - Affected quantity
  - Date and site
  - Category and concession details
- Verify the record is complete enough for dashboard analysis.

**8. Open the dashboard and review complaint status** [6:30](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=390)

![generated-image-at-00:06:30](https://loom.com/i/379a748ae5ca40d583eb9714a99178a8?workflows_screenshot=true)

- Navigate to the dashboard after the complaint is saved.
- Review the list of complaints and their current status.
- Check whether the complaint is marked as analyzed or not analyzed.
- Confirm the dashboard displays key operational fields such as customer, product, status, and AI risk.

**9. Run the AI analysis workflow** [7:17](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=437)

![generated-image-at-00:07:17](https://loom.com/i/a821d51a05c94f3693486f6e7e0badf6?workflows_screenshot=true)

- Select the complaint record to analyze.
- Run the AI analysis process.
- Review the six analysis outputs presented by the system.
- Use the analysis results to support triage and investigation planning.

**10. Review completeness, classification, and risk outputs** [7:57](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=477)

![generated-image-at-00:07:57](https://loom.com/i/e8f18e0cd084488a8cf4bf0bd2707c67?workflows_screenshot=true)

- Check the complaint summary generated by the AI.
- Review the completeness checker score and any missing fields.
- Confirm the AI classification output, including severity and rationale.
- Review the risk-related outputs and any similarity or match indicators.
- Use these results to determine whether the complaint needs additional review or escalation.

**11. Review root cause and draft CAPA suggestions** [9:02](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=542)

![generated-image-at-00:09:02](https://loom.com/i/594119fcdf9c462e899d2fa6f4fe0909?workflows_screenshot=true)

- Examine the AI-generated root cause analysis.
- Review any suggested contributing factors such as moisture ingress or humidity exposure.
- Check the draft CAPA output.
- Treat CAPA suggestions as draft guidance for human review, not as final decisions.

**12. Review the complaint log and analysis fields** [9:42](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=582)

![generated-image-at-00:09:42](https://loom.com/i/4a9e12dbb3aa493ca835dba8d2aaaf52?workflows_screenshot=true)

- Open the complaint log view.
- Confirm the record includes operational and analytical fields such as: 
  - Product name and strength
  - Batch/lot details
  - Affected quantity
  - Manufacturing and expiry dates
  - Facility name
  - Product material
  - Effect analysis
  - AI-computed risk assessment
- Verify the complaint record is complete enough for quality review and follow-up.

**13. Understand the analysis pipeline and tool execution logic** [10:06](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=606)

![generated-image-at-00:10:06](https://loom.com/i/57a24c922b054016b748dffba46fa451?workflows_screenshot=true)

- Review the graph-based workflow used by the system.
- Confirm the complaint extraction pipeline runs as a two-node process.
- Confirm the deeper analysis pipeline runs as a six-node process.
- Note that certain steps are conditionally gated, such as CAPA generation depending on completeness.
- Use this structure to understand why some outputs may not appear until required fields are present.

**14. Use fixed tool routing and JSON prompting for reliability** [11:11](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=671)

![generated-image-at-00:11:11](https://loom.com/i/6640b35e859e42f08232bb71576afc42?workflows_screenshot=true)

- Follow the system design that uses a fixed sequence with conditional gates.
- Do not rely on the model to choose tools arbitrarily.
- Use each tool through its own endpoint when testing or troubleshooting.
- Prefer JSON prompting for consistent behavior across models.
- Apply the configured model and fallback strategy as defined in the system.

**15. Apply human review and sign-off before closure** [13:17](https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea?t=797)

![generated-image-at-00:13:17](https://loom.com/i/d3877bac0be6444aa48a9116f68e3761?workflows_screenshot=true)

- Treat all CAPA outputs as hypotheses or drafts.
- Require human review before any final quality decision is made.
- Ensure completeness checks happen before deeper analysis and final sign-off.
- Use the AI to reduce manual effort and surface inconsistencies, but keep the human as the final approver.

### Cautionary Notes

- Do not treat AI-generated classifications, root causes, or CAPA suggestions as final quality decisions.
- Always verify extracted complaint data against the original complaint text before committing the record.
- If required fields are missing, complete them before relying on deeper analysis outputs.
- Ensure a qualified human reviewer signs off before closure or escalation.
- Be careful when correcting AI-extracted values so the update applies to the correct field and record.

### Tips for Efficiency

- Paste a complete complaint narrative at intake to improve extraction quality.
- Correct errors immediately after extraction to avoid downstream rework.
- Use the completeness checker early to identify missing fields before running deeper analysis.
- Review dashboard status indicators first to quickly identify which complaints need attention.
- Use the dedicated tool endpoints for testing individual functions instead of rerunning the full workflow.
- Keep the complaint record structured and consistent so AI analysis and CAPA drafting are more reliable.

### Link to Loom

<https://loom.com/share/259d457c592c4ef0aac73f6d06cd72ea>
