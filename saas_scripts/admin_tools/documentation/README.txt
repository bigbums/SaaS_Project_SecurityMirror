===============================
QA Toolkit for menu.ps1 Script
===============================

This toolkit contains everything you need to perform quality assurance testing on the PowerShell script: menu.ps1

-------------------------------
Contents of this Toolkit
-------------------------------
1. menu_script_QA_checklist.docx
   - Editable Word document with a step-by-step QA checklist.

2. menu_script_QA_checklist.pdf
   - PDF version of the QA checklist for easy viewing and printing.

3. smoke_test.ps1
   - PowerShell script that automatically runs key test cases for menu.ps1.

-------------------------------
How to Use This Toolkit
-------------------------------

1. Place all files in the same folder as your menu.ps1 script:
   C:\Users\DELL\saas_scripts\admin_tools

2. Run the smoke test:
   Open PowerShell and execute:
   pwsh.exe -File "C:\Users\DELL\saas_scripts\admin_tools\smoke_test.ps1"

   This will automatically test:
   - Option 1: Reset DB
   - Option 2: Seed DB
   - Option 7: Full Automated Test
   - Option X: Pipeline Reset→Seed→Full Test
   - Option 8: View current log
   - Option 9: Clear current log
   - Option A: List all logs
   - Option D: Delete old logs
   - Option Z: Invalid input test

3. Review the output in the PowerShell console to confirm expected behavior.

4. Open the checklist (DOCX or PDF) and manually verify:
   - Menu displays correctly
   - Help/About section works
   - Logs are handled properly
   - Invalid input is caught
   - Script exits cleanly with option 0

-------------------------------
Notes
-------------------------------
- Ensure PowerShell Core (pwsh.exe) is installed.
- Run PowerShell as Administrator if required by your script.
- This toolkit is designed for manual and automated QA validation.

