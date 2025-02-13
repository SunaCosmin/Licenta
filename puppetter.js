const puppeteer = require('puppeteer');
const fs = require('node:fs');
function parseArgs() 
{
    const args = process.argv.slice(2); 
    const result = {};
    for (let i = 0; i < args.length; i++) {
        
        if (args[i].startsWith('-')) {
            const key = args[i].substring(1); 
            const value = args[i + 1]; 
            result[key] = value;
            i++; 
        }
    }    
    return result;
}

function urlmodifier(url) {
    let modifiedUrl = '';  

    for (let i = 0; i < url.length; i++) {
        if (url[i] === '/') {
            modifiedUrl += '_';  
        } else {
            modifiedUrl += url[i]; 
        }
    }

    return modifiedUrl;
}

const args = parseArgs();
const url = args.url;

fs.mkdirSync(`data/${urlmodifier(url)}`);

(async () => {

    const browser = await puppeteer.launch({
        headless: true,  
        args: [
          '--no-sandbox',  
          '--disable-setuid-sandbox',  
          '--disable-web-security',  
          '--allow-insecure-localhost',  
          '--ignore-certificate-errors', 
        ],
      });
  const page = await browser.newPage();
  await page.goto(url); 
  const htmlContent = await page.content();
  fs.writeFile(`data/${urlmodifier(url)}/content.html`, htmlContent, (err) => {
    if (err) {
      console.log('Error writing to file', err);
    } else {
      console.log('File has been written successfully');
    }
  });
  await page.screenshot({ path: `data/${urlmodifier(url)}/image.png`, fullPage: true });
  await browser.close();
})();



