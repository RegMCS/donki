from playwright.sync_api import sync_playwright

def run_script(text):
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set headless=False to see the browser
        page = browser.new_page()

        # Open the target page
        page.goto('https://partyrock.aws/u/devseen/Yu9FE1DSv/HeadlineGraph')  # Replace with the actual URL of the page

        # Pausing to manually solve CAPTCHA
        page.pause()  # This will pause the script until you press Resume in the browser DevTools

        # After CAPTCHA is solved, you can continue the script
        print("CAPTCHA solved, resuming script...")

        # Wait for the textarea to appear (before the CAPTCHA)
        print("Waiting for the textarea to appear...")
        page.wait_for_selector('textarea[aria-label="Headlines Input"]', timeout=10000)

        # Interact with the textarea (e.g., type into it)
        page.fill('textarea[aria-label="Headlines Input"]', text)

        # Continue the script after CAPTCHA is solved
        # e.g., submitting the form or clicking a button
        page.keyboard.press('Control+Enter')  # Press Ctrl+Enter

        # Wait for a result or another page element to appear after submission
        page.pause()  # This will pause the script until you press Resume in the browser DevTools



if __name__ == '__main__':

    sample_text = """Myanmar's military regime is now facing a harder time in getting access to funding globally.

Singapore's United Overseas Bank (UOB) is cutting off ties with banks in Myanmar from Friday (Sep 1), a move that is in step with international sanctions targeting Myanmar's banking industry.

The bank will restrict all incoming and outgoing payments to and from Myanmar accounts. It will also put curbs on Visa and Mastercard transactions from Myanmar.

With this latest move, the Singapore lender is effectively severing ties with its Myanmar counterparts. 

CNA has reached out to the bank but UOB said it cannot comment on client relationships."""


    run_script(sample_text)
