const { chromium } = require('playwright');

const BASE = 'http://edupro.localhost:8080';
const OUT = 'C:\\Users\\ttsha\\Documents\\Edupro SMS\\manual_screenshots';

async function loginAndShoot(browser, { email, password, shots }) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.fill('#login_email', email);
  await page.fill('#login_password', password);
  await page.click('.btn-login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  for (const shot of shots) {
    if (shot.url) {
      await page.goto(BASE + shot.url, { waitUntil: 'networkidle' });
      await page.waitForTimeout(800);
    }
    if (shot.click) {
      await page.click(shot.click);
      await page.waitForTimeout(500);
    }
    await page.screenshot({ path: `${OUT}\\${shot.name}.png`, fullPage: shot.fullPage !== false });
    console.log('saved', shot.name);
  }
  await context.close();
}

(async () => {
  const browser = await chromium.launch();

  // Login page (no auth)
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${OUT}\\01_login.png` });
    await context.close();
    console.log('saved 01_login');
  }

  // Headmaster
  await loginAndShoot(browser, {
    email: 'qa.manual.headmaster@example.edupro.test',
    password: 'TempQA2026#',
    shots: [
      { name: '02_headmaster_dashboard', url: '/dashboard' },
      { name: '03_headmaster_classreview', url: '/class-review?group=' + encodeURIComponent('Form 1 Purple') },
    ],
  });

  // Teacher
  await loginAndShoot(browser, {
    email: 'qa.manual.teacher@example.edupro.test',
    password: 'TempQA2026#',
    shots: [
      { name: '04_teacher_dashboard', url: '/dashboard' },
      { name: '05_marks_entry', url: '/marks-entry?plan=EDU-ASP-2026-00088' },
    ],
  });

  // Bursar
  await loginAndShoot(browser, {
    email: 'qa.manual.bursar@example.edupro.test',
    password: 'TempQA2026#',
    shots: [
      { name: '06_bursar', url: '/bursar' },
    ],
  });

  // Student / parent portal
  await loginAndShoot(browser, {
    email: '00126@firstclasshigh.ac.zw',
    password: 'TempQA2026#',
    shots: [
      { name: '07_myreports_overview', url: '/my-reports', fullPage: true },
      { name: '08_myreports_grades', click: 'button.tab-btn:has-text("Grades")', fullPage: false },
      { name: '09_myreports_profile', click: 'button.tab-btn:has-text("Profile")', fullPage: false },
      { name: '10_myreports_fees', click: 'button.tab-btn:has-text("Fees")', fullPage: false },
    ],
  });

  // Print views (public-ish, still needs the headmaster/bursar session for permission)
  await loginAndShoot(browser, {
    email: 'qa.manual.headmaster@example.edupro.test',
    password: 'TempQA2026#',
    shots: [
      { name: '11_report_card_pdf', url: '/printview?doctype=Report%20Card&name=' + encodeURIComponent('RC-EDU-STU-2026-00004-2026 (Term 2)') + '&format=IGCSE%20Report%20Card&no_letterhead=0' },
      { name: '12_fee_statement_pdf', url: '/printview?doctype=Student&name=EDU-STU-2026-00011&format=Fee%20Statement&no_letterhead=0' },
    ],
  });

  await browser.close();
  console.log('DONE');
})().catch((err) => { console.error(err); process.exit(1); });
