const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});
for(const n of ['t3']){await p.goto('file://'+__dirname+'/'+n+'.html');await p.waitForTimeout(700);await p.locator('#t').screenshot({path:__dirname+'/'+n+'.png'});}await b.close()})();
