import { test, expect } from '@playwright/test';

test.skip('homepage loads and shows navigation', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
});

