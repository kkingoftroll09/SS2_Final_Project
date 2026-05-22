#!/usr/bin/env python3
import json, time, os
from urllib import request as urllib_request, parse as urllib_parse
from playwright.sync_api import sync_playwright

BASE_API = 'http://127.0.0.1:8000'
FRONTEND_URL = 'http://127.0.0.1:8001/index.html'

# simple helper to login and get token
def get_admin_token():
    data = urllib_parse.urlencode({'username':'admin','password':'password123'}).encode('utf-8')
    req = urllib_request.Request(BASE_API + '/auth/login', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib_request.urlopen(req, timeout=5) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw).get('access_token')


def run_ui_flow():
    token = get_admin_token()
    if not token:
        print('Could not get admin token')
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        # set token in localStorage before page load
        context.add_init_script(f"() => localStorage.setItem('token', '{token}')")
        page = context.new_page()
        page.goto(FRONTEND_URL, timeout=15000)

        # try to navigate to Employees page via clicking menu if exists
        try:
            # if there's a nav link with data-page or text 'Employees'
            if page.locator("text=Employees").count() > 0:
                page.click("text=Employees")
            else:
                # try hash route
                page.goto(FRONTEND_URL + '#employees')
        except Exception as e:
            print('Could not navigate via UI menu:', e)

        # wait for employees page to load table
        page.wait_for_selector('#employees-tbody', timeout=5000)

        # click Add Employee button
        page.click('#btn-add-employee', timeout=3000)
        page.wait_for_timeout(500)

        # fill form fields in modal (assumes specific ids used by EmployeesPage openForm)
        page.fill('#e-name', 'UI Test Employee')
        page.fill('#e-username', f'ui.test.{int(time.time())%10000}')
        page.fill('#e-password', 'password123')
        page.select_option('#e-role', 'receptionist')
        page.click('#modal-save')

        # wait for toast/success and table refresh
        page.wait_for_timeout(1000)

        # find the created row by name
        rows = page.locator('#employees-tbody tr')
        created_id = None
        for i in range(rows.count()):
            txt = rows.nth(i).inner_text()
            if 'UI Test Employee' in txt:
                # try to extract onclick id from edit button
                # fallback: click edit button in this row
                try:
                    rows.nth(i).locator('button:text("Edit")').click()
                except Exception:
                    try:
                        rows.nth(i).locator('button').first.click()
                    except Exception:
                        pass
                created_id = 'found'
                break

        # attempt update via modal
        if created_id:
            page.fill('#e-name', 'UI Test Employee Updated')
            page.click('#modal-save')
            page.wait_for_timeout(800)

            # find updated text
            updated = any('UI Test Employee Updated' in rows.nth(i).inner_text() for i in range(rows.count()))
            print('Updated visible in table:', updated)

            # delete: click delete button on that row
            for i in range(rows.count()):
                txt = rows.nth(i).inner_text()
                if 'UI Test Employee Updated' in txt:
                    # delete button might have class danger
                    try:
                        rows.nth(i).locator('button.danger').click()
                    except Exception:
                        try:
                            rows.nth(i).locator('button:text("Delete")').click()
                        except Exception as e:
                            print('Could not click delete button:', e)
                    # confirm dialog
                    page.wait_for_timeout(300)
                    try:
                        page.click('button:has-text("Confirm")')
                    except Exception:
                        try:
                            page.click('button:has-text("Yes")')
                        except Exception:
                            pass
                    page.wait_for_timeout(800)
                    break

        browser.close()
    print('UI flow complete')
    return 0

if __name__ == '__main__':
    exit(run_ui_flow())
