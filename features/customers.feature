Feature: The customer service back-end
    As a customer liaison
    I need a RESTful catalog service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | first_name | last_name | address    | email        | password   | status |
        | fido       | dog       | California | MALE@aol.com | secret123  | active |
        | kitty      | cat       | Pakistan   | FE@MALE.com  | meow456    | deleted |
        | leo        | lion      | New York   | MAL@E.com    | roar789    | suspended |
        | sammy      | snake     | Antarctica | UNKNO@WN.com | hiss000    | active |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Happy"
    And I set the "Last Name" to "Hippo"
    And I set the "address" to "Empire State Building"
    And I set the "email" to "test@devopsrules.com"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "First Name" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Happy" in the "First Name" field
    And I should see "Hippo" in the "Last Name" field
    And I should see "Empire State Building" in the "address" field
    And I should see "test@devopsrules.com" in the "email" field

Scenario: List all customers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should see "leo" in the results

Scenario: Search for first name
    When I visit the "Home Page"
    And I set the "First Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should not see "kitty" in the results
    And I should not see "leo" in the results

# Scenario: Search for dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for available
#     When I visit the "Home Page"
#     And I select "True" in the "Available" dropdown
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "sammy" in the results
#     And I should not see "leo" in the results

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the "First Name" field
    And I should see "dog" in the "Last Name" field
    When I change "First Name" to "Loki"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Loki" in the "First Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Loki" in the results
    And I should not see "fido" in the results


Scenario: Delete a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the "First Name" field
    And I should see "dog" in the "Last Name" field
    When I press the "Delete" button
    Then I should see the message "Customer has been Deleted!"
    When I press the "Search" button
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "kitty" in the results
    And I should not see "fido" in the results