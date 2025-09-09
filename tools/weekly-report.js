#!/usr/bin/env node
// Fetch timeseries from backend and export a lightweight PDF via puppeteer
const fs = require('fs')
const path = require('path')
const puppeteer = require('puppeteer')

async function main() {
  const base = process.env.REPORT_BASE_URL || 'http://localhost:8000'
  const out = process.argv[2] || path.join(__dirname, '..', 'docs', 'weekly-report.pdf')
  const res = await fetch(`${base}/api/v1/parent/mastery/timeseries?days=7`)
  const series = await res.json()
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Weekly Report</title>
  <style>body{font-family:Arial, sans-serif;padding:24px} table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:6px}</style>
  </head><body>
  <h1>Kids AI Weekly Report</h1>
  <p>Base: ${base}</p>
  <table><thead><tr><th>Date</th><th>Count</th><th>Success Rate</th></tr></thead><tbody>
  ${series.map((r)=>`<tr><td>${r.date}</td><td>${r.count}</td><td>${(r.success_rate*100).toFixed(1)}%</td></tr>`).join('')}
  </tbody></table>
  </body></html>`
  const browser = await puppeteer.launch({ headless: 'new' })
  const page = await browser.newPage()
  await page.setContent(html, { waitUntil: 'networkidle0' })
  await page.pdf({ path: out, format: 'A4', printBackground: true })
  await browser.close()
  console.log(`Saved ${out}`)
}

main().catch((e)=>{ console.error(e); process.exit(1) })
