import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(**p.devices['iPhone 13']); pg=await ctx.new_page()
        cdp=await ctx.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate', {'rate':4})
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1500)
        await pg.evaluate("localStorage.setItem('moked.units', JSON.stringify(['401','11','402','403','404','411','412','יס״מ','כלבן','בילוש','מג״ב','מסוק']))"); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.click('#btnStart'); await pg.wait_for_timeout(3000); await pg.evaluate('CINE && endCine()')
        await pg.evaluate("S.calls=[]; S.deck=[SCEN.find(x=>x.t==='פיגוע ירי'),SCEN.find(x=>x.t==='דקירה'),SCEN.find(x=>x.t==='ירי')]; spawnCall(); spawnCall(); spawnCall(); answer(0)")
        for view in ('call','map'):
            await pg.evaluate(f"setView('{view}')")
            r = await pg.evaluate("""() => new Promise(res => { const d=[]; let last=performance.now(); let lt=[]; 
               const po = new PerformanceObserver(l => l.getEntries().forEach(e => lt.push(Math.round(e.duration)))); try{ po.observe({type:'longtask', buffered:false}); }catch(e){}
               const f = t => { d.push(t-last); last=t; if(d.length<300) requestAnimationFrame(f); else { po.disconnect(); d.sort((a,b)=>a-b); res({median:d[150].toFixed(1), p95:d[285].toFixed(1), max:d[299].toFixed(1), longtasks:lt.length, worst:Math.max(0,...lt)}); } }; requestAnimationFrame(f); })""")
            print(view, r)
        # tap latency: time from click to DOM change for asking a question
        await pg.evaluate("setView('call')")
        lat = await pg.evaluate("""async () => { const out=[]; for(let i=0;i<5;i++){ const b=document.querySelector('#call .qs button'); if(!b) break; const t0=performance.now(); b.click(); await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))); out.push(Math.round(performance.now()-t0)); await new Promise(r=>setTimeout(r,1500)); } return out; }""")
        print('tap to next frame ms', lat)
        await b.close()
asyncio.run(main())
