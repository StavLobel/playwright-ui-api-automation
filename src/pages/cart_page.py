"""
Cart page object for SauceDemo application.

This module implements the Page Object Model for the SauceDemo shopping cart page,
providing methods for cart management, item removal, and checkout operations.
"""

from typing import Any, Dict, List

import allure
from playwright.sync_api import Page, expect

from src.core.base_page import BasePage
from src.core.types import TestContext


class CartPage(BasePage):
    """
    Page object for SauceDemo shopping cart page.

    This page handles all interactions with the shopping cart including
    viewing cart items, removing items, updating quantities, and proceeding to checkout.
    """

    # Main cart elements
    CART_CONTAINER = "#cart_contents_container"
    CART_LIST = ".cart_list"
    CART_ITEMS = ".cart_item"

    # Cart item elements
    CART_ITEM_NAME = ".inventory_item_name"
    CART_ITEM_DESC = ".inventory_item_desc"
    CART_ITEM_PRICE = ".inventory_item_price"
    CART_QUANTITY = ".cart_quantity"

    # Action buttons
    REMOVE_BUTTON = "[data-test^='remove']"
    CONTINUE_SHOPPING_BUTTON = "#continue-shopping"
    CHECKOUT_BUTTON = "#checkout"

    # Header elements
    CART_HEADER = ".header_secondary_container"
    CART_TITLE = ".title"

    # Navigation elements
    SHOPPING_CART_BADGE = ".shopping_cart_badge"

    def __init__(self, page: Page, context: TestContext) -> None:
        """
        Initialize the cart page.

        Args:
            page: Playwright page instance
            context: Test execution context
        """
        super().__init__(page, context)

    @property
    def url_pattern(self) -> str:
        """URL pattern that identifies this page."""
        return "/cart.html"

    @property
    def page_title(self) -> str:
        """Expected page title for this page."""
        return "Swag Labs"

    @allure.step("Verify cart page loaded")
    def verify_page_loaded(self) -> None:
        """
        Verify that the cart page is properly loaded.

        This method checks that all essential cart page elements are visible
        and the page is ready for interaction.

        Raises:
            AssertionError: If required elements are not found
        """
        self.logger.info("Verifying cart page is loaded")

        try:
            # Verify URL pattern
            import re

            expect(self.page).to_have_url(
                re.compile(rf".*{re.escape(self.url_pattern)}$")
            )

            # Verify essential elements are visible
            expect(self.page.locator(self.CART_CONTAINER)).to_be_visible()
            expect(self.page.locator(self.CART_TITLE)).to_be_visible()
            expect(self.page.locator(self.CONTINUE_SHOPPING_BUTTON)).to_be_visible()
            expect(self.page.locator(self.CHECKOUT_BUTTON)).to_be_visible()

            # Verify page title
            expect(self.page).to_have_title(self.page_title)

            # Verify cart title text
            expect(self.page.locator(self.CART_TITLE)).to_have_text("Your Cart")

            self.logger.info("Cart page verification successful")

        except Exception as e:
            self.logger.error(f"Cart page verification failed: {str(e)}")
            self._take_screenshot("cart_page_verification_failed")
            raise

    @allure.step("Get cart items count")
    def get_cart_items_count(self) -> int:
        """
        Get the number of items currently in the cart.

        Returns:
            int: Number of items in the cart
        """
        self.logger.debug("Getting cart items count")

        try:
            # Check if cart has any items
            if self.is_element_visible(self.CART_ITEMS, timeout=3000):
                count = self.get_elements_count(self.CART_ITEMS)
                self.logger.info(f"Found {count} items in cart")
                return count
            else:
                self.logger.info("Cart is empty")
                return 0

        except Exception as e:
            self.logger.error(f"Failed to get cart items count: {str(e)}")
            return 0

    @allure.step("Get cart item names")
    def get_cart_item_names(self) -> List[str]:
        """
        Get a list of all product names in the cart.

        Returns:
            List[str]: List of product names in the cart
        """
        self.logger.debug("Getting cart item names")

        try:
            if self.get_cart_items_count() == 0:
                return []

            # Get all cart item name elements
            name_elements = self.page.locator(self.CART_ITEM_NAME).all()
            item_names = [element.text_content() or "" for element in name_elements]

            self.logger.debug(f"Cart item names: {item_names}")
            return item_names

        except Exception as e:
            self.logger.error(f"Failed to get cart item names: {str(e)}")
            return []

    @allure.step("Get cart item details")
    def get_cart_item_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about all items in the cart.

        Returns:
            List[Dict[str, Any]]: List of cart item details including name, price, quantity
        """
        self.logger.debug("Getting cart item details")

        try:
            items_count = self.get_cart_items_count()
            if items_count == 0:
                return []

            cart_items = []
            item_elements = self.page.locator(self.CART_ITEMS).all()

            for i, item_element in enumerate(item_elements):
                name = item_element.locator(self.CART_ITEM_NAME).text_content() or ""
                description = (
                    item_element.locator(self.CART_ITEM_DESC).text_content() or ""
                )
                price = item_element.locator(self.CART_ITEM_PRICE).text_content() or ""
                quantity = (
                    item_element.locator(self.CART_QUANTITY).text_content() or "1"
                )

                item_details = {
                    "index": i,
                    "name": name,
                    "description": description,
                    "price": price,
                    "quantity": quantity,
                }

                cart_items.append(item_details)

            self.logger.debug(f"Cart item details: {cart_items}")
            return cart_items

        except Exception as e:
            self.logger.error(f"Failed to get cart item details: {str(e)}")
            return []

    @allure.step("Remove item from cart: {item_name}")
    def remove_item_by_name(self, item_name: str) -> None:
        """
        Remove a specific item from the cart by its name.

        Args:
            item_name: Name of the item to remove

        Raises:
            ValueError: If item with given name is not found in cart
        """
        self.logger.info(f"Removing item from cart: {item_name}")

        try:
            # Find the cart item by name
            cart_item = self.page.locator(self.CART_ITEMS).filter(has_text=item_name)

            if cart_item.count() == 0:
                available_items = self.get_cart_item_names()
                raise ValueError(
                    f"Item '{item_name}' not found in cart. "
                    f"Available items: {available_items}"
                )

            # Click the remove button for this item
            remove_button = cart_item.locator(self.REMOVE_BUTTON)
            remove_button.click()

            # Wait for item to be removed
            self.page.wait_for_timeout(1000)

            self.logger.info(f"Successfully removed '{item_name}' from cart")

        except Exception as e:
            self.logger.error(
                f"Failed to remove item '{item_name}' from cart: {str(e)}"
            )
            self._take_screenshot("remove_item_failed")
            raise

    @allure.step("Remove first item from cart")
    def remove_first_item(self) -> str:
        """
        Remove the first item from the cart.

        Returns:
            str: Name of the item that was removed

        Raises:
            ValueError: If cart is empty
        """
        self.logger.info("Removing first item from cart")

        try:
            if self.get_cart_items_count() == 0:
                raise ValueError("Cannot remove item - cart is empty")

            # Get the name of the first item
            first_item = self.page.locator(self.CART_ITEMS).first
            item_name = (
                first_item.locator(self.CART_ITEM_NAME).text_content() or "Unknown"
            )

            # Click the remove button
            remove_button = first_item.locator(self.REMOVE_BUTTON)
            remove_button.click()

            # Wait for item to be removed
            self.page.wait_for_timeout(1000)

            self.logger.info(f"Successfully removed first item: {item_name}")
            return item_name

        except Exception as e:
            self.logger.error(f"Failed to remove first item from cart: {str(e)}")
            self._take_screenshot("remove_first_item_failed")
            raise

    @allure.step("Clear cart")
    def clear_cart(self) -> None:
        """
        Remove all items from the cart.

        This method removes all items one by one until the cart is empty.
        """
        self.logger.info("Clearing all items from cart")

        try:
            items_count = self.get_cart_items_count()
            self.logger.debug(f"Starting with {items_count} items in cart")

            while self.get_cart_items_count() > 0:
                self.remove_first_item()
                # Small delay to allow UI to update
                self.page.wait_for_timeout(500)

            self.logger.info("Successfully cleared all items from cart")

        except Exception as e:
            self.logger.error(f"Failed to clear cart: {str(e)}")
            self._take_screenshot("clear_cart_failed")
            raise

    @allure.step("Continue shopping")
    def continue_shopping(self) -> None:
        """
        Click the "Continue Shopping" button to return to the inventory page.
        """
        self.logger.info("Continuing shopping - returning to inventory page")

        try:
            self.click_element(self.CONTINUE_SHOPPING_BUTTON)

            # Wait for navigation to inventory page
            self.page.wait_for_url("**/inventory.html", timeout=5000)

            self.logger.info("Successfully returned to inventory page")

        except Exception as e:
            self.logger.error(f"Failed to continue shopping: {str(e)}")
            self._take_screenshot("continue_shopping_failed")
            raise

    @allure.step("Proceed to checkout")
    def proceed_to_checkout(self) -> None:
        """
        Click the "Checkout" button to proceed to the checkout process.

        Raises:
            ValueError: If cart is empty
        """
        self.logger.info("Proceeding to checkout")

        try:
            if self.get_cart_items_count() == 0:
                raise ValueError("Cannot proceed to checkout - cart is empty")

            self.click_element(self.CHECKOUT_BUTTON)

            # Wait for navigation to checkout page
            self.page.wait_for_url("**/checkout-step-one.html", timeout=5000)

            self.logger.info("Successfully proceeded to checkout")

        except Exception as e:
            self.logger.error(f"Failed to proceed to checkout: {str(e)}")
            self._take_screenshot("checkout_failed")
            raise

    @allure.step("Verify cart is empty")
    def verify_cart_is_empty(self) -> None:
        """
        Verify that the cart is empty (contains no items).

        Raises:
            AssertionError: If cart contains items
        """
        self.logger.info("Verifying cart is empty")

        try:
            items_count = self.get_cart_items_count()

            if items_count > 0:
                item_names = self.get_cart_item_names()
                error_msg = (
                    f"Expected empty cart, but found {items_count} items: {item_names}"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            # Verify no cart badge is visible
            badge_visible = self.is_element_visible(
                self.SHOPPING_CART_BADGE, timeout=2000
            )
            if badge_visible:
                badge_count = self.get_text(self.SHOPPING_CART_BADGE)
                raise AssertionError(
                    f"Expected no cart badge, but found badge with count: {badge_count}"
                )

            self.logger.info("Cart is empty as expected")

        except Exception as e:
            self.logger.error(f"Cart empty verification failed: {str(e)}")
            self._take_screenshot("cart_empty_verification_failed")
            raise

    @allure.step("Verify cart contains item: {item_name}")
    def verify_cart_contains_item(self, item_name: str) -> None:
        """
        Verify that the cart contains a specific item.

        Args:
            item_name: Name of the item to verify

        Raises:
            AssertionError: If item is not found in cart
        """
        self.logger.info(f"Verifying cart contains item: {item_name}")

        try:
            cart_items = self.get_cart_item_names()

            if item_name not in cart_items:
                error_msg = (
                    f"Item '{item_name}' not found in cart. "
                    f"Cart contains: {cart_items}"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            self.logger.info(f"Verified cart contains item: {item_name}")

        except Exception as e:
            self.logger.error(f"Cart item verification failed: {str(e)}")
            self._take_screenshot("cart_item_verification_failed")
            raise
