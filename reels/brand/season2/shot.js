const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [n,h] of [['post',1350],['story',1920]]){const p=await b.newPage({viewport:{width:1080,height:h}});await p.goto('file://'+__dirname+'/'+n+'.html');await p.waitForTimeout(800);await p.locator('#t').screenshot({path:__dirname+'/season2_out_'+n+'.png'});}
await b.close()})();
