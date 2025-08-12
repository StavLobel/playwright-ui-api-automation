"""
Test module for inventory list count verification.

This module contains tests for verifying that the SauceDemo inventory page
displays the correct number of products after successful user login.

Test Case: TC-UI-001
Objective: Verify that exactly 6 items are displayed in the inventory after login
"""

import allure
import pytest
from playwright.sync_api import Page

from src.core.assertions import get_assertion_helper
from src.core.types import TestContext
from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
@allure.epic("UI Testing")
@allure.feature("Inventory Management")
@allure.story("Inventory Item Count")
@allure.title("Verify inventory displays exactly 6 items after login")
@allure.description(
    """
This test verifies that the SauceDemo inventory page correctly displays
exactly 6 products after a successful user login. This is a critical
validation of the core inventory display functionality.

Steps:
1. Navigate to SauceDemo login page
2. Login with standard user credentials
3. Wait for inventory page to load
4. Count the number of inventory items displayed
5. Verify exactly 6 items are present

Expected Result:
- Login is successful and redirects to inventory page
- Inventory page displays exactly 6 product items
- All items have proper product information
"""
)
@allure.testcase("TC-UI-001", "Inventory List Count Verification")
def test_inventory_displays_exactly_six_items(
    page: Page,
    test_context: TestContext,
    standard_user_credentials: dict,
    allure_reporter,
) -> None:
    """
    Verify that exactly 6 items are displayed in the inventory after login.

    This test validates the core inventory display functionality by logging in
    with standard user credentials and counting the number of products shown.

    Args:
        page: Playwright page instance
        test_context: Test execution context with correlation ID
        standard_user_credentials: User credentials for login
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If inventory count is not exactly 6
    """
    assertions = get_assertion_helper(
        test_context.logger if hasattr(test_context, "logger") else None
    )

    with allure.step("Initialize page objects"):
        login_page = LoginPage(page, test_context)
        inventory_page = InventoryPage(page, test_context)

    with allure.step("Navigate to SauceDemo login page"):
        login_page.navigate_to_login()
        login_page.verify_login_page_loaded()

    with allure.step(
        f"Login with standard user: {standard_user_credentials['username']}"
    ):
        login_page.login(
            username=standard_user_credentials["username"],
            password=standard_user_credentials["password"],
        )

    with allure.step("Verify inventory page is loaded"):
        inventory_page.verify_page_loaded()

        # Take screenshot of loaded inventory page
        allure_reporter.attach_screenshot(page, "Inventory Page Loaded")

    with allure.step("Count inventory items"):
        item_count = inventory_page.get_inventory_count()

        # Attach inventory count to report
        allure_reporter.attach_json(
            {"inventory_count": item_count, "expected_count": 6},
            "Inventory Count Details",
        )

    with allure.step("Verify exactly 6 items are displayed"):
        assertions.assert_equals(
            actual=item_count,
            expected=6,
            message=f"Expected exactly 6 inventory items, but found {item_count} items",
        )

    # Get product names for additional validation
    with allure.step("Get product details for validation"):
        product_names = inventory_page.get_product_names()

        allure_reporter.attach_json(
            {"product_names": product_names}, "Product Names List"
        )

        # Verify that we have product names for all items
        assertions.assert_equals(
            actual=len(product_names),
            expected=6,
            message=f"Expected 6 product names, but got {len(product_names)}",
        )

        # Verify that all product names are non-empty
        empty_names = [name for name in product_names if not name.strip()]
        if empty_names:
            raise AssertionError(f"Found {len(empty_names)} products with empty names")


@pytest.mark.ui
@pytest.mark.regression
@allure.epic("UI Testing")
@allure.feature("Inventory Management")
@allure.story("Inventory Item Validation")
@allure.title("Verify inventory items have complete information")
@allure.description(
    """
This test verifies that all inventory items display complete information
including name, description, price, and image after login.

This is an extended validation that ensures data quality beyond just count.
"""
)
def test_inventory_items_have_complete_information(
    page: Page,
    test_context: TestContext,
    logged_in_user,  # This fixture handles login
    allure_reporter,
) -> None:
    """
    Verify that all inventory items have complete information displayed.

    This test validates that each inventory item has all required fields
    populated (name, description, price) and that the data is meaningful.

    Args:
        page: Playwright page instance
        test_context: Test execution context
        logged_in_user: Fixture that ensures user is logged in
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize inventory page"):
        inventory_page = InventoryPage(page, test_context)
        inventory_page.verify_page_loaded()

    with allure.step("Get inventory count"):
        item_count = inventory_page.get_inventory_count()
        assertions.assert_greater_than(
            actual=item_count,
            threshold=0,
            message="Inventory should contain at least one item",
        )

    with allure.step("Validate each inventory item has complete information"):
        incomplete_items = []

        for i in range(item_count):
            product_details = inventory_page.get_product_details(i)

            # Check for required fields
            if not product_details.get("name", "").strip():
                incomplete_items.append(f"Item {i}: missing name")

            if not product_details.get("description", "").strip():
                incomplete_items.append(f"Item {i}: missing description")

            if not product_details.get("price", "").strip():
                incomplete_items.append(f"Item {i}: missing price")

            # Validate price format (should start with $)
            price = product_details.get("price", "")
            if price and not price.startswith("$"):
                incomplete_items.append(f"Item {i}: invalid price format '{price}'")

        # Attach validation results
        allure_reporter.attach_json(
            {
                "total_items_checked": item_count,
                "incomplete_items_count": len(incomplete_items),
                "incomplete_items": incomplete_items,
            },
            "Item Validation Results",
        )

        # Assert that all items are complete
        if incomplete_items:
            error_msg = (
                f"Found {len(incomplete_items)} items with incomplete information:\n"
            )
            error_msg += "\n".join(incomplete_items)
            raise AssertionError(error_msg)
