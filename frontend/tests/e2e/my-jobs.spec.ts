import { test, expect } from '@playwright/test';

test('recruiter can view My Jobs and job detail', async ({ page }) => {
  const apiBase = 'http://localhost:5000/api';
  const email = `myjobs_${Date.now()}@example.com`;
  const password = 'Password123!';
  const username = `myjobs_${Date.now()}`;

  await page.request.post(`${apiBase}/auth/register`, { data: { email, password, username } });
  const loginRes = await page.request.post(`${apiBase}/auth/login`, { data: { email, password } });
  const { access_token, refresh_token } = await loginRes.json();

  await page.addInitScript(([t, r]) => { localStorage.setItem('token', t); localStorage.setItem('refresh_token', r); }, [access_token, refresh_token]);

  await page.goto('http://localhost:5173/recruiter/create-job');
  await page.getByLabel('Title').fill('MyJobs E2E');
  await page.getByLabel('Description').fill('desc long enough');
  await page.getByLabel('Salary Min').fill('1');
  await page.getByLabel('Salary Max').fill('2');
  await page.getByLabel('Location').fill('Remote');
  await page.getByLabel('Requirements (comma separated)').fill('A');
  await page.getByLabel('Responsibilities').fill('Resp');
  await page.getByLabel('Skills (comma separated)').fill('S');
  await page.getByLabel('Application Deadline').fill('2030-10-31');
  await page.getByRole('button', { name: /post job/i }).click();

  await page.goto('http://localhost:5173/recruiter/my-jobs');
  await expect(page.getByText('MyJobs E2E')).toBeVisible();
  await page.getByText('MyJobs E2E').click();
  await expect(page.getByRole('heading', { name: /myjobs e2e/i })).toBeVisible();
});


