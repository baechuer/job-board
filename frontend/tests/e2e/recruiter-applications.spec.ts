import { test, expect } from '@playwright/test';

test.describe('Recruiter Application Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'fake-token',
          user: {
            id: 1,
            email: 'recruiter@example.com',
            username: 'recruiter',
            roles: [{ role: 'recruiter' }]
          }
        })
      });
    });

    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: 1,
            email: 'recruiter@example.com',
            username: 'recruiter',
            roles: [{ role: 'recruiter' }]
          }
        })
      });
    });

    await page.route('**/api/recruiter/my-jobs/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          title: 'Software Engineer',
          description: 'A great job opportunity',
          location: 'San Francisco',
          salary_min: 50000,
          salary_max: 80000,
          employment_type: 'full_time',
          seniority: 'mid',
          work_mode: 'remote',
          status: 'active',
          created_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    await page.route('**/api/applications/jobs/*/applications', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          applications: [
            {
              id: 1,
              first_name: 'John',
              last_name: 'Doe',
              email: 'john@example.com',
              phone: '123-456-7890',
              current_company: 'Tech Corp',
              experience: '3-5 years',
              salary_expectation: 70000,
              status: 'submitted',
              applied_at: '2024-01-01T00:00:00Z',
              additional_info: 'Passionate developer'
            },
            {
              id: 2,
              first_name: 'Jane',
              last_name: 'Smith',
              email: 'jane@example.com',
              phone: '987-654-3210',
              current_company: 'Startup Inc',
              experience: '1-2 years',
              salary_expectation: 60000,
              status: 'accepted',
              applied_at: '2024-01-02T00:00:00Z',
              additional_info: 'Eager to learn'
            },
            {
              id: 3,
              first_name: 'Bob',
              last_name: 'Johnson',
              email: 'bob@example.com',
              phone: '555-123-4567',
              current_company: 'Big Corp',
              experience: '5-10 years',
              salary_expectation: 90000,
              status: 'rejected',
              applied_at: '2024-01-03T00:00:00Z',
              additional_info: 'Senior developer'
            }
          ],
          pagination: {
            total: 3,
            pages: 1,
            current_page: 1,
            per_page: 20
          }
        })
      });
    });

    await page.route('**/api/applications/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '123-456-7890',
          current_company: 'Tech Corp',
          current_position: 'Developer',
          experience: '3-5 years',
          education: 'bachelor',
          skills: 'Python, JavaScript, React',
          portfolio: 'https://johndoe.com',
          linkedin: 'https://linkedin.com/in/johndoe',
          github: 'https://github.com/johndoe',
          availability: 'Immediately',
          salary_expectation: 70000,
          notice_period: '2 weeks',
          work_authorization: 'US Citizen',
          relocation: 'Yes',
          additional_info: 'Passionate about technology',
          status: 'submitted',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          resume_path: 'resumes/john_doe_resume.pdf',
          cover_letter_path: 'cover_letters/john_doe_cover_letter.pdf',
          job: {
            id: 1,
            title: 'Software Engineer',
            location: 'San Francisco',
            employment_type: 'full_time',
            seniority: 'mid',
            work_mode: 'remote',
            salary_min: 50000,
            salary_max: 80000
          }
        })
      });
    });

    await page.route('**/api/applications/*/status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Application status updated successfully',
          application_id: 1,
          status: 'accepted'
        })
      });
    });

    await page.route('**/api/applications/*/resume', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        body: Buffer.from('fake pdf content')
      });
    });

    await page.route('**/api/applications/*/cover-letter', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        body: Buffer.from('fake cover letter content')
      });
    });
  });

  test('complete recruiter application management flow', async ({ page }) => {
    // Navigate to job detail page
    await page.goto('/recruiter/my-jobs/1');
    
    // Wait for job details to load
    await expect(page.getByText('Software Engineer')).toBeVisible();
    await expect(page.getByText('San Francisco')).toBeVisible();
    
    // Click "View Applications" button
    await page.getByRole('button', { name: 'View Applications' }).click();
    
    // Wait for applications page to load
    await expect(page.getByText('Job Applications')).toBeVisible();
    await expect(page.getByText('John Doe')).toBeVisible();
    await expect(page.getByText('Jane Smith')).toBeVisible();
    await expect(page.getByText('Bob Johnson')).toBeVisible();
    
    // Check status filter tabs
    await expect(page.getByText('All Applications')).toBeVisible();
    await expect(page.getByText('Submitted')).toBeVisible();
    await expect(page.getByText('Accepted')).toBeVisible();
    await expect(page.getByText('Rejected')).toBeVisible();
    
    // Check status counts
    await expect(page.getByText('3')).toBeVisible(); // All applications count
    await expect(page.getByText('1')).toBeVisible(); // Individual status counts
    
    // Test filtering by status
    await page.getByText('Submitted').click();
    await expect(page.getByText('John Doe')).toBeVisible();
    await expect(page.getByText('Jane Smith')).not.toBeVisible();
    await expect(page.getByText('Bob Johnson')).not.toBeVisible();
    
    // Go back to all applications
    await page.getByText('All Applications').click();
    await expect(page.getByText('John Doe')).toBeVisible();
    await expect(page.getByText('Jane Smith')).toBeVisible();
    await expect(page.getByText('Bob Johnson')).toBeVisible();
    
    // Test filtering by accepted status
    await page.getByText('Accepted').click();
    await expect(page.getByText('Jane Smith')).toBeVisible();
    await expect(page.getByText('John Doe')).not.toBeVisible();
    await expect(page.getByText('Bob Johnson')).not.toBeVisible();
    
    // Go back to all applications
    await page.getByText('All Applications').click();
    
    // Test status update
    await page.getByRole('button', { name: 'Accept' }).first().click();
    
    // Click on "View Full Application" for John Doe
    await page.getByRole('button', { name: 'View Full Application' }).first().click();
    
    // Wait for application detail page to load
    await expect(page.getByText('Application Details')).toBeVisible();
    await expect(page.getByText('John Doe')).toBeVisible();
    await expect(page.getByText('john@example.com')).toBeVisible();
    await expect(page.getByText('Tech Corp')).toBeVisible();
    
    // Check job information sidebar
    await expect(page.getByText('Job Information')).toBeVisible();
    await expect(page.getByText('Software Engineer')).toBeVisible();
    await expect(page.getByText('San Francisco')).toBeVisible();
    await expect(page.getByText('Full Time')).toBeVisible();
    await expect(page.getByText('Mid')).toBeVisible();
    await expect(page.getByText('Remote')).toBeVisible();
    await expect(page.getByText('$50,000 - $80,000')).toBeVisible();
    
    // Check status actions
    await expect(page.getByText('Status Actions')).toBeVisible();
    await expect(page.getByText('Mark as Reviewing')).toBeVisible();
    await expect(page.getByText('Accept')).toBeVisible();
    await expect(page.getByText('Reject')).toBeVisible();
    
    // Check documents section
    await expect(page.getByText('Documents')).toBeVisible();
    await expect(page.getByText('Resume')).toBeVisible();
    await expect(page.getByText('Cover Letter')).toBeVisible();
    
    // Test document viewing
    await page.getByRole('button', { name: 'View' }).first().click();
    await expect(page.getByText('Resume - John Doe')).toBeVisible();
    await expect(page.getByText('Close')).toBeVisible();
    
    // Close the modal
    await page.getByRole('button', { name: 'Close' }).click();
    await expect(page.getByText('Resume - John Doe')).not.toBeVisible();
    
    // Test document download
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download' }).first().click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('john_doe_resume.pdf');
    
    // Test status update from detail page
    await page.getByRole('button', { name: 'Accept' }).first().click();
    
    // Test back navigation
    await page.getByText('← Back to Applications').click();
    await expect(page.getByText('Job Applications')).toBeVisible();
    
    // Test back to job details
    await page.getByText('← Back to Job Details').click();
    await expect(page.getByText('Software Engineer')).toBeVisible();
  });

  test('handles empty applications list', async ({ page }) => {
    // Mock empty applications response
    await page.route('**/api/applications/jobs/*/applications', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          applications: [],
          pagination: {
            total: 0,
            pages: 0,
            current_page: 1,
            per_page: 20
          }
        })
      });
    });

    await page.goto('/recruiter/my-jobs/1');
    await page.getByRole('button', { name: 'View Applications' }).click();
    
    await expect(page.getByText('No applications')).toBeVisible();
    await expect(page.getByText('No applications have been submitted for this job yet.')).toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/applications/jobs/*/applications', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error'
        })
      });
    });

    await page.goto('/recruiter/my-jobs/1');
    await page.getByRole('button', { name: 'View Applications' }).click();
    
    await expect(page.getByText('Error')).toBeVisible();
    await expect(page.getByText('Failed to load applications')).toBeVisible();
  });

  test('handles application detail not found', async ({ page }) => {
    // Mock application not found
    await page.route('**/api/applications/999', async route => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Application not found or access denied'
        })
      });
    });

    await page.goto('/recruiter/applications/999');
    
    await expect(page.getByText('Application Not Found')).toBeVisible();
    await expect(page.getByText('The application you\'re looking for doesn\'t exist.')).toBeVisible();
  });

  test('handles file download errors', async ({ page }) => {
    // Mock file download error
    await page.route('**/api/applications/*/resume', async route => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Resume not found'
        })
      });
    });

    await page.goto('/recruiter/applications/1');
    
    // Try to download resume
    await page.getByRole('button', { name: 'Download' }).first().click();
    
    // Should handle error gracefully (no crash)
    await expect(page.getByText('Application Details')).toBeVisible();
  });
});
