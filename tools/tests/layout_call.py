import asyncio, json, sys
from playwright.async_api import async_playwright
VIEWS = [('d1280x600',1280,600,False),('safari1288x655',1288,655,False),('d1366x768',1366,768,False),('d1440x900',1440,900,False),('d1536x864',1536,864,False),
 ('d1920x1080',1920,1080,False),('d2560x1300',2560,1300,False),('d1024x700',1024,700,False),('ipadP',768,1024,True),('ipadL',1024,768,True),
 ('se',375,667,True),('i13',390,844,True),('i13L',844,390,True),('pixel',412,915,True),('promax',430,932,True)]
CHECK = r'''
(name) => {
  const bad = [], R = el => el.getBoundingClientRect(), vis = el => { const r = R(el); return r.width > 0 && r.height > 0; };
  const vw = innerWidth, vh = innerHeight;
  const inside = (r, c, tol=1) => r.top >= c.top - tol && r.bottom <= c.bottom + tol && r.left >= c.left - tol && r.right <= c.right + tol;
  // what clips an element: every scrolling/hidden ancestor
  const clipRect = el => { let r = {top:0,left:0,bottom:vh,right:vw}; for(let p = el.parentElement; p; p = p.parentElement){ const cs = getComputedStyle(p); if(/(auto|scroll|hidden|clip)/.test(cs.overflow + cs.overflowY + cs.overflowX)){ const q = R(p); r = {top:Math.max(r.top,q.top),left:Math.max(r.left,q.left),bottom:Math.min(r.bottom,q.bottom),right:Math.min(r.right,q.right)}; } } return r; };
  const fully = el => vis(el) && inside(R(el), clipRect(el));
  const panel = document.getElementById('callPanel');
  if(S.active && vis(panel)){
    const vfully = el => { if(!vis(el)) return false; const r = R(el), c = clipRect(el.closest('.chips') || el); return r.top >= c.top - 1 && r.bottom <= c.bottom + 1; };
    document.querySelectorAll('#call .call-foot button').forEach(b => { if(b.offsetParent === null) return; if(b.closest('.chips') ? !vfully(b) : !fully(b)) bad.push('foot button cut: ' + b.textContent.trim().slice(0,22)); });
    const tr = document.getElementById('tr'); if(tr){ const r = R(tr), c = clipRect(tr); const h = Math.min(r.bottom,c.bottom) - Math.max(r.top,c.top); if(h < 40) bad.push('transcript visible ' + Math.round(h) + 'px'); }
    const loc = document.querySelector('#call .loc'); if(loc && !fully(loc)) bad.push('address cut');
    const ask = document.getElementById('askPanel');
    const qb = [...document.querySelectorAll(vis(ask) ? '#askBody .qs button' : '#call .qs button')];
    const full = qb.filter(fully).length;
    if(qb.length && full < Math.min(qb.length, 4)) bad.push('questions fully visible ' + full + '/' + qb.length);
    const tabs = document.querySelector(vis(ask) ? '#askBody .tabs' : '#call .tabs'); if(tabs && !fully(tabs)) bad.push('question tabs cut');
    const bc = document.getElementById('bcBox'); if(bc && vis(bc)) document.querySelectorAll('#call .call-foot button, #call .qs button').forEach(b => { const a = R(b), c = R(bc); if(vis(b) && a.top < c.bottom && a.bottom > c.top && a.left < c.right && a.right > c.left && b.closest('.call-foot')) bad.push('broadcast covers ' + b.textContent.trim().slice(0,15)); });
  }
  // a waiting line must be reachable
  if(S.calls.some(c => !c.held)){
    const qa = document.getElementById('quickAns'), btn = document.querySelector('#queue [data-ans]');
    if(!(qa && vis(qa) && !qa.classList.contains('hidden')) && !(btn && fully(btn))) bad.push('no reachable answer button');
    if(qa && vis(qa) && !qa.classList.contains('hidden')) document.querySelectorAll('#call .call-foot button').forEach(b => { const a = R(b), c = R(qa); if(vis(b) && a.top < c.bottom - 2 && a.bottom > c.top + 2 && a.left < c.right && a.right > c.left) bad.push('answer pill covers ' + b.textContent.trim().slice(0,15)); });
  }
  if(document.documentElement.scrollWidth > vw + 1) bad.push('page wider than screen');
  return bad;
}
'''
async def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name,w,h,touch in VIEWS:
            if only and only != name: continue
            ctx = await b.new_context(viewport={'width':w,'height':h}, is_mobile=touch and w < 900, has_touch=touch, device_scale_factor=2)
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(700)
            await pg.evaluate("localStorage.setItem('moked.units', JSON.stringify(['401','11','402','403','404','411','412','יס״מ','כלבן','בילוש','מג״ב','מסוק']))")
            await pg.reload(); await pg.wait_for_timeout(700)
            await pg.click('#btnStart'); await pg.wait_for_timeout(2500); await pg.evaluate('CINE && endCine()'); await pg.wait_for_timeout(300)
            res = {}
            for waiting in (0,3,8):
                for stage in ('fresh','sent','bc'):
                    await pg.evaluate(f"""(() => {{ S.calls=[]; S.active=null; S.deck=[SCEN.find(x=>x.t==='פיגוע ירי')]; for(let i=0;i<{waiting}+1;i++) spawnCall(); answer(0);
                       if(typeof setView==='function') setView('call'); }})()""")
                    await pg.wait_for_timeout(1800)
                    if stage in ('asked','sent','bc'):
                        await pg.evaluate("for(let i=0;i<3;i++){ const q=tabList(S.active).list[0]; if(q) ask(q.id); }"); await pg.wait_for_timeout(1500)
                    if stage in ('sent','bc'):
                        await pg.evaluate("S.units.filter(u=>u.state==='free').slice(0,2).forEach(u=>u.sel=true); decide('u')"); await pg.wait_for_timeout(300); await pg.evaluate('CINE && endCine()'); await pg.evaluate("setView('call')"); await pg.wait_for_timeout(700)
                    if stage == 'bc':
                        await pg.evaluate("broadcast('tlm')"); await pg.wait_for_timeout(700)
                    await pg.evaluate("S.calls.forEach(c=>c.wait=Math.min(c.wait,5)); renderQueue(); renderCall()"); await pg.wait_for_timeout(200)
                    bad = await pg.evaluate(CHECK, name)
                    if bad:
                        key=f'{waiting}-{stage}'; res[key]=bad
                        await pg.screenshot(path=f'/tmp/lay-{name}-{key}.png')
                    await pg.evaluate("$('#bcBox').classList.add('hidden'); radioClear(); A.bcOn=false; S.incs.slice().forEach(i=>{ try{ i.units.forEach(u=>{u.x=i.x;u.y=i.y;u.path=[];}); closeInc(i);}catch(e){} }); S.bcq=[]")
            n = sum(len(v) for v in res.values()); total += n
            print(name, flush=True); print(name, 'OK' if not res else json.dumps(res, ensure_ascii=False)[:900], errs[:2])
            await ctx.close()
        await b.close()
    print('TOTAL PROBLEMS', total)
asyncio.run(main())
