"""
Test module for adding first item to cart functionality.

This module contains tests for verifying that users can successfully add
the first inventory item to their shopping cart.

Test Case: TC-UI-002
Objective: Verify that the first inventory item can be added to cart and badge updates
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
@allure.feature("Shopping Cart")
@allure.story("Add Item to Cart")
@allure.title("Verify first inventory item can be added to cart")
@allure.description(
    """
This test verifies that users can successfully add the first inventory
item to their shopping cart and that the cart badge updates accordingly.

Steps:
1. Navigate to SauceDemo login page
2. Login with standard user credentials
3. Wait for inventory page to load
4. Add the first inventory item to cart
5. Verify cart badge shows count of 1
6. Verify item appears in cart

Expected Result:
- Login is successful and redirects to inventory page
- First item can be added to cart successfully
- Cart badge displays count of 1
- Item is properly added to cart
"""
)
@allure.testcase("TC-UI-002", "Add First Item to Cart")
def test_add_first_item_to_cart(
    page: Page,
    test_context: TestContext,
    standard_user_credentials: dict,
    allure_reporter,
) -> None:
    """
    Verify that the first inventory item can be added to cart successfully.

    This test validates the core shopping cart functionality by ensuring
    users can add items and the cart state updates correctly.

    Args:
        page: Playwright page instance
        test_context: Test execution context with correlation ID
        standard_user_credentials: User credentials for login
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If item cannot be added to cart or badge doesn't update
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

    with allure.step("Verify cart badge shows 0 items initially"):
        initial_cart_count = inventory_page.get_cart_item_count()
        assertions.assert_equals(
            actual=initial_cart_count,
            expected=0,
            message=f"Expected cart to start with 0 items, but found {initial_cart_count}",
        )

    with allure.step("Add first inventory item to cart"):
        # Get first item details before adding
        first_item_name = inventory_page.get_product_name(0)
        first_item_price = inventory_page.get_product_price(0)

        allure_reporter.attach_json(
            {
                "first_item_name": first_item_name,
                "first_item_price": first_item_price,
                "action": "adding_to_cart",
            },
            "First Item Details",
        )

        # Add first item to cart
        inventory_page.add_item_to_cart(0)

        # Take screenshot after adding item
        allure_reporter.attach_screenshot(page, "Item Added to Cart")

    with allure.step("Verify cart badge shows 1 item"):
        updated_cart_count = inventory_page.get_cart_item_count()
        assertions.assert_equals(
            actual=updated_cart_count,
            expected=1,
            message=f"Expected cart to show 1 item after adding, but found {updated_cart_count}",
        )

        allure_reporter.attach_json(
            {
                "cart_count_before": initial_cart_count,
                "cart_count_after": updated_cart_count,
                "expected_change": 1,
            },
            "Cart Count Change",
        )

    with allure.step("Verify add to cart button changed to remove"):
        button_text = inventory_page.get_add_to_cart_button_text(0)
        assertions.assert_equals(
            actual=button_text,
            expected="Remove",
            message=f"Expected button text to change to 'Remove', but found '{button_text}'",
        )

    with allure.step("Verify cart icon is visible and accessible"):
        cart_icon = inventory_page.get_cart_icon()
        assertions.assert_true(
            actual=cart_icon.is_visible(),
            message="Cart icon should be visible after adding item",
        )

        # Take final screenshot showing updated cart state
        allure_reporter.attach_screenshot(page, "Cart Updated Successfully")
