Feature: Notification factory method
  Scenario: Email notification
    Given an email service
    When I notify the student
    Then the notification starts with EMAIL

  Scenario: SMS notification
    Given an sms service
    When I notify the student
    Then the notification starts with SMS

  Scenario: Empty notification is rejected
    Given an email service
    When I submit an empty message
    Then no notification is written
