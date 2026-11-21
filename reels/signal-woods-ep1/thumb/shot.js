const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/thumb.html');await p.waitForTimeout(800);await p.locator('#t').screenshot({path:__dirname+'/signal_ep1_thumbnail.png'});await b.close()})();
