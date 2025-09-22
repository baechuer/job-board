import { test, expect } from '@playwright/test';

const API = 'http://localhost:5000/api';

async function mockAuthRoutes(page: any) {
  await page.route(`${API}/auth/register`, async route => {
    const json = { id: 123, email: 'new@user.com', verify_token: 'token' };
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(json) });
  });
  await page.route(`${API}/auth/login`, async route => {
    const json = { access_token: 'fake-token', refresh_token: 'fake-refresh' };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(json) });
  });
  await page.route(`${API}/auth/refresh`, async route => {
    const json = { access_token: 'new-fake-token' };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(json) });
  });
  await page.route(`${API}/auth/me`, async route => {
    const json = { user: { id: 1, email: 'me@me.com', username: 'me', roles: [{ role: 'candidate' }] } };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(json) });
  });
}

test('register page shows and submits form', async ({ page }) => {
  await mockAuthRoutes(page);
  await page.goto('/register');
  await expect(page.getByRole('heading', { level: 2, name: /create your account/i })).toBeVisible();
  await page.getByLabel('Email address', { exact: true }).fill('new@user.com');
  await page.getByLabel('Username', { exact: true }).fill('newuser');
  await page.getByLabel('Password', { exact: true }).fill('Password123!');
  await page.getByLabel('Confirm Password', { exact: true }).fill('Password123!');
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/verify-email/);
});

test('login works and shows home', async ({ page }) => {
  await mockAuthRoutes(page);
  await page.goto('/login');
  await expect(page.getByRole('heading', { level: 2, name: /sign in to your account/i })).toBeVisible();
  await page.getByLabel('Email address', { exact: true }).fill('me@me.com');
  await page.getByLabel('Password', { exact: true }).fill('Password123!');
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/?$/);
});
