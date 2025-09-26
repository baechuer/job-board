import { test, expect } from '@playwright/test';

test.describe('Candidate Applications Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application (use baseURL from Playwright config)
    await page.goto('/');
  });

  test('should hide apply button for recruiters', async ({ page }) => {
    // Login as recruiter
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer2@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard/recruiter');

    // Navigate to jobs page
    await page.click('text=Jobs');
    await page.waitForURL('**/jobs');

    // Click on first job
    await page.click('.job-card:first-child');
    await page.waitForURL('**/jobs/*');

    // Check that apply button is not visible for recruiters
    const applyButton = page.locator('text=Apply Now');
    await expect(applyButton).not.toBeVisible();

    // Check that recruiter message is shown
    await expect(page.locator('text=You\'re signed in as a recruiter')).toBeVisible();
  });

  test('should show apply button for candidates', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard/candidate');

    // Navigate to jobs page
    await page.click('text=Jobs');
    await page.waitForURL('**/jobs');

    // Click on first job
    await page.click('.job-card:first-child');
    await page.waitForURL('**/jobs/*');

    // Check that apply button is visible for candidates
    const applyButton = page.locator('text=Apply Now');
    await expect(applyButton).toBeVisible();

    // Check that candidate message is shown
    await expect(page.locator('text=You\'re signed in. Continue with your application')).toBeVisible();
  });

  test('should display applications in candidate dashboard', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard/candidate');

    // Check that applications count is displayed
    await expect(page.locator('text=Applications')).toBeVisible();
    
    // Click on "View My Applications"
    await page.click('text=View My Applications');
    await page.waitForURL('**/candidate/applications');

    // Check that applications page loads
    await expect(page.locator('h1:has-text("My Applications")')).toBeVisible();
  });

  test('should show empty state when no applications', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to applications page
    await page.goto('/candidate/applications');

    // Check empty state
    await expect(page.locator('text=No applications yet')).toBeVisible();
    await expect(page.locator('text=Browse Jobs')).toBeVisible();
  });

  test('should apply for job and see it in applications', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to jobs page
    await page.click('text=Jobs');
    await page.waitForURL('**/jobs');

    // Click on first job
    await page.click('.job-card:first-child');
    await page.waitForURL('**/jobs/*');

    // Click apply button
    await page.click('text=Apply Now');
    await page.waitForURL('**/jobs/*/apply');

    // Fill out application form
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="phone"]', '1234567890');
    
    // Select experience
    await page.selectOption('select[name="experience"]', '0-1 years');
    
    // Select education
    await page.selectOption('select[name="education"]', 'bachelor');
    
    // Fill skills
    await page.fill('textarea[name="skills"]', 'Python, JavaScript, React');
    
    // Fill salary expectation
    await page.fill('input[name="salaryExpectation"]', '90000');
    
    // Select work authorization
    await page.selectOption('select[name="workAuthorization"]', 'US Citizen');
    
    // Select relocation
    await page.selectOption('select[name="relocation"]', 'Yes');
    
    // Fill availability
    await page.fill('input[name="availability"]', 'Immediately available');
    
    // Fill additional info
    await page.fill('textarea[name="additionalInfo"]', 'I am excited about this opportunity');

    // Upload resume file
    const resumeFile = await page.locator('input[name="resume"]');
    await resumeFile.setInputFiles({
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('Test resume content')
    });

    // Upload cover letter file
    const coverLetterFile = await page.locator('input[name="coverLetter"]');
    await coverLetterFile.setInputFiles({
      name: 'cover_letter.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('Test cover letter content')
    });

    // Submit application
    await page.click('button[type="submit"]');

    // Wait for success message and redirect
    await page.waitForURL('**/jobs/*');

    // Navigate to applications page
    await page.goto('/candidate/applications');

    // Check that application appears in the list
    await expect(page.locator('text=John Doe')).toBeVisible();
    await expect(page.locator('text=submitted')).toBeVisible();
  });

  test('should show application details correctly', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to applications page
    await page.goto('/candidate/applications');

    // If there are applications, check the details
    const applicationCard = page.locator('.card').first();
    if (await applicationCard.isVisible()) {
      // Check that job title is displayed
      await expect(applicationCard.locator('h3')).toBeVisible();
      
      // Check that status is displayed
      await expect(applicationCard.locator('text=submitted')).toBeVisible();
      
      // Check that applied date is displayed
      await expect(applicationCard.locator('text=Applied')).toBeVisible();
      
      // Check that personal info is displayed
      await expect(applicationCard.locator('text=Applied as:')).toBeVisible();
      await expect(applicationCard.locator('text=Email:')).toBeVisible();
    }
  });

  test('should handle pagination correctly', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to applications page
    await page.goto('/candidate/applications');

    // Check pagination controls if there are multiple pages
    const pagination = page.locator('text=Page');
    if (await pagination.isVisible()) {
      // Check that pagination info is displayed
      await expect(pagination).toBeVisible();
      
      // Check that Previous/Next buttons are present
      await expect(page.locator('text=Previous')).toBeVisible();
      await expect(page.locator('text=Next')).toBeVisible();
    }
  });

  test('should show quick actions on applications page', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to applications page
    await page.goto('http://localhost:3000/candidate/applications');

    // Check quick actions
    await expect(page.locator('text=Browse Jobs')).toBeVisible();
    await expect(page.locator('text=Saved Jobs')).toBeVisible();
    await expect(page.locator('text=Update Profile')).toBeVisible();
  });
});

test.describe('Role-based Access Control', () => {
  test('should redirect recruiters away from candidate applications', async ({ page }) => {
    // Login as recruiter
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer2@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Try to access candidate applications page
    await page.goto('http://localhost:3000/candidate/applications');

    // Should be redirected or show access denied
    await expect(page.locator('text=Access denied')).toBeVisible();
  });

  test('should allow candidates to access applications page', async ({ page }) => {
    // Login as candidate
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'baechuer3@gmail.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Navigate to applications page
    await page.goto('http://localhost:3000/candidate/applications');

    // Should be able to access the page
    await expect(page.locator('h1:has-text("My Applications")')).toBeVisible();
  });
});
