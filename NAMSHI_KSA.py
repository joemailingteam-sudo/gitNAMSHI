import asyncio
import csv
import json
from urllib.parse import urljoin
from playwright.async_api import async_playwright


async def scrape_jumia(query="nike shoes", output="csv", max_pages=3):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            products = []

            for page_num in range(1, max_pages + 1):
                print(f"scrape page {page_num}")

                URL = f"https://www.namshi.com/saudi-en/kids/search/?q=nike%20{query}"

                await page.goto(URL, wait_until="domcontentloaded")

                # Wait for products
                try:
                    await page.wait_for_selector(
                        "div.ProductBox_container__wiajf.ProductBox_boxContainer__p7PaQ",
                        timeout=10000,
                    )
                except Exception:
                    print(f"no products found on page {page_num}")
                    break

                # Get product cards
                product_elements = await page.query_selector_all(
                    "div.ProductBox_container__wiajf.ProductBox_boxContainer__p7PaQ"
                )

                print(f"Found {len(product_elements)} products " f"on page {page_num}")

                for product in product_elements:
                    try:

                        # -------------------------
                        # PRODUCT TITLE
                        # -------------------------
                        title_element = await product.query_selector(
                            "div.ProductImage_imageContainer__B5pcR img"
                        )

                        # -------------------------
                        # PRODUCT PRICE
                        # -------------------------
                        price_element = await product.query_selector(
                            "div.ProductPrice_preReductionPrice__oM4c9"
                        )

                        # -------------------------
                        # RATING
                        # -------------------------
                        rating_element = await product.query_selector("div.rating-star")

                        rating = (
                            await rating_element.inner_text()
                            if rating_element
                            else "N/A"
                        )

                        # -------------------------
                        # REVIEW COUNT
                        # -------------------------
                        review_count = (
                            await rating_element.get_attribute("data-count-reviews")
                            if rating_element
                            else "N/A"
                        )

                        # -------------------------
                        # DISCOUNT / OLD PRICE
                        # -------------------------
                        discount_element = await product.query_selector(
                            "span.ProductPrice_value__YcE7Z"
                        )

                        # -------------------------
                        # PRODUCT LINK
                        # -------------------------
                        link_element = await product.query_selector(
                            "a.ProductBox_container__wiajf"
                        )

                        # -------------------------
                        # EXTRACT TITLE
                        # -------------------------
                        title = (
                            await title_element.get_attribute("alt")
                            if title_element
                            else "N/A"
                        )

                        # -------------------------
                        # EXTRACT PRICE
                        # -------------------------
                        price = (
                            await price_element.inner_text() if price_element else "N/A"
                        )

                        # -------------------------
                        # EXTRACT DISCOUNT
                        # -------------------------
                        discount = (
                            await discount_element.inner_text()
                            if discount_element
                            else "no discount"
                        )

                        # -------------------------
                        # EXTRACT LINK
                        # -------------------------
                        link = await link_element.get_attribute("href")

                        if not link:
                            link = "N/A"

                        elif not link.startswith("http"):
                            link = urljoin("https://www.namshi.com/", link)

                        # -------------------------
                        # ADD PRODUCT
                        # -------------------------
                        products.append(
                            {
                                "title": title.strip(),
                                "price": price.strip(),
                                "rating": rating.strip(),
                                "reviews": review_count,
                                "discount": discount.strip(),
                                "link": link,
                            }
                        )

                    except Exception as e:
                        print(f"Error extracting product data: {e}")
                        continue

            await browser.close()

            # -------------------------
            # SAVE DATA
            # -------------------------
            file_name = f"{query}.productos.{output}"

            if output == "csv":

                with open(file_name, "w", newline="", encoding="utf-8") as file:

                    fieldnames = [
                        "title",
                        "price",
                        "rating",
                        "reviews",
                        "discount",
                        "link",
                    ]

                    writer = csv.DictWriter(file, fieldnames=fieldnames)

                    writer.writeheader()
                    writer.writerows(products)

            elif output == "json":

                with open(file_name, "w", encoding="utf-8") as file:

                    json.dump(products, file, indent=4, ensure_ascii=False)

            print(
                f"Successfully scraped {len(products)} "
                f"products across pages. "
                f"Data saved to {file_name}"
            )

        except Exception as e:
            print(f"An error occured: {e}")


asyncio.run(scrape_jumia(query="nike shoes", output="csv", max_pages=3))
