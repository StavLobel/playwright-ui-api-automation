"""
Inventory page object for SauceDemo application.

This module implements the Page Object Model for the SauceDemo inventory page,
providing methods for product browsing, cart operations, and inventory management.
"""

from typing import List

import allure
from playwright.sync_api import Page, expect

from src.core.base_page import BasePage
from src.core.types import TestContext


class InventoryPage(BasePage):
    """
    Page object for SauceDemo inventory/products page.

    This page handles all interactions with the main product listing including
    counting items, adding to cart, filtering, sorting, and product details.
    """

    # Main inventory elements
    INVENTORY_CONTAINER = "[data-test='inventory-container']"
    INVENTORY_LIST = ".inventory_list"
    INVENTORY_ITEMS = ".inventory_item"

    # Product item elements
    INVENTORY_ITEM_NAME = ".inventory_item_name"
    INVENTORY_ITEM_DESC = ".inventory_item_desc"
    INVENTORY_ITEM_PRICE = ".inventory_item_price"
    INVENTORY_ITEM_IMG = ".inventory_item_img"

    # Cart and action buttons
    ADD_TO_CART_BUTTON = "[data-test^='add-to-cart']"
    REMOVE_BUTTON = "[data-test^='remove']"
    SHOPPING_CART_LINK = ".shopping_cart_link"
    SHOPPING_CART_BADGE = ".shopping_cart_badge"

    # Header and navigation
    APP_LOGO = ".app_logo"
    MENU_BUTTON = "#react-burger-menu-btn"

    # Sorting and filtering
    PRODUCT_SORT_CONTAINER = ".product_sort_container"

    def __init__(self, page: Page, context: TestContext) -> None:
        """
        Initialize the inventory page.

        Args:
            page: Playwright page instance
            context: Test execution context
        """
        super().__init__(page, context)

    @property
    def url_pattern(self) -> str:
        """URL pattern that identifies this page."""
        return "/inventory.html"

    @property
    def page_title(self) -> str:
        """Expected page title for this page."""
        return "Swag Labs"

    @allure.step("Verify inventory page loaded")
    def verify_page_loaded(self) -> None:
        """
        Verify that the inventory page is properly loaded.

        This method checks that all essential inventory page elements are visible
        and the page is ready for interaction.

        Raises:
            AssertionError: If required elements are not found
        """
        self.logger.info("Verifying inventory page is loaded")

        try:
            # Verify URL pattern
            import re

            expect(self.page).to_have_url(
                re.compile(rf".*{re.escape(self.url_pattern)}$")
            )

            # Verify essential elements are visible
            expect(self.page.locator(self.APP_LOGO)).to_be_visible()
            expect(self.page.locator(self.INVENTORY_CONTAINER)).to_be_visible()
            expect(self.page.locator(self.INVENTORY_LIST)).to_be_visible()
            expect(self.page.locator(self.SHOPPING_CART_LINK)).to_be_visible()

            # Verify page title
            expect(self.page).to_have_title(self.page_title)

            # Wait for inventory items to load
            self.wait_for_element(self.INVENTORY_ITEMS, state="visible")

            self.logger.info("Inventory page verification successful")

        except Exception as e:
            self.logger.error(f"Inventory page verification failed: {str(e)}")
            self._take_screenshot("inventory_page_verification_failed")
            raise

    @allure.step("Get inventory count")
    def get_inventory_count(self) -> int:
        """
        Get the total number of inventory items displayed on the page.

        This method counts all visible inventory items and returns the count.
        It includes validation to ensure items are properly loaded.

        Returns:
            int: Number of inventory items displayed

        Raises:
            TimeoutError: If inventory items don't load within timeout
        """
        self.logger.debug("Counting inventory items")

        try:
            # Wait for inventory items to be visible
            self.wait_for_element(self.INVENTORY_ITEMS, state="visible")

            # Get count of inventory items
            count = self.get_elements_count(self.INVENTORY_ITEMS)

            self.logger.info(f"Found {count} inventory items")

            # Validate that we have a reasonable number of items
            if count == 0:
                self.logger.warning(
                    "No inventory items found - this may indicate a loading issue"
                )
                self._take_screenshot("no_inventory_items")

            return count

        except Exception as e:
            self.logger.error(f"Failed to count inventory items: {str(e)}")
            self._take_screenshot("inventory_count_failed")
            raise

    @allure.step("Get product names")
    def get_product_names(self) -> List[str]:
        """
        Get a list of all product names displayed on the inventory page.

        Returns:
            List[str]: List of product names
        """
        self.logger.debug("Getting product names")

        try:
            # Wait for inventory items to load
            self.wait_for_element(self.INVENTORY_ITEMS, state="visible")

            # Get all product name elements
            name_elements = self.page.locator(self.INVENTORY_ITEM_NAME).all()
            product_names = [element.text_content() or "" for element in name_elements]

            self.logger.debug(f"Found product names: {product_names}")
            return product_names

        except Exception as e:
            self.logger.error(f"Failed to get product names: {str(e)}")
            return []

    @allure.step("Add first item to cart")
    def add_first_item_to_cart(self) -> str:
        """
        Add the first inventory item to the shopping cart.

        This method finds the first inventory item, gets its name for logging,
        and clicks the "Add to cart" button. It includes validation that the
        button state changes correctly.

        Returns:
            str: Name of the product that was added to cart

        Raises:
            TimeoutError: If add to cart button is not found
            AssertionError: If button state doesn't change as expected
        """
        self.logger.info("Adding first inventory item to cart")

        try:
            # Wait for inventory items to be visible
            self.wait_for_element(self.INVENTORY_ITEMS, state="visible")

            # Get the first product name for logging
            first_item = self.page.locator(self.INVENTORY_ITEMS).first
            product_name = (
                first_item.locator(self.INVENTORY_ITEM_NAME).text_content() or "Unknown"
            )

            self.logger.debug(f"Adding product to cart: {product_name}")

            # Find and click the first "Add to cart" button
            first_add_button = first_item.locator(self.ADD_TO_CART_BUTTON).first

            # Verify button is visible and enabled
            expect(first_add_button).to_be_visible()
            expect(first_add_button).to_be_enabled()

            # Click the add to cart button
            first_add_button.click()

            # Wait briefly for the button state to change
            self.page.wait_for_timeout(1000)

            # Verify button text changed to "Remove" (indicating successful add)
            remove_button = first_item.locator(self.REMOVE_BUTTON).first
            expect(remove_button).to_be_visible(timeout=5000)

            self.logger.info(f"Successfully added '{product_name}' to cart")
            return product_name

        except Exception as e:
            self.logger.error(f"Failed to add first item to cart: {str(e)}")
            self._take_screenshot("add_to_cart_failed")
            raise

    @allure.step("Add product to cart by name: {product_name}")
    def add_product_to_cart_by_name(self, product_name: str) -> None:
        """
        Add a specific product to cart by its name.

        Args:
            product_name: Name of the product to add to cart

        Raises:
            ValueError: If product with given name is not found
        """
        self.logger.info(f"Adding product to cart by name: {product_name}")

        try:
            # Find the product by name
            product_locator = self.page.locator(self.INVENTORY_ITEMS).filter(
                has_text=product_name
            )

            if product_locator.count() == 0:
                available_products = self.get_product_names()
                raise ValueError(
                    f"Product '{product_name}' not found. "
                    f"Available products: {available_products}"
                )

            # Click the add to cart button for this product
            add_button = product_locator.locator(self.ADD_TO_CART_BUTTON)
            add_button.click()

            # Wait for button state change
            self.page.wait_for_timeout(1000)

            self.logger.info(f"Successfully added '{product_name}' to cart")

        except Exception as e:
            self.logger.error(
                f"Failed to add product '{product_name}' to cart: {str(e)}"
            )
            self._take_screenshot("add_product_by_name_failed")
            raise

    @allure.step("Get cart badge count")
    def get_cart_badge_count(self) -> str:
        """
        Get the shopping cart badge count as displayed on the page.

        This method retrieves the number displayed on the shopping cart badge,
        which indicates how many items are currently in the cart.

        Returns:
            str: Cart badge count as string (e.g., "1", "2", etc.),
                 empty string if no badge is visible
        """
        self.logger.debug("Getting cart badge count")

        try:
            if self.is_element_visible(self.SHOPPING_CART_BADGE, timeout=3000):
                badge_text = self.get_text(self.SHOPPING_CART_BADGE)
                self.logger.debug(f"Cart badge count: {badge_text}")
                return badge_text
            else:
                self.logger.debug("Cart badge not visible (likely empty cart)")
                return ""

        except Exception as e:
            self.logger.warning(f"Failed to get cart badge count: {str(e)}")
            return ""

    @allure.step("Verify cart badge count: {expected_count}")
    def verify_cart_badge_count(self, expected_count: str) -> None:
        """
        Verify that the cart badge shows the expected count.

        Args:
            expected_count: Expected count as string (e.g., "1", "2")

        Raises:
            AssertionError: If cart badge count doesn't match expected
        """
        self.logger.info(f"Verifying cart badge count: {expected_count}")

        try:
            if expected_count == "" or expected_count == "0":
                # Expect no badge to be visible for empty cart
                badge_visible = self.is_element_visible(
                    self.SHOPPING_CART_BADGE, timeout=3000
                )
                if badge_visible:
                    actual_count = self.get_text(self.SHOPPING_CART_BADGE)
                    raise AssertionError(
                        f"Expected empty cart (no badge), but found badge with count: {actual_count}"
                    )
                self.logger.info(
                    "Cart badge verification successful - no badge visible as expected"
                )
            else:
                # Expect specific count
                self.wait_for_element(
                    self.SHOPPING_CART_BADGE, state="visible", timeout=5000
                )
                actual_count = self.get_text(self.SHOPPING_CART_BADGE)

                if actual_count != expected_count:
                    error_msg = (
                        f"Cart badge count mismatch.\n"
                        f"Expected: {expected_count}\n"
                        f"Actual: {actual_count}"
                    )
                    self.logger.error(error_msg)
                    raise AssertionError(error_msg)

                self.logger.info(
                    f"Cart badge verification successful - count: {actual_count}"
                )

        except Exception as e:
            self.logger.error(f"Cart badge verification failed: {str(e)}")
            self._take_screenshot("cart_badge_verification_failed")
            raise

    @allure.step("Click shopping cart")
    def click_shopping_cart(self) -> None:
        """
        Click the shopping cart link to navigate to the cart page.

        This method clicks the shopping cart icon in the header to navigate
        to the cart page for checkout.
        """
        self.logger.info("Clicking shopping cart link")

        try:
            self.click_element(self.SHOPPING_CART_LINK)

            # Wait for navigation to cart page
            self.page.wait_for_url("**/cart.html", timeout=5000)

            self.logger.info("Successfully navigated to cart page")

        except Exception as e:
            self.logger.error(f"Failed to navigate to cart: {str(e)}")
            self._take_screenshot("cart_navigation_failed")
            raise

    @allure.step("Get product details")
    def get_product_details(self, product_index: int = 0) -> dict:
        """
        Get detailed information about a specific product.

        Args:
            product_index: Index of the product (0-based)

        Returns:
            dict: Product details including name, description, price
        """
        self.logger.debug(f"Getting details for product at index {product_index}")

        try:
            # Get the specific product item
            products = self.page.locator(self.INVENTORY_ITEMS)

            if product_index >= products.count():
                raise IndexError(f"Product index {product_index} out of range")

            product = products.nth(product_index)

            # Extract product details
            name = product.locator(self.INVENTORY_ITEM_NAME).text_content() or ""
            description = product.locator(self.INVENTORY_ITEM_DESC).text_content() or ""
            price = product.locator(self.INVENTORY_ITEM_PRICE).text_content() or ""

            details = {
                "name": name,
                "description": description,
                "price": price,
                "index": product_index,
            }

            self.logger.debug(f"Product details: {details}")
            return details

        except Exception as e:
            self.logger.error(f"Failed to get product details: {str(e)}")
            return {}
