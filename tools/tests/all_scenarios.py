import asyncio, json
from playwright.async_api import async_playwright
JS = r'''
async () => {
  const out = []; cancelAnimationFrame(raf);
  const logs = []; const _log = log; log = function(k, who, txt){ logs.push(String(txt)); return _log.apply(this, arguments); };
  for(const sc of SCEN){
    const p = [];
    if(sc.pri < 3 && !sc.tgt && !sc.good) p.push('dispatch scenario without good text');
    try{
      S.calls = []; S.active = null; S.incs.slice().forEach(i => { i.units.forEach(u => { u.state='free'; u.inc=null; u.path=[]; }); }); S.incs = [];
      S.units.forEach(u => { if(u.state==='gone') u.state='free'; });
      S.t = 30; S.endHold = 0; S.bcq = []; S.echoQ = []; S.deck = [sc]; spawnCall(); answer(0); const c = S.active;
      for(let k=0;k<300 && c.q.length;k++){ tick(0.1); }
      for(let n=0;n<20;n++){ const q = openQuestions(c)[0]; if(!q) break; ask(q.id); for(let k=0;k<200 && c.q.length;k++) tick(0.1); }
      const t = sc.tgt; const recBefore = S.rec.length; logs.length = 0;
      if(t==='ref') decide('ref'); else if(t==='x') decide('x'); else if(t==='110') decide('110');
      else if(Array.isArray(t)){ t.forEach(k => c.ext[k]=true); decide('endno'); }
      else { S.units.filter(u => u.state==='free' && !u.air).slice(0, sc.need||1).forEach(u => u.sel=true); (sc.ext||[]).forEach(k => c.ext[k]=true); decide(sc.pri===1 ? 'u' : 'r'); }
      if(CINE) endCine();
      for(let k=0;k<6000 && (S.active===c || S.incs.length); k++){ tick(0.1); if(CINE) endCine(); if(CREW_INC){ const b=document.querySelector('#crewReq button'); if(b) b.click(); } }
      const recs = S.rec.slice(recBefore);
      if(!recs.length) p.push('no score record');
      recs.forEach(r => { const txt = JSON.stringify(r); if(/undefined|NaN/.test(txt)) p.push('bad record: '+(txt.match(/.{60}(undefined|NaN|null).{20}/)||[''])[0]); if(r.score < 70) p.push('correct handling scored '+r.score+' '+(r.note||'').slice(0,120)); });
      logs.forEach(l => { if(/undefined|NaN/.test(l)) p.push('log text: '+l.slice(0,120)); });
      if(S.incs.length) p.push('incident did not close');
    }catch(e){ p.push('ERROR '+String(e.stack||e).slice(0,200)); }
    if(p.length) out.push(sc.t+' → '+p.join(' | '));
  }
  return out;
}
'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(700)
        await pg.evaluate("localStorage.setItem('moked.units', JSON.stringify(['401','11','402','403','404','411','412','יס״מ']))"); await pg.reload(); await pg.wait_for_timeout(600)
        await pg.click('#btnStart'); await pg.wait_for_timeout(1500); await pg.evaluate('CINE && endCine()')
        r = await pg.evaluate(JS); print('\n'.join(r) or 'ALL OK'); print('pageerrors', errs[:5])
asyncio.run(main())
