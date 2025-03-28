const puppeteer = require('puppeteer');
const fs = require('node:fs');
const sharp = require('sharp');
const path = require('path');

function parseArgs() {
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

function arraysEqual(a, b) {
    return a.length === b.length && a.every((val, index) => val === b[index]);
}

//This function needs improvments
function checkIfAllPixelsAreSame(imagePath) {
  return sharp(imagePath)
      .raw()
      .toBuffer()
      .then((data) => {
          const width = 100; 
          const height = Math.floor(data.length / (width * 4)); 
          let isUniform = true;

          const firstPixel = [data[0], data[1], data[2], data[3]]; 

          for (let i = 4; i < data.length; i += 4) {
              const currentPixel = [data[i], data[i + 1], data[i + 2], data[i + 3]];
              if (!arraysEqual(firstPixel, currentPixel)) {
                  isUniform = false;
                  break;
              }
          }

          return isUniform;
      })
      .catch((err) => {
          console.error(`Error processing image ${imagePath}:`, err);
          return false;
      });
}

async function janitor() {
  const directoryPath = 'buffer'; 
  const dirs = fs.readdirSync(directoryPath);

  for (const dir of dirs) {
    const file_content = fs.readdirSync(`buffer/${dir}`);
    const image_path = `buffer/${dir}/image.png`;
    
    if(fs.existsSync(image_path)){
        checkIfAllPixelsAreSame(image_path).then((result) => {
        if (result) {
            console.log(`All pixels in ${image_path} are the same!`);
            fs.rmSync(`buffer/${dir}`, { recursive: true, force: true });
        } 
        }).catch((err) => {
            console.error(`Error checking image ${image_path}`);
        });
    }

    fs.readFile('messages.txt', 'utf-8', (err, data) => {
        if (err) {
            return console.error('Error reading messages.txt:', err.message);
        }
    
        const messages = data.split("\n").map(line => line.trim()).filter(line => line.length > 0);
    
       
        fs.readdir('buffer', (err, dirs) => {
            if (err) {
                return console.error('Error reading buffer directory:', err.message);
            }
    
            for (const dir of dirs) {
                const contentPath = path.join('buffer', dir, 'content.html');
    
                if (fs.existsSync(contentPath)) {
                    const fileContent = fs.readFileSync(contentPath, 'utf-8');
                    for (const message of messages) {
                        const regex = new RegExp(`\\b${message.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g'); 
                        if (regex.test(fileContent)) {
                            console.log(`Invalid message fouund at ${dir}`);
                            fs.rmSync(path.join('buffer', dir), { recursive: true, force: true });
                            break; 
                        }
                    }
                }
            }
        });
    });
    

    if (file_content.length === 0) {
        console.log(`Removing empty directory: data/${dir}`);
        fs.rmdirSync(`buffer/${dir}`);
      }

  }
}

const args = parseArgs();
const page_number = args.page_number;
let fetch_link = "";  

if (!page_number || isNaN(page_number) || parseInt(page_number) < 0) 
  fetch_link = "https://phishtank.org/phish_search.php?page=0&active=y&valid=y&Search=Search";
 else 
  fetch_link = `https://phishtank.org/phish_search.php?page=${page_number}&active=y&valid=y&Search=Search`;

async function data_extractor(url) {
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

    fs.mkdirSync(`buffer/${urlmodifier(url)}`);
    const page = await browser.newPage();
    await page.goto(url);
    const htmlContent = await page.content();

    fs.writeFile(`buffer/${urlmodifier(url)}/content.html`, htmlContent, (err) => {
        if (err) {
            console.log('Error writing to file', err);
        } else {
            console.log('File has been written successfully');
        }
    });

    await page.screenshot({ path: `buffer/${urlmodifier(url)}/image.png`, fullPage: true });
    fs.writeFileSync(`buffer/${urlmodifier(url)}/url.txt`, url, 'utf8')
    await browser.close();
}

fetch(fetch_link)
    .then(response => response.text())
    .then(data => {
        data= data.split('\n')[63];
        let links = [];
        let i = 0;
        while (i < data.length) {
     
          if (data.substring(i, i + 4) === "http") {
          
            let urlEnd = data.indexOf(' ', i);
            if (urlEnd === -1) {
              urlEnd = data.indexOf('"', i); 
            }
    
            if (urlEnd !== -1) {
              
              const url = data.substring(i, urlEnd);
              links.push(url);
              i = urlEnd; 
            } else {
              break; 
            }
          } else {
            i++; 
          }
        }
        
        for (let i = 0; i < links.length; i++) {
            links[i] = links[i].slice(0, -3);
        }

        console.log(links);
        const promises = links.map(url => {
            return fetch(url)
                .then(response => {
                    if (response.ok) {
                        return data_extractor(url);  
                    }
                }).catch(error => {
                    console.log('Error with link', url, error);
                });
        });

        Promise.all(promises)
            .then(() => {
                console.log("The janitor is being called");
                janitor();
            })
            .catch(err => {
                console.error('Error during scraping process', err);
            });
        

    })
    .catch(console.error);

    