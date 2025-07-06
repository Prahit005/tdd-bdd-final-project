Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name       | description     | price   | available | category   |
        | Hat        | A red fedora    | 59.95   | True      | CLOTHS     |
        | Shoes      | Blue shoes      | 120.50  | False     | CLOTHS     |
        | Big Mac    | 1/4 lb burger   | 5.99    | True      | FOOD       |
        | Sheets     | Full bed sheets | 87.00   | True      | HOUSEWARES |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Catalog Administration" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hammer"
    And I set the "Description" to "Claw hammer"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "34.95"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hammer" in the "Name" field
    And I should see "Claw hammer" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "Tools" in the "Category" dropdown
    And I should see "34.95" in the "Price" field

Scenario: Read a Product
    When I set the "Name" to "Drill"
    And I set the "Description" to "Power drill"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "79.99"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Drill" in the "Name" field
    And I should see "Power drill" in the "Description" field

Scenario: Update a Product
    When I set the "Name" to "Screwdriver"
    And I set the "Description" to "Flat-head"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "15.00"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I change "Description" to "Phillips-head"
    When I press the "Update" button
    Then I should see the message "Success"
    And I should see "Phillips-head" in the "Description" field

Scenario: Delete a Product
    When I set the "Name" to "Wrench"
    And I set the "Description" to "Pipe wrench"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "23.50"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    When I paste the "Id" field
    And I press the "Delete" button
    Then the "Name" field should be empty

Scenario: Search Products by Name
    When I set the "Name" to "UniqueName"
    And I set the "Description" to "Special"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "99.99"
    And I press the "Create" button
    Then I should see the message "Success"
    When I set the "Name" to "UniqueName"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "UniqueName" in the "Name" field

Scenario: Search Products by Category
    When I set the "Name" to "Blender"
    And I set the "Description" to "Kitchen appliance"
    And I select "True" in the "Available" dropdown
    And I select "Housewares" in the "Category" dropdown
    And I set the "Price" to "45.00"
    And I press the "Create" button
    Then I should see the message "Success"
    When I select "Housewares" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Blender" in the "Name" field
