# GUI Manual Testing Guide

## Prerequisites
✅ All automated tests pass (59/59)
✅ Tkinter is available (version 8.6)

## How to Launch the GUI
```bash
python gui_main.py
```

---

## Test 1: GUI Startup and Initialization

### Steps:
1. Run `python gui_main.py`
2. Observe the main window

### Expected Results:
- [ ] Main window opens without errors
- [ ] Window title is "Email Signature Generator"
- [ ] Window has reasonable default size
- [ ] Two tabs are visible: "Signature" and "Settings"
- [ ] "Signature" tab is selected by default
- [ ] All form fields are visible and empty
- [ ] Status bar is visible at the bottom

### Notes:
_Record any issues here_

---

## Test 2: Form Validation with Valid Inputs

### Steps:
1. Enter valid data in each field:
   - Name: "John Doe"
   - Position: "Software Engineer"
   - Address: "Lisbon, Portugal"
   - Phone: "+351 21 123 4567"
   - Mobile: "+351 91 234 5678"
   - Email: "john.doe@example.com"
   - Website: "www.example.com"

### Expected Results:
- [ ] No validation errors appear
- [ ] Email field shows green checkmark or valid indicator
- [ ] Phone fields show green checkmark or valid indicator
- [ ] Generate button becomes enabled
- [ ] Preview button becomes enabled

### Notes:
_Record any issues here_

---

## Test 3: Form Validation with Invalid Inputs

### Steps:
1. Enter invalid email: "notanemail"
2. Observe validation feedback
3. Enter invalid phone: "abc123"
4. Observe validation feedback

### Expected Results:
- [ ] Invalid email shows red border or error indicator
- [ ] Error message appears for email (e.g., "Invalid email format")
- [ ] Invalid phone shows red border or error indicator
- [ ] Error message appears for phone
- [ ] Generate button remains disabled

### Steps (continued):
5. Correct the email to "valid@example.com"
6. Correct the phone to "+351 21 123 4567"

### Expected Results:
- [ ] Error indicators disappear
- [ ] Valid indicators appear (green checkmark)
- [ ] Generate button becomes enabled

### Notes:
_Record any issues here_

---

## Test 4: Signature Generation Workflow

### Steps:
1. Fill in all required fields with valid data (use Test 2 data)
2. Click "Generate Signature" button
3. Observe the process

### Expected Results:
- [ ] Status message shows "Generating signature..."
- [ ] Generate button becomes disabled during generation
- [ ] Success message appears with file path
- [ ] File is created in the output directory
- [ ] Option to open containing folder is available
- [ ] Generate button re-enables after completion

### Steps (continued):
4. Navigate to the output directory
5. Verify the signature file exists

### Expected Results:
- [ ] PNG file exists with correct name
- [ ] File can be opened and displays signature correctly
- [ ] Signature contains all entered information

### Notes:
_Record any issues here_

---

## Test 5: Preview Functionality

### Steps:
1. Fill in all required fields with valid data
2. Click "Preview" button
3. Observe the preview

### Expected Results:
- [ ] Preview generates without errors
- [ ] Preview image appears in the preview section
- [ ] Preview shows all entered information
- [ ] Preview is sized appropriately for viewing

### Steps (continued):
4. Change the name field to "Jane Smith"
5. Wait a moment or click preview again

### Expected Results:
- [ ] Preview updates to show "Jane Smith"
- [ ] Auto-update works (if implemented)

### Notes:
_Record any issues here_

---

## Test 6: Profile Save/Load/Delete

### Test 6a: Save Profile
#### Steps:
1. Fill in form with test data
2. Click "Save Profile" button
3. Enter profile name: "Test Profile 1"
4. Click OK/Save

#### Expected Results:
- [ ] Dialog prompts for profile name
- [ ] Success message appears
- [ ] Profile file is created in profiles/ directory

### Test 6b: Load Profile
#### Steps:
1. Clear all form fields
2. Click "Load Profile" button
3. Select "Test Profile 1" from list
4. Click OK/Load

#### Expected Results:
- [ ] Dialog shows list of available profiles
- [ ] "Test Profile 1" appears in the list
- [ ] All form fields populate with saved data
- [ ] Data matches what was saved

