import { test, expect } from '@playwright/test';

test.describe('Job Application Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-token',
          refresh_token: 'mock-refresh-token'
        })
      });
    });

    await page.route('**/api/auth/profile', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            roles: [{ role: 'candidate' }]
          }
        })
      });
    });

    await page.route('**/api/jobs/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          title: 'Software Engineer',
          description: 'A great job opportunity',
          location: 'San Francisco',
          employment_type: 'full_time',
          work_mode: 'remote',
          salary_min: 50000,
          salary_max: 80000
        })
      });
    });

    await page.route('**/api/applications/jobs/*/apply', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'created',
          application: {
            id: 1,
            job_id: 1,
            status: 'submitted',
            created_at: '2024-01-01T00:00:00Z'
          }
        })
      });
    });
  });

  test('should display job properties correctly', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Check that job properties are displayed with proper formatting
    await expect(page.locator('text=Apply for Software Engineer')).toBeVisible();
    await expect(page.locator('text=📍 San Francisco')).toBeVisible();
    await expect(page.locator('text=🏢 Remote')).toBeVisible();
    await expect(page.locator('text=💼 Full Time')).toBeVisible();
    await expect(page.locator('text=💰 $50,000 - $80,000')).toBeVisible();
  });

  test('should validate PDF file uploads', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Test invalid file type
    const fileInput = page.locator('input[name="resume"]');
    await fileInput.setInputFiles({
      name: 'resume.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('This is not a PDF')
    });
    
    // Check for validation error
    await expect(page.locator('text=Only PDF files are allowed')).toBeVisible();
    
    // Test valid PDF file
    await fileInput.setInputFiles({
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake pdf content')
    });
    
    // Error should be cleared
    await expect(page.locator('text=Only PDF files are allowed')).not.toBeVisible();
  });

  test('should validate file size', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Create a large file (6MB)
    const largeContent = Buffer.alloc(6 * 1024 * 1024, 'a');
    
    const fileInput = page.locator('input[name="resume"]');
    await fileInput.setInputFiles({
      name: 'large_resume.pdf',
      mimeType: 'application/pdf',
      buffer: largeContent
    });
    
    // Check for size validation error
    await expect(page.locator('text=File size must be less than 5MB')).toBeVisible();
  });

  test('should submit application successfully', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Fill out the form
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.fill('input[name="email"]', 'john@example.com');
    await page.fill('input[name="phone"]', '123-456-7890');
    await page.fill('input[name="currentCompany"]', 'Tech Corp');
    await page.fill('input[name="currentPosition"]', 'Developer');
    await page.selectOption('select[name="experience"]', '3-5 years');
    await page.selectOption('select[name="education"]', 'bachelor');
    await page.fill('textarea[name="skills"]', 'Python, JavaScript, React');
    await page.fill('input[name="portfolio"]', 'https://johndoe.com');
    await page.fill('input[name="linkedin"]', 'https://linkedin.com/in/johndoe');
    await page.fill('input[name="github"]', 'https://github.com/johndoe');
    await page.fill('input[name="availability"]', 'Immediately');
    await page.fill('input[name="salaryExpectation"]', '70000');
    await page.fill('input[name="noticePeriod"]', '2 weeks');
    await page.fill('input[name="workAuthorization"]', 'US Citizen');
    await page.fill('input[name="relocation"]', 'Yes');
    await page.fill('textarea[name="additionalInfo"]', 'Passionate about technology');
    
    // Upload PDF files
    const resumeInput = page.locator('input[name="resume"]');
    const coverLetterInput = page.locator('input[name="coverLetter"]');
    
    await resumeInput.setInputFiles({
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake resume content')
    });
    
    await coverLetterInput.setInputFiles({
      name: 'cover_letter.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake cover letter content')
    });
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Check for success message
    await expect(page.locator('text=Application submitted successfully!')).toBeVisible();
    
    // Should redirect to job page
    await expect(page).toHaveURL('/jobs/1');
  });

  test('should show validation errors for missing required fields', async ({ page }) => {
    await page.goto('/jobs/1/apply');
    
    // Try to submit without filling required fields
    await page.click('button[type="submit"]');
    
    // Check for HTML5 validation errors
    const firstNameInput = page.locator('input[name="firstName"]');
    await expect(firstNameInput).toHaveAttribute('required');
    
    const lastNameInput = page.locator('input[name="lastName"]');
    await expect(lastNameInput).toHaveAttribute('required');
    
    const emailInput = page.locator('input[name="email"]');
    await expect(emailInput).toHaveAttribute('required');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/applications/jobs/*/apply', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Validation failed'
        })
      });
    });

    await page.goto('/jobs/1/apply');
    
    // Fill out minimal form
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.fill('input[name="email"]', 'john@example.com');
    
    // Upload PDF files
    const resumeInput = page.locator('input[name="resume"]');
    const coverLetterInput = page.locator('input[name="coverLetter"]');
    
    await resumeInput.setInputFiles({
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake resume content')
    });
    
    await coverLetterInput.setInputFiles({
      name: 'cover_letter.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake cover letter content')
    });
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Check for error message
    await expect(page.locator('text=Error: Validation failed')).toBeVisible();
  });

  test('should redirect to login if not authenticated', async ({ page }) => {
    // Mock unauthenticated state
    await page.route('**/api/auth/profile', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Unauthorized'
        })
      });
    });

    await page.goto('/jobs/1/apply');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/login');
  });

  test('should show loading state during submission', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/applications/jobs/*/apply', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'created',
          application: {
            id: 1,
            job_id: 1,
            status: 'submitted',
            created_at: '2024-01-01T00:00:00Z'
          }
        })
      });
    });

    await page.goto('/jobs/1/apply');
    
    // Fill out minimal form
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.fill('input[name="email"]', 'john@example.com');
    
    // Upload PDF files
    const resumeInput = page.locator('input[name="resume"]');
    const coverLetterInput = page.locator('input[name="coverLetter"]');
    
    await resumeInput.setInputFiles({
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake resume content')
    });
    
    await coverLetterInput.setInputFiles({
      name: 'cover_letter.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('%PDF-1.4 fake cover letter content')
    });
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Check for loading state
    await expect(page.locator('button[type="submit"]:has-text("Submitting...")')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
  });
});
