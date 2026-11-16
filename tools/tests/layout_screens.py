import asyncio, json, sys
from playwright.async_api import async_playwright
exec(open('/tmp/lay.py').read().split('CHECK =')[0].split('VIEWS =')[1].join(['VIEWS =','']) if False else '')
VIEWS = [('d1280x600',1280,600,False),('safari1288x655',1288,655,False),('d1920x1080',1920,1080,False),('d1024x700',1024,700,False),('ipadP',768,1024,True),('ipadL',1024,768,True),
 ('se',375,667,True),('i13',390,844,True),('i13L',844,390,True),('promax',430,932,True)]
CHK = r'''
(sel) => { const bad=[]; const R=e=>e.getBoundingClientRect(); const vw=innerWidth, vh=innerHeight;
  document.querySelectorAll(sel).forEach(b => { if(b.offsetParent===null) return; const r=R(b);
    let c={top:0,left:0,bottom:vh,right:vw}; for(let p=b.parentElement;p;p=p.parentElement){ const cs=getComputedStyle(p); if(/(auto|scroll|hidden)/.test(cs.overflow+cs.overflowX+cs.overflowY)){ const q=R(p); c={top:Math.max(c.top,q.top),left:Math.max(c.left,q.left),bottom:Math.min(c.bottom,q.bottom),right:Math.min(c.right,q.right)}; } }
    if(r.top < c.top-1 || r.bottom > c.bottom+1 || r.left < c.left-1 || r.right > c.right+1) bad.push(sel+': '+(b.textContent||b.getAttribute('aria-label')||'').trim().slice(0,20)); });
  if(document.documentElement.scrollWidth > vw+1) bad.push('page wider than screen ('+document.documentElement.scrollWidth+')');
  return bad; }
'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); allbad = 0
        for name,w,h,touch in VIEWS:
            ctx = await b.new_context(viewport={'width':w,'height':h}, is_mobile=touch and w < 900, has_touch=touch)
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(700)
            out = {}
            out['start'] = [x for x in await pg.evaluate(CHK, '#start .upick button') if 'wider' in x]
            await pg.click('#btnStart'); await pg.wait_for_timeout(1200)
            out['cine'] = await pg.evaluate(CHK, '#cine button')
            await pg.evaluate('CINE && endCine()'); await pg.wait_for_timeout(300)
            await pg.evaluate("S.calls=[]; S.deck=[SCEN.find(x=>x.t==='תאונת דרכים עם נפגעים')]; spawnCall(); answer(0)"); await pg.wait_for_timeout(1500)
            await pg.evaluate("S.units.filter(u=>u.state==='free').slice(0,2).forEach(u=>u.sel=true); decide('u')"); await pg.wait_for_timeout(300); await pg.evaluate('CINE && endCine()')
            for v in ('map','units','radio'):
                await pg.evaluate(f"setView('{v}')"); await pg.wait_for_timeout(500)
                out[v] = await pg.evaluate(CHK, '#tabbar button, #incs button, #units .unit button')
            await pg.evaluate("unitCard(S.units[0])"); await pg.wait_for_timeout(300); out['card'] = await pg.evaluate(CHK, '#unitCard button'); await pg.evaluate("unitCard(null)")
            await pg.evaluate("const i=S.incs[0]; i.units.forEach(u=>{u.x=i.x;u.y=i.y;u.path=[];arrive(u)}); askForCrew(i)"); await pg.wait_for_timeout(500); out['crew'] = await pg.evaluate(CHK, '#crewReq button'); await pg.evaluate("$('#crewReq').classList.add('hidden')")
            await pg.evaluate("setPause(true)"); await pg.wait_for_timeout(300); out['pause'] = await pg.evaluate(CHK, '#pauseBox button'); await pg.evaluate("setPause(false)")
            await pg.evaluate("endShift()"); await pg.wait_for_timeout(900); out['end'] = await pg.evaluate(CHK, '#end button, #endBox button, .end button')
            out = {k:v for k,v in out.items() if v}; allbad += sum(len(v) for v in out.values())
            print(name, 'OK' if not out else json.dumps(out, ensure_ascii=False)[:1500], errs[:2], flush=True)
            if out: await pg.screenshot(path=f'/tmp/l2-{name}.png')
            await ctx.close()
        print('TOTAL', allbad)
asyncio.run(main())
