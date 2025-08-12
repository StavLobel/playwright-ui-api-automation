"""
Test module for adding items to shopping cart.

This module contains tests for verifying cart functionality including
adding items to cart and verifying cart badge updates.

Test Case: TC-UI-002
Objective: Verify that adding the first inventory item to cart updates the cart badge to show "1"
"""

import allure
import pytest
from playwright.sync_api import Page

from src.core.assertions import get_assertion_helper
from src.core.types import TestContext
from src.pages.cart_page import CartPage
from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
@allure.epic("UI Testing")
@allure.feature("Shopping Cart")
@allure.story("Add to Cart Functionality")
@allure.title("Verify adding first item to cart updates badge to '1'")
@allure.description(
    """
This test verifies that adding the first inventory item to the shopping cart
correctly updates the cart badge to display "1", indicating one item in cart.

Steps:
1. Navigate to SauceDemo and complete login
2. Locate the first product item in the inventory
3. Click the "Add to cart" button for the first item
4. Verify button text changes to "Remove"
5. Check the shopping cart badge in the header
6. Verify cart badge displays "1"

Expected Result:
- First product is successfully added to cart
- "Add to cart" button changes to "Remove"
- Shopping cart badge appears with count "1"
- Cart icon is highlighted/updated to show active state
"""
)
@allure.testcase("TC-UI-002", "Add First Item to Cart")
def test_add_first_item_to_cart_updates_badge(
    page: Page,
    test_context: TestContext,
    standard_user_credentials: dict,
    allure_reporter,
) -> None:
    """
    Verify that adding the first inventory item to cart updates the cart badge to show "1".

    This test validates the core shopping cart functionality by adding an item
    and verifying that the UI correctly reflects the cart state.

    Args:
        page: Playwright page instance
        test_context: Test execution context with correlation ID
        standard_user_credentials: User credentials for login
        allure_reporter: Allure reporter for enhanced reporting

    Raises:
        AssertionError: If cart badge is not updated correctly
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize page objects"):
        login_page = LoginPage(page, test_context)
        inventory_page = InventoryPage(page, test_context)

    with allure.step("Navigate to SauceDemo and complete login"):
        login_page.navigate_to_login()
        login_page.login(
            username=standard_user_credentials["username"],
            password=standard_user_credentials["password"],
        )

    with allure.step("Verify inventory page is loaded"):
        inventory_page.verify_page_loaded()

        # Take screenshot of initial state
        allure_reporter.attach_screenshot(page, "Inventory Page - Initial State")

    with allure.step("Verify cart is initially empty"):
        initial_cart_count = inventory_page.get_cart_badge_count()
        assertions.assert_equals(
            actual=initial_cart_count,
            expected="",
            message="Cart should be empty initially (no badge visible)",
        )

    with allure.step("Add first inventory item to cart"):
        product_name = inventory_page.add_first_item_to_cart()

        # Attach product information
        allure_reporter.attach_json(
            {"added_product": product_name}, "Product Added to Cart"
        )

        # Take screenshot after adding item
        allure_reporter.attach_screenshot(page, "After Adding Item to Cart")

    with allure.step("Verify cart badge shows '1'"):
        cart_badge_count = inventory_page.get_cart_badge_count()

        assertions.assert_equals(
            actual=cart_badge_count,
            expected="1",
            message=f"Expected cart badge to show '1' after adding item, but got '{cart_badge_count}'",
        )

        # Attach cart state information
        allure_reporter.attach_json(
            {
                "cart_badge_count": cart_badge_count,
                "expected_count": "1",
                "product_added": product_name,
            },
            "Cart Badge Verification",
        )

    with allure.step("Verify 'Add to cart' button changed to 'Remove'"):
        # Get the first inventory item and check button state
        first_item = page.locator(inventory_page.INVENTORY_ITEMS).first
        remove_button = first_item.locator(inventory_page.REMOVE_BUTTON)

        # Verify remove button is now visible
        try:
            page.wait_for_selector(
                f"{inventory_page.INVENTORY_ITEMS}:first-child {inventory_page.REMOVE_BUTTON}",
                state="visible",
                timeout=5000,
            )
        except Exception:
            raise AssertionError(
                "'Add to cart' button did not change to 'Remove' button"
            )


@pytest.mark.ui
@pytest.mark.regression
@allure.epic("UI Testing")
@allure.feature("Shopping Cart")
@allure.story("Cart Navigation")
@allure.title("Verify added item appears in cart page")
@allure.description(
    """
