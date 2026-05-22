const puppeteer = require('puppeteer-core');
const fetch = global.fetch || require('node-fetch');
const BASE_API = 'http://127.0.0.1:8000';
const path = require('path');
const FRONTEND = 'file://' + path.resolve(__dirname, 'frontend booking hotel management', 'index.html');

async function loginGetToken(){
  const res = await fetch(BASE_API + '/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: 'admin', password: 'password123' })
  });
  if(!res.ok) throw new Error('Login failed: '+res.status);
  const j = await res.json();
  return j.access_token;
}

(async ()=>{
  try{
    const token = await loginGetToken();
    console.log('Got token, launching browser...');
    // use local Chrome executable
    const execPath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
    const browser = await puppeteer.launch({executablePath: execPath, headless: true, args: ['--no-sandbox','--disable-setuid-sandbox']});
    const page = await browser.newPage();
    // set token before any script runs
    await page.evaluateOnNewDocument((t)=>{
      localStorage.setItem('token', t);
    }, token);

    await page.goto(FRONTEND, {waitUntil: 'networkidle2', timeout: 15000});
    // navigate to employees page; try clicking nav or use hash
    // click sidebar nav item for Employees
    try{
      await page.waitForSelector('.nav-item[data-page="employees"]', {timeout:5000});
      await page.click('.nav-item[data-page="employees"]');
      await page.waitForTimeout(300);
    }catch(e){
      await page.goto(FRONTEND + '#employees', {waitUntil:'networkidle2'});
    }

    // wait for employees table
    await page.waitForSelector('#employees-tbody', {timeout:10000});

    // click Add Employee
    await page.click('#btn-add-employee');
    await page.waitForSelector('#modal-save');

    const unique = 'puppeteer.' + Date.now().toString().slice(-4);
    await page.type('#emp-name', 'Puppeteer Test User');
    // if username field present
    const usernameField = await page.$('#emp-username');
    if(usernameField){
      await page.type('#emp-username', unique);
    } else {
      // some forms don't have username; ignore
    }
    // password field if exists
    const passField = await page.$('#emp-password');
    if(passField) await page.type('#emp-password','password123');
    // select role
    try{ await page.select('#emp-role', 'Receptionist'); }catch(e){}
    await page.click('#modal-save');
    // wait for table refresh
    await page.waitForTimeout(1000);

    // find created row
    const rows = await page.$$eval('#employees-tbody tr', trs => trs.map(tr => tr.innerText));
    const created = rows.find(r => r.includes('Puppeteer Test User'));
    console.log('Created row present?', !!created);

    // attempt edit: click edit on row that contains name
    for(const r of await page.$$('#employees-tbody tr')){
      const text = await r.evaluate(n => n.innerText);
      if(text.includes('Puppeteer Test User')){
        // click the first button (edit)
        const btn = await r.$('button');
        if(btn){ await btn.click(); await page.waitForSelector('#modal-save'); await page.click('#emp-name', {clickCount:3}); await page.type('#emp-name','Puppeteer Test User Updated'); await page.click('#modal-save'); await page.waitForTimeout(800); }
        break;
      }
    }
    // verify update
    const rows2 = await page.$$eval('#employees-tbody tr', trs => trs.map(tr => tr.innerText));
    const updated = rows2.find(r => r.includes('Puppeteer Test User Updated'));
    console.log('Updated visible?', !!updated);

    // delete: click delete button on updated row
    for(const r of await page.$$('#employees-tbody tr')){
      const text = await r.evaluate(n => n.innerText);
      if(text.includes('Puppeteer Test User Updated')){
        const btns = await r.$$('button');
        if(btns.length>1){
          // second button is delete
          await btns[1].click();
          // confirm dialog
          try{ await page.waitForSelector('button:has-text("Confirm"), button:has-text("Yes")',{timeout:1000}); await page.click('button:has-text("Confirm"), button:has-text("Yes")'); }catch(e){}
          await page.waitForTimeout(800);
        }
        break;
      }
    }
    const rows3 = await page.$$eval('#employees-tbody tr', trs => trs.map(tr => tr.innerText));
    const deleted = rows3.find(r => r.includes('Puppeteer Test User Updated'));
    console.log('Deleted absent?', !deleted);

    await browser.close();
    console.log('Puppeteer UI flow done.');
    process.exit(0);
  }catch(err){
    console.error('Error during Puppeteer flow:', err);
    process.exit(2);
  }
})();
