import asyncio, sys, json
from playwright.async_api import async_playwright
BOT = r'''
async (seed) => {
  const out = {errs:[], notes:[], bcs:[], ends:0};
  cancelAnimationFrame(raf);                          // drive the clock ourselves
  const origErr = window.onerror;
  let steps = 0, lastLog = 0;
  const pickR = a => a[Math.floor(Math.random()*a.length)];
  while(S && !S.over && steps < 40000){
    steps++;
    try{
      if(CINE){ endCine(); continue; }
      tick(0.1); if(S.over) break;
      if(steps % 3 === 0) draw();
      // the bot plays
      if(!S.active && S.calls.length && Math.random() < 0.3) answer(0);
      const c = S.active;
      if(c && !c.ending){
        const r = Math.random();
        if(r < 0.25){ const q = tabList(c).list[0]; if(q) ask(q.id); }
        else if(r < 0.32 && c.t0 === undefined){
          const sc = c.sc, sent = c.inc && S.incs.includes(c.inc);
          if(sent){ if(Math.random()<0.5) decide('end'); }
          else if(sc.tgt==='ref') decide('ref'); else if(sc.tgt==='x') decide('x'); else if(sc.tgt==='110') decide('110');
          else if(Array.isArray(sc.tgt)){ sc.tgt.forEach(k => c.ext[k]=true); decide(Math.random()<0.5 ? 't' : 'endno'); }
          else if(c.grp && c.grp.inc && Math.random()<0.6) decide('dup');
          else { const free = S.units.filter(u => u.state==='free'); free.slice(0, 1 + Math.floor(Math.random()*2)).forEach(u => u.sel = true); (sc.ext||[]).forEach(k => c.ext[k]=true); decide(sc.pri===1 ? 'u' : 'r'); }
        }
      }
      if(Math.random() < 0.002 && S.incs.length){ const inc = pickR(S.incs); const free = S.units.filter(u => u.state==='free'); if(free.length){ free[0].sel = true; reinforce(inc, [free[0]], true); } }
      if(Math.random() < 0.002){ const u = S.units.find(u => canRelease(u)); if(u) releaseUnit(u); }
      if(Math.random() < 0.003 && CREW_INC){ document.querySelector('#crewReq button') && document.querySelector('#crewReq button').click(); }
      // invariants
      for(const u of S.units){
        if((u.state==='enroute' || u.state==='scene') && (!u.inc || !S.incs.includes(u.inc))) out.notes.push('unit '+u.cs+' '+u.state+' without live incident at '+S.t.toFixed(1));
        if(u.state==='free' && u.inc) out.notes.push('free unit with inc '+u.cs);
        if(!isFinite(u.x) || !isFinite(u.y)) out.notes.push('NaN pos '+u.cs);
      }
      for(const inc of S.incs){ if(!inc.units.length) out.notes.push('incident without units '+inc.sc.t); if(inc.arrivedAt!=null && inc.sceneAt==null && S.t - inc.arrivedAt > 60) out.notes.push('stuck at scene '+inc.sc.t); }
      if(RQ.length > 400) out.notes.push('radio queue long '+RQ.length);
      if(S.t - lastLog > 30){ lastLog = S.t; }
      if(A.bcOn && !out._bcSeen){ out._bcSeen = 1; }
    }catch(e){ out.errs.push(String(e && e.stack || e).slice(0,300)); if(out.errs.length > 10) break; }
    if(steps % 200 === 0) await new Promise(r => setTimeout(r, 0));     // let promises (radio queue) move
  }
  // after the clock runs out, wait for the end hold
  let w = 0; while(S && !S.over && w < 400){ try{ tick(0.1); }catch(e){ out.errs.push(String(e).slice(0,200)); break; } await new Promise(r => setTimeout(r, 50)); w++; }
  out.over = S.over; out.t = S.t; out.rec = S.rec.length; out.avg = avg(); out.steps = steps;
  out.notes = [...new Set(out.notes)].slice(0, 30);
  out.bcLog = S.log ? undefined : undefined;
  return out;
}
'''
async def main():
    mobile = len(sys.argv) > 1 and sys.argv[1]=='m'
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for k in range(runs):
            ctx=await b.new_context(**(p.devices['iPhone 13'] if mobile else {'viewport':{'width':1400,'height':860}}))
            pg=await ctx.new_page(); errs=[]
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate(f"localStorage.setItem('moked.lvlSel','{k%4}'); localStorage.setItem('moked.units', JSON.stringify({json.dumps(['401','11','402','403','404','411','יס״מ','תנועה','כלבן','בילוש','מג״ב','מסוק'] if k%2 else ['401','11','402','403','404'])}))")
            await pg.reload(); await pg.wait_for_timeout(800)
            await pg.click('#btnStart'); await pg.wait_for_timeout(1500)
            r = await pg.evaluate(BOT, k)
            print('run',k,'mobile' if mobile else 'desk', json.dumps(r, ensure_ascii=False)[:1500]); print('pageerrors', errs[:5])
            await ctx.close()
        await b.close()
asyncio.run(main())