This test verifies that after adding an item to cart, the item correctly
appears in the cart page when navigating to the cart.
"""
)
def test_added_item_appears_in_cart_page(
    page: Page,
    test_context: TestContext,
    logged_in_user,  # This fixture handles login
    allure_reporter,
) -> None:
    """
    Verify that an item added to cart appears correctly in the cart page.

    This test validates the complete add-to-cart workflow by adding an item
    and then navigating to the cart page to verify the item is listed.

    Args:
        page: Playwright page instance
        test_context: Test execution context
        logged_in_user: Fixture that ensures user is logged in
        allure_reporter: Allure reporter for enhanced reporting
    """
    assertions = get_assertion_helper()

    with allure.step("Initialize page objects"):
        inventory_page = InventoryPage(page, test_context)
        cart_page = CartPage(page, test_context)

    with allure.step("Verify inventory page is loaded"):
        inventory_page.verify_page_loaded()

    with allure.step("Add first item to cart"):
        product_name = inventory_page.add_first_item_to_cart()

        allure_reporter.attach_json({"product_added": product_name}, "Product Added")

    with allure.step("Navigate to cart page"):
        inventory_page.click_shopping_cart()
        cart_page.verify_page_loaded()

        # Take screenshot of cart page
        allure_reporter.attach_screenshot(page, "Cart Page with Added Item")

    with allure.step("Verify cart contains the added item"):
        cart_items = cart_page.get_cart_item_names()

        assertions.assert_list_contains(
            items=cart_items,
            item=product_name,
            message=f"Expected cart to contain '{product_name}', but cart items are: {cart_items}",
        )

        # Verify cart has exactly one item
        cart_count = cart_page.get_cart_items_count()
        assertions.assert_equals(
            actual=cart_count,
            expected=1,
            message=f"Expected cart to have 1 item, but found {cart_count} items",
        )

        # Get and attach detailed cart information
        cart_details = cart_page.get_cart_item_details()
        allure_reporter.attach_json(
            {
                "cart_items_count": cart_count,
                "cart_items": cart_items,
                "cart_details": cart_details,
            },
            "Cart Verification Details",
        )


@pytest.mark.ui
@pytest.mark.regression
@allure.epic("UI Testing")
@allure.feature("Shopping Cart")
@allure.story("Multiple Items")
@allure.title("Verify cart badge updates when adding multiple items")
@allure.description(
    """
This test verifies that the cart badge correctly updates when adding
multiple items to the cart, showing the accurate count.
"""
)
def test_cart_badge_updates_with_multiple_items(
    page: Page, test_context: TestContext, logged_in_user, allure_reporter
) -> None:
    """
    Verify that cart badge correctly updates when adding multiple items.

    This test validates that the cart badge count accurately reflects
    the number of items when multiple products are added to the cart.

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

    with allure.step("Verify cart is initially empty"):
        initial_count = inventory_page.get_cart_badge_count()
        assertions.assert_equals(initial_count, "", "Cart should be empty initially")

    with allure.step("Add first item to cart"):
        first_product = inventory_page.add_first_item_to_cart()

        # Verify badge shows "1"
        inventory_page.verify_cart_badge_count("1")

        allure_reporter.attach_screenshot(page, "After Adding First Item")

    with allure.step("Add second item to cart"):
        # Get product names to find a different product
        product_names = inventory_page.get_product_names()

        # Find a product different from the first one
        second_product = None
        for name in product_names:
            if name != first_product:
                second_product = name
                break

        if second_product:
            inventory_page.add_product_to_cart_by_name(second_product)

            # Verify badge shows "2"
            inventory_page.verify_cart_badge_count("2")

            allure_reporter.attach_screenshot(page, "After Adding Second Item")

            # Attach test results
            allure_reporter.attach_json(
                {
                    "first_product": first_product,
                    "second_product": second_product,
                    "final_cart_count": "2",
                },
                "Multiple Items Test Results",
            )
        else:
            pytest.skip("Could not find a second product to add to cart")
