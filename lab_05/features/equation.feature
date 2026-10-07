Feature: Real roots of a biquadratic equation
  Scenario: Four distinct real roots
    Given coefficients 1, -5, 4
    When I solve the equation
    Then the roots are -2, -1, 1, 2

  Scenario: No real roots
    Given coefficients 1, 0, 1
    When I solve the equation
    Then there are no real roots

  Scenario: Every real number is a solution
    Given coefficients 0, 0, 0
    When I solve the equation
    Then every real number is a solution
