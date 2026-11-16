import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(**p.devices['iPhone 13']); pg=await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(800)
        await pg.click('#btnStart'); await pg.wait_for_timeout(2500); await pg.evaluate('CINE && endCine()')
        await pg.evaluate("S.calls=[]; S.deck=[SCEN.find(x=>x.t==='דקירה')]; spawnCall(); answer(0)"); await pg.wait_for_timeout(3000)
        ok=0
        for i in range(5):
            btn = await pg.query_selector('#call .qs button'); box = await btn.bounding_box()
            before = await pg.evaluate("S.active.lines.length + S.active.q.length")
            x,y = box['x']+box['width']/2, box['y']+box['height']/2
            await pg.mouse.move(x,y); await pg.mouse.down()
            # while the finger is down, the conversation moves on (forces a re-render)
            await pg.evaluate("S.active.lines.push({who:'caller', text:'בדיקה '+Math.random(), ts:'00:00:00'}); renderCall()")
            await pg.wait_for_timeout(150); await pg.mouse.up(); await pg.wait_for_timeout(400)
            after = await pg.evaluate("S.active.lines.length + S.active.q.length")
            ok += after > before + 1
            await pg.wait_for_timeout(1500)
        print('taps registered', ok, 'of 5', errs)
        await b.close()
asyncio.run(main())
