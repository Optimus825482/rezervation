# Check-in and QR Scanning Specification

## ADDED Requirements

### Requirement: QR Code Scanner
The system SHALL provide a web-based QR code scanner for check-in operations.

#### Scenario: Successful QR scan
- **GIVEN** kontrolör has camera access
- **WHEN** valid reservation QR code is scanned
- **THEN** reservation details are displayed
- **AND** check-in confirmation button is shown

#### Scenario: Invalid QR code
- **GIVEN** QR code does not match reservation format
- **WHEN** code is scanned
- **THEN** error message "Invalid QR code" is shown
- **AND** scanner continues to run

#### Scenario: Already checked-in
- **GIVEN** reservation was already checked in
- **WHEN** QR code is scanned again
- **THEN** warning "Already checked in at [timestamp]" is shown
- **AND** reservation details are displayed

### Requirement: Manual Search Fallback
The system SHALL provide manual search when QR scanning is not available.

#### Scenario: Search by phone
- **GIVEN** camera is not available
- **WHEN** kontrolör enters phone "05551234567"
- **THEN** matching reservations are displayed
- **AND** kontrolör can select correct reservation
