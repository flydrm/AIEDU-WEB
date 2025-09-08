import { test, expect } from '@playwright/test'

test('home shows title and bottom nav', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Kids AI' })).toBeVisible()
  await expect(page.getByRole('link', { name: '首页' })).toBeVisible()
  await expect(page.getByRole('link', { name: '聊天' })).toBeVisible()
})

test('chat can send and render messages (smoke)', async ({ page }) => {
  await page.goto('/chat')
  const input = page.getByLabel('输入消息')
  await input.fill('你好')
  await page.getByRole('button', { name: '发送' }).click()
  await expect(page.getByText('我')).toBeVisible()
})

test('lesson page loads', async ({ page }) => {
  await page.goto('/lesson')
  await expect(page.getByText('今日微课')).toBeVisible()
})

test('parent page toggles night mode and fetches metrics', async ({ page }) => {
  await page.goto('/parent')
  await page.getByLabel('夜间模式').check()
  await page.getByRole('button', { name: '查看服务指标' }).click()
  await expect(page.getByLabel('metrics')).toBeVisible()
})

