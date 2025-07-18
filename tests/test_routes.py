######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestProductService
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product, Category
from tests.factories import ProductFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def test_get_product(self):
        """It should Read a Product"""
        test_product = ProductFactory()
        payload = test_product.serialize()
        response = self.client.post(BASE_URL, json=payload)
        print("POST response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        response = self.client.get(f"{BASE_URL}/{new_product['id']}")
        print("GET response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(data["description"], test_product.description)

    def test_update_product(self):
        """It should Update an existing Product"""
        # Create a product first
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Grab the new product
        new_product = response.get_json()
        new_product["description"] = "Updated description"
        # Send PUT request
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Confirm it updated
        updated = response.get_json()
        self.assertEqual(updated["description"], "Updated description")

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_id = response.get_json()["id"]
        # Delete the product
        response = self.client.delete(f"{BASE_URL}/{product_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Try to get it again (should 404)
        response = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ############################################################
    #  T E S T   C A S E S
    ############################################################
    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

        #
        # Uncomment this code once READ is implemented
        #

        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_product = response.get_json()
        # self.assertEqual(new_product["name"], test_product.name)
        # self.assertEqual(new_product["description"], test_product.description)
        # self.assertEqual(Decimal(new_product["price"]), test_product.price)
        # self.assertEqual(new_product["available"], test_product.available)
        # self.assertEqual(new_product["category"], test_product.category.name)

    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        logging.debug("Product no name: %s", new_product)
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with wrong Content-Type"""
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    #
    # ADD YOUR TEST CASES HERE
    #

    ######################################################################
    # Utility functions
    ######################################################################

    def get_product_count(self):
        """save the current number of products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # logging.debug("data = %s", data)
        return len(data)

    def test_query_product_by_name(self):
        """It should Query Products by Name"""
        self._create_products(3)
        product = ProductFactory(name="SpecialName")
        self.client.post(BASE_URL, json=product.serialize())

        response = self.client.get(BASE_URL, query_string="name=SpecialName")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "SpecialName")

    def test_query_product_by_availability(self):
        """It should Query Products by Availability"""
        ProductFactory(available=True).create()
        ProductFactory(available=False).create()

        response = self.client.get(BASE_URL, query_string="available=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        for p in data:
            self.assertFalse(p["available"])

    def test_query_product_by_category(self):
        """It should Query Products by Category"""
        ProductFactory(category=Category.FOOD).create()
        ProductFactory(category=Category.TOOLS).create()

        response = self.client.get(BASE_URL, query_string="category=FOOD")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        for p in data:
            self.assertEqual(p["category"], "FOOD")

    def test_query_product_by_invalid_category(self):
        """It should return 400 for invalid category"""
        response = self.client.get(BASE_URL, query_string="category=INVALID")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_product_by_invalid_availability(self):
        """It should return 400 for invalid availability"""
        response = self.client.get(BASE_URL, query_string="available=maybe")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexistent_product(self):
        """It should return 404 for a missing product"""
        response = self.client.get(f"{BASE_URL}/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