### Test 6c: Delete Profile
#### Steps:
1. Click "Delete Profile" button
2. Select "Test Profile 1"
3. Confirm deletion

#### Expected Results:
- [ ] Confirmation dialog appears
- [ ] Profile is removed from list
- [ ] Profile file is deleted from profiles/ directory

### Notes:
_Record any issues here_

---

## Test 7: Settings Editing and Saving

### Steps:
1. Click on "Settings" tab
2. Observe current configuration values

### Expected Results:
- [ ] Settings tab displays without errors
- [ ] Color settings show current values
- [ ] Dimension settings show current values
- [ ] Font path settings show current values

### Steps (continued):
3. Modify a dimension value (e.g., change width to 800)
4. Try entering invalid dimension (e.g., "abc")
5. Click "Save Settings" button

### Expected Results:
- [ ] Invalid dimension is rejected with error message
- [ ] Valid dimension is accepted
- [ ] Settings save successfully
- [ ] Success message appears
- [ ] Configuration file is updated

### Steps (continued):
6. Close and reopen the GUI
7. Check Settings tab

### Expected Results:
- [ ] Modified settings persist
- [ ] New dimension value (800) is displayed

### Notes:
_Record any issues here_

---

## Test 8: Logo Selection and Preview

### Steps:
1. Return to "Signature" tab
2. Click "Browse Logo" button
3. Observe file picker dialog

### Expected Results:
- [ ] File picker opens
- [ ] Filter shows only PNG and JPG files
- [ ] Can navigate to logo.png in project root

### Steps (continued):
4. Select logo.png
5. Click Open

### Expected Results:
- [ ] Logo file path displays in GUI
- [ ] Logo thumbnail preview appears
- [ ] Preview is appropriately sized

### Steps (continued):
6. Generate preview or signature
7. Verify logo appears in output

### Expected Results:
- [ ] Selected logo is used in signature
- [ ] Logo is properly positioned and sized

### Notes:
_Record any issues here_

---

## Test 9: Error Handling Scenarios

### Test 9a: Invalid Logo File
#### Steps:
1. Manually enter invalid logo path: "/nonexistent/logo.png"
2. Try to generate preview

#### Expected Results:
- [ ] Error message appears
- [ ] Application does not crash
- [ ] Error message is clear and helpful

### Test 9b: Read-Only Output Directory
#### Steps:
1. (Skip if difficult to set up)
2. Try to generate signature to read-only location

#### Expected Results:
- [ ] Error message about permissions
- [ ] Application does not crash

### Test 9c: Missing Required Fields
#### Steps:
1. Leave name field empty
2. Try to generate signature

#### Expected Results:
- [ ] Generate button is disabled
- [ ] OR error message appears
- [ ] Application does not crash

### Notes:
_Record any issues here_

---

## Test 10: Platform-Specific Testing (macOS)

### Steps:
1. Test keyboard shortcuts (Cmd+Q to quit, etc.)
2. Test window minimize/maximize
3. Test window close button
4. Test file dialogs (native macOS appearance)

### Expected Results:
- [ ] Keyboard shortcuts work as expected
- [ ] Window controls work properly
- [ ] File dialogs use native macOS style
- [ ] Application exits cleanly when closed

### Steps (continued):
5. Close window using close button (red X)

### Expected Results:
- [ ] Application exits without errors
- [ ] No error messages in terminal
- [ ] Temporary files are cleaned up

### Notes:
_Record any issues here_

---

## Summary Checklist

After completing all tests above:

- [ ] All automated tests pass (59/59) ✅
- [ ] GUI starts without errors
- [ ] Form validation works correctly
- [ ] Signature generation works
- [ ] Preview functionality works
- [ ] Profile save/load/delete works
- [ ] Settings editing works
- [ ] Logo selection works
- [ ] Error handling is graceful
- [ ] Platform-specific features work
- [ ] Application exits cleanly

---

## Issues Found

_List any issues discovered during testing:_

1. 
2. 
3. 

---

## Test Completion

Date: _______________
Tester: _______________
Platform: macOS
Python Version: 3.13.7
Tkinter Version: 8.6

Overall Status: [ ] PASS  [ ] FAIL  [ ] NEEDS REVIEW
