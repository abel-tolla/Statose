# job is to open a browser, navigate to a FotMob league URL,
# intercept the leagues?id= network response, and return the raw JSON.

from playwright.sync_api import sync_playwright


def fetch_league(fotmob_id: int, league: str, season: str):
    # sync_playwright creates a playwright session
    with sync_playwright() as p:
        # opens browser, think of it as opening chrome, firefox, safari or etc.
        # headless=False, determines if you want to be able to see this window opening up or not
        browser = p.chromium.launch()

        # create a browser page, think of it as opening a tab in your browser
        page = browser.new_page()

        # this tells playwright the next browser action I perform
        # it should capture a response matching this url pattern
        with page.expect_response(f"**/api/data/leagues?id={fotmob_id}**") as resp:
            # playwright actions: page.goto(), page.click(), page.fill(), page.locator(), page.expect_response()
            page.goto(
                f"https://www.fotmob.com/leagues/{fotmob_id}/overview/{league}?season={season}"
            )

            # gets the html element and click it, I used get_by_role because I wanted to specify that it is a link
            # you can use .get_by_text which just needs the name of the html element

            # page.get_by_role("link", name="Table").click()

        # resp is a response listener, this is the actual HTTP response
        # you can then use these methods to retrieve any information:
        # response.url, response.status, response.headers, response.body(), response.json()
        response = resp.value
        data = response.json()

        browser.close()

        return data
