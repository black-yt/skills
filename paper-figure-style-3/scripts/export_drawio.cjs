#!/usr/bin/env node
'use strict';
// Render with the actual draw.io embed editor; require Playwright on NODE_PATH
// or install the bundled package.json dependencies in the skill directory.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('playwright');

async function main() {
  const args = process.argv.slice(2);
  const files = [];
  let outputDir=path.resolve(__dirname,'../outputs');
  for (let index=0;index<args.length;index++) {
    if (args[index]==='--output-dir') {
      if (!args[index+1]) throw new Error('--output-dir requires a directory');
      outputDir=path.resolve(args[++index]);
    } else if (args[index].startsWith('--')) throw new Error('Unknown argument: '+args[index]);
    else files.push(args[index]);
  }
  if (!files.length) throw new Error('Usage: node scripts/export_drawio.cjs [--output-dir outputs] file.drawio [...]');
  const launch = { headless: true };
  if (process.env.DRAWIO_CHROMIUM_EXECUTABLE) launch.executablePath = process.env.DRAWIO_CHROMIUM_EXECUTABLE;
  const browser = await chromium.launch(launch);
  try {
    const page = await browser.newPage({ viewport: { width: 1800, height: 1200 },
      userAgent:'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36' });
    await page.setContent('<!doctype html><html><body style="margin:0"><iframe id="editor" style="width:100vw;height:100vh;border:0"></iframe></body></html>');
    await page.evaluate(() => {
      window.drawioMessages = [];
      window.addEventListener('message', event => {
        if (event.origin !== 'https://embed.diagrams.net') return;
        try { window.drawioMessages.push(JSON.parse(event.data)); } catch {}
      });
      document.querySelector('#editor').src = 'https://embed.diagrams.net/?embed=1&proto=json&spin=1&libraries=1&ui=min&dark=0';
    });
    const event = async (name, cursor) => {
      await page.waitForFunction(({name, cursor}) => window.drawioMessages.slice(cursor).some(item => item.event === name), {name, cursor}, {timeout: 120000});
      return page.evaluate(({name,cursor}) => window.drawioMessages.slice(cursor).find(item => item.event === name), {name,cursor});
    };
    const send = async message => {
      const cursor = await page.evaluate(() => window.drawioMessages.length);
      await page.evaluate(message => document.querySelector('#editor').contentWindow.postMessage(JSON.stringify(message), 'https://embed.diagrams.net'), message);
      return cursor;
    };
    await event('init', 0);
    const frame = page.frames().find(f => f.url().startsWith('https://embed.diagrams.net'));
    const version = await frame.evaluate(() => typeof EditorUi !== 'undefined' ? EditorUi.VERSION : null);
    for (const file of files) {
      const absolute = path.resolve(file);
      const xml = await fs.readFile(absolute, 'utf8');
      const outdir = outputDir;
      await fs.mkdir(outdir, {recursive:true});
      const stem = path.basename(file, path.extname(file));
      let cursor = await send({action:'load', xml, title:stem, background:'#FFFFFF', scale:1, dark:0});
      const loaded = await event('load', cursor);
      if (loaded.error) throw new Error(`${stem}: ${loaded.error}`);
      let exportedSVG;
      for (const [format, ext] of [['xmlsvg','svg'], ['xmlpng','png'], ['json','json']]) {
        cursor = await send({action:'export', format, scale:2, border:8, background:'#FFFFFF', embedImages:false, embedCellMetadata:true, includeData:true});
        const result = await event('export', cursor);
        if (result.error) throw new Error(`${stem} export: ${result.error}`);
        let data;
        if (ext === 'json') {
          data = typeof result.data === 'string' && result.data.startsWith('data:') ? decodeURIData(result.data) : Buffer.from(typeof result.data === 'string' ? result.data : JSON.stringify(result.data, null, 2));
        } else data = decodeURIData(result.data);
        await fs.writeFile(path.join(outdir, `${stem}.${ext}`), data);
        if (ext==='svg') exportedSVG=data.toString('utf8');
      }
      const dimensions=exportedSVG.match(/viewBox="[^" ]+ [^" ]+ ([\d.]+) ([\d.]+)"/);
      if (!dimensions) throw new Error(stem+': exported SVG has no viewBox');
      const printPage=await browser.newPage({colorScheme:'light'});
      try {
        await printPage.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0}svg{display:block}</style></head><body>'+exportedSVG+'</body></html>');
        await printPage.evaluate(()=>document.fonts.ready);
        await printPage.pdf({path:path.join(outdir,`${stem}.pdf`),width:dimensions[1]+'px',height:dimensions[2]+'px',printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});
      } finally {await printPage.close();}
      await fs.writeFile(path.join(outdir, `${stem}.render.json`), JSON.stringify({engine:'draw.io embed',version,modelBounds:loaded.modelBounds,source:stem+'.drawio',source_sha256:crypto.createHash('sha256').update(xml).digest('hex'),formats:['svg-with-xml','png-with-xml','pdf','native-json']},null,2)+'\n');
      console.log(`${stem}: rendered by draw.io ${version || '(version unavailable)'}`);
    }
  } finally { await browser.close(); }
}

function decodeURIData(uri) {
  if (typeof uri !== 'string' || !uri.startsWith('data:')) throw new Error('draw.io returned no data URI');
  const comma = uri.indexOf(',');
  return uri.slice(0, comma).includes(';base64') ? Buffer.from(uri.slice(comma+1),'base64') : Buffer.from(decodeURIComponent(uri.slice(comma+1)));
}
main().catch(error => {console.error(error.message); process.exitCode=1;});
