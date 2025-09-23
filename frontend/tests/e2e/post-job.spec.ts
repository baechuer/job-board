import { test, expect } from '@playwright/test';

test('recruiter can post a job with extended fields', async ({ page }) => {
  // Ensure backend user exists and obtain tokens via API
  const apiBase = 'http://localhost:5000/api';
  const email = `recruiter_${Date.now()}@example.com`;
  const password = 'Password123!';
  const username = `recruiter_${Date.now()}`;

  await page.request.post(`${apiBase}/auth/register`, {
    data: { email, password, username },
  });
  const loginRes = await page.request.post(`${apiBase}/auth/login`, {
    data: { email, password },
  });
  const loginJson = await loginRes.json();
  const accessToken = loginJson.access_token as string;
  const refreshToken = loginJson.refresh_token as string;

  // Prime tokens in localStorage before visiting app
  await page.addInitScript(([token, refresh]) => {
    localStorage.setItem('token', token as string);
    localStorage.setItem('refresh_token', refresh as string);
  }, [accessToken, refreshToken]);

  await page.goto('http://localhost:5173/');

  // Navigate to Post Job
  await page.goto('http://localhost:5173/recruiter/create-job');

  await page.getByLabel('Title').fill('QA Engineer');
  await page.getByLabel('Description').fill('Testing applications');
  await page.getByLabel('Salary Min').fill('70000');
  await page.getByLabel('Salary Max').fill('90000');
  await page.getByLabel('Location').fill('Remote');
  await page.getByLabel('Requirements (comma separated)').fill('Testing, Selenium');
  await page.getByLabel('Responsibilities').fill('Write test plans');
  await page.getByLabel('Skills (comma separated)').fill('JS, Playwright');
  await page.getByLabel('Application Deadline').fill('2025-10-31');
  await page.getByLabel('Employment Type').selectOption('full_time');
  await page.getByLabel('Seniority').selectOption('junior');
  await page.getByLabel('Work Mode').selectOption('remote');
  await page.getByLabel('Visa Sponsorship').selectOption('no');
  await page.getByLabel('Work Authorization (e.g. US Citizen, H1B)').fill('Any');
  await page.getByLabel('Nice to haves').fill('Cypress');
  await page.getByLabel('About team').fill('QA Team');

  await page.getByRole('button', { name: /post job/i }).click();

  // Debug: capture response body for create-job call
  const resp = await page.waitForResponse(r => r.url().includes('/recruiter/create-job') && r.request().method() === 'POST');
  const body = await resp.json().catch(() => ({}));
  // Expect success
  expect({ status: resp.status(), body }).toEqual(expect.objectContaining({ status: 201 }));
});


