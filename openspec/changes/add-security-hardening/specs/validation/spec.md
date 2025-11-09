# Input Validation Specification

## ADDED Requirements

### Requirement: Input Validation Framework
The system SHALL validate all user inputs using Marshmallow schemas before processing to prevent injection attacks and data corruption.

**Validation Rules:**
- All form inputs must pass schema validation
- Invalid inputs return 400 Bad Request with specific error messages
- Validation occurs before database operations
- Validation errors are logged

#### Scenario: Valid user registration
- **GIVEN** registration form is submitted
- **WHEN** all fields pass UserSchema validation
- **THEN** user is created successfully

#### Scenario: Invalid email format
- **GIVEN** registration form with email "notanemail"
- **WHEN** UserSchema validation runs
- **THEN** validation fails with "Invalid email format"
- **AND** HTTP 400 is returned

#### Scenario: Invalid phone format
- **GIVEN** reservation form with phone "123"
- **WHEN** ReservationSchema validation runs
- **THEN** validation fails with "Phone must be in format 05XX XXX XX XX"
- **AND** HTTP 400 is returned

#### Scenario: Missing required fields
- **GIVEN** event form with missing name
- **WHEN** EventSchema validation runs
- **THEN** validation fails with "Name is required"
- **AND** HTTP 400 is returned

### Requirement: XSS Protection
The system SHALL sanitize all user-generated content before storage and display to prevent Cross-Site Scripting attacks.

**Sanitization Rules:**
- HTML tags stripped from text inputs (except safe tags in rich text)
- JavaScript code removed
- Event handlers removed
- Dangerous attributes removed
- Templates use auto-escape by default

#### Scenario: Script tag in user input
- **GIVEN** user submits note "<script>alert('xss')</script>Hello"
- **WHEN** content is sanitized
- **THEN** stored as "Hello"
- **AND** script is completely removed

#### Scenario: Event handler in input
- **GIVEN** user submits name "<img src=x onerror='alert(1)'>John"
- **WHEN** content is sanitized
- **THEN** stored as "John"
- **AND** dangerous attributes removed

#### Scenario: Safe HTML preserved in rich text
- **GIVEN** admin submits description "<p><b>Important</b> event</p>"
- **WHEN** content is sanitized with allow_html=True
- **THEN** stored as "<p><b>Important</b> event</p>"
- **AND** safe tags preserved

#### Scenario: Template auto-escape
- **GIVEN** template renders user-generated content
- **WHEN** content contains "<script>alert('xss')</script>"
- **THEN** rendered as escaped HTML entities
- **AND** browser displays as text, not executes

### Requirement: Phone Number Validation
The system SHALL validate Turkish phone numbers in the format 05XX XXX XX XX.

**Validation Rules:**
- Must start with "05"
- Total 11 digits (05XXXXXXXXX)
- Accept formats: "05XXXXXXXXX", "05XX XXX XX XX", "05XX-XXX-XX-XX"
- Normalize to "05XXXXXXXXX" format in database

#### Scenario: Valid phone number - no spaces
- **GIVEN** phone input "05551234567"
- **WHEN** validation runs
- **THEN** accepted and stored as "05551234567"

#### Scenario: Valid phone number - with spaces
- **GIVEN** phone input "0555 123 45 67"
- **WHEN** validation runs
- **THEN** accepted and normalized to "05551234567"

#### Scenario: Valid phone number - with dashes
- **GIVEN** phone input "0555-123-45-67"
- **WHEN** validation runs
- **THEN** accepted and normalized to "05551234567"

#### Scenario: Invalid phone number - wrong prefix
- **GIVEN** phone input "03551234567"
- **WHEN** validation runs
- **THEN** validation fails with "Phone must start with 05"

#### Scenario: Invalid phone number - wrong length
- **GIVEN** phone input "055123456"
- **WHEN** validation runs
- **THEN** validation fails with "Phone must be 11 digits"

### Requirement: Email Validation
The system SHALL validate email addresses according to RFC 5322 standard.

#### Scenario: Valid email
- **GIVEN** email input "user@example.com"
- **WHEN** validation runs
- **THEN** email is accepted

#### Scenario: Invalid email - no @
- **GIVEN** email input "userexample.com"
- **WHEN** validation runs
- **THEN** validation fails with "Invalid email format"

#### Scenario: Invalid email - no domain
- **GIVEN** email input "user@"
- **WHEN** validation runs
- **THEN** validation fails with "Invalid email format"

### Requirement: SQL Injection Prevention
The system SHALL prevent SQL injection attacks by using parameterized queries exclusively through SQLAlchemy ORM.

**Prevention Measures:**
- No raw SQL queries allowed
- All database access through SQLAlchemy ORM
- All user inputs passed as parameters
- Static code analysis to detect raw SQL

#### Scenario: Safe parameterized query
- **GIVEN** user searches by phone "0555'; DROP TABLE users; --"
- **WHEN** query is executed via ORM
- **THEN** search treats input as literal string
- **AND** no SQL injection occurs
- **AND** no tables are dropped

#### Scenario: Reject raw SQL in code review
- **GIVEN** code contains `db.execute("SELECT * FROM users WHERE phone = '" + phone + "'")`
- **WHEN** static analysis runs
- **THEN** violation is flagged
- **AND** code review fails
