'use client';

import { useEffect, useMemo, useState } from 'react';

const demoRows = [
  { id:'cmp_1', campaign:'VAPORTEK ES', country:'ES', spend:184.20, revenue:438.00, leads:32, bid:8.50, budget:250, roi30:128, roi60:116, trend:-18 },
  { id:'cmp_2', campaign:'SpeedSteam PT', country:'PT', spend:146.90, revenue:284.00, leads:21, bid:7.80, budget:220, roi30:74, roi60:92, trend:-31 },
  { id:'cmp_3', campaign:'VacuFresh PL', country:'PL', spend:211.40, revenue:512.00, leads:39, bid:6.90, budget:300, roi30:142, roi60:133, trend:12 },
  { id:'cmp_4', campaign:'SliceMaster DE', country:'DE', spend:159.30, revenue:235.00, leads:17, bid:9.20, budget:220, roi30:41, roi60:58, trend:-39 },
];

function roi(revenue, spend){ return spend ? ((revenue-spend)/spend)*100 : 0; }
function money(v){ return new Intl.NumberFormat('it-IT',{style:'currency',currency:'EUR'}).format(v); }

export default function Home(){
  const [haircut,setHaircut] = useState(30);
  const [target,setTarget] = useState(100);
  const [rows,setRows] = useState(demoRows);
  const [mode,setMode] = useState('SAFE MODE');
  const [lastSync,setLastSync] = useState('Demo locale');
  const [selected,setSelected] = useState(null);

  useEffect(()=>{
    fetch('/api/dashboard').then(r=>r.ok?r.json():null).then(d=>{
      if(d?.rows?.length){ setRows(d.rows); setLastSync(d.source || 'API'); }
    }).catch(()=>{});
  },[]);

  const totals = useMemo(()=>{
    const spend=rows.reduce((a,r)=>a+r.spend,0);
    const revenue=rows.reduce((a,r)=>a+r.revenue,0);
    const adjusted=revenue*(1-haircut/100);
    const leads=rows.reduce((a,r)=>a+r.leads,0);
    return {spend,revenue,adjusted,leads,roi:roi(adjusted,spend),cpa:leads?spend/leads:0};
  },[rows,haircut]);

  function recommendation(r){
    const adjRoi=roi(r.revenue*(1-haircut/100),r.spend);
    if(r.roi30 < 35 || r.trend < -30) return {action:'LOWER BID', delta:'-15%', cls:'danger', reason:'ROI marginale in deterioramento'};
    if(adjRoi >= target && r.roi30 >= target) return {action:'RAISE BID', delta:'+8%', cls:'good', reason:'ROI sopra target e marginale solido'};
    return {action:'KEEP', delta:'0%', cls:'neutral', reason:'Attendere più dati prima di intervenire'};
  }

  async function syncNow(){
    setLastSync('Sincronizzazione…');
    try{
      const res=await fetch('/api/dashboard',{cache:'no-store'});
      const d=await res.json();
      if(d.rows?.length) setRows(d.rows);
      setLastSync(new Date().toLocaleTimeString('it-IT'));
    }catch{ setLastSync('Errore sync'); }
  }

  return <main className="shell">
    <aside className="sidebar">
      <div className="brand">METABID<span>COPILOT</span></div>
      <nav><button className="active">Dashboard</button><button>Campagne</button><button>Decisioni</button><button>Connessioni</button><button>Impostazioni</button></nav>
      <div className="sideBottom"><div className="statusDot"></div><div><b>{mode}</b><small>Nessuna modifica automatica</small></div></div>
    </aside>

    <section className="content">
      <header><div><p className="eyebrow">AFFILIATE PERFORMANCE CONTROL</p><h1>Dashboard ROI intraday</h1><p className="muted">Bid first · Budget second · Profit lock attivo</p></div><div className="headerActions"><span className="sync">Ultimo sync: {lastSync}</span><button onClick={syncNow} className="primary">Sincronizza ora</button></div></header>

      <div className="kpis">
        <Kpi title="SPEND META" value={money(totals.spend)} sub="oggi" />
        <Kpi title="REVENUE TM" value={money(totals.revenue)} sub="lordo" />
        <Kpi title="REVENUE ADJUSTED" value={money(totals.adjusted)} sub={`haircut ${haircut}%`} />
        <Kpi title="ROI ADJUSTED" value={`${totals.roi.toFixed(1)}%`} sub={`target ${target}%`} hot={totals.roi>=target}/>
        <Kpi title="LEADS / CPA" value={`${totals.leads} · ${money(totals.cpa)}`} sub="lead reali" />
      </div>

      <div className="toolbar card">
        <div><label>Haircut revenue</label><input type="range" min="0" max="50" value={haircut} onChange={e=>setHaircut(+e.target.value)}/><b>{haircut}%</b></div>
        <div><label>ROI target</label><input type="number" value={target} onChange={e=>setTarget(+e.target.value)}/><b>%</b></div>
        <div className="safe"><span>CONTROLLO</span><strong>{mode}</strong></div>
      </div>

      <div className="sectionTitle"><div><h2>Campagne attive</h2><p className="muted">Decisioni basate su ROI marginale 30m/1h + trend</p></div><span>{rows.length} campagne</span></div>

      <div className="table card">
        <div className="tr th"><span>Campagna</span><span>Spend</span><span>Revenue adj.</span><span>ROI adj.</span><span>ROI 30m</span><span>Trend</span><span>Bid</span><span>Copilot</span></div>
        {rows.map(r=>{ const rec=recommendation(r); const adj=r.revenue*(1-haircut/100); const rr=roi(adj,r.spend); return <div className="tr" key={r.id} onClick={()=>setSelected(r)}>
          <span><b>{r.campaign}</b><small>{r.country} · {r.leads} lead</small></span>
          <span>{money(r.spend)}</span><span>{money(adj)}</span><span className={rr>=target?'positive':''}>{rr.toFixed(0)}%</span><span>{r.roi30}%</span><span className={r.trend<0?'negative':'positive'}>{r.trend>0?'+':''}{r.trend}%</span><span>{money(r.bid)}</span><span><button className={`pill ${rec.cls}`}>{rec.action} {rec.delta}</button></span>
        </div>})}
      </div>

      <div className="grid2">
        <div className="card panel"><h3>Regole controller</h3><Rule a="ROI marginale collassa" b="Riduci bid 10–20%"/><Rule a="ROI ≥ target + volume" b="Aumenta bid 5–10%"/><Rule a="Budget limitante + ROI forte" b="Aumenta budget"/><Rule a="Dopo modifica" b="Cooldown 60–90 min"/></div>
        <div className="card panel"><h3>Integrazioni</h3><div className="integration"><span>Meta Marketing API</span><b className="pending">DA CONFIGURARE</b></div><div className="integration"><span>TrafficManager</span><b className="pending">DA CONFIGURARE</b></div><div className="integration"><span>Matching</span><code>subid2 → adset_id</code></div><p className="muted mini">Le credenziali vanno salvate come Environment Variables su Vercel, mai nel browser.</p></div>
      </div>
    </section>

    {selected && <div className="modalBackdrop" onClick={()=>setSelected(null)}><div className="modal card" onClick={e=>e.stopPropagation()}><button className="close" onClick={()=>setSelected(null)}>×</button><p className="eyebrow">COPILOT DECISION</p><h2>{selected.campaign}</h2><p>{recommendation(selected).reason}</p><div className="decisionBox"><strong>{recommendation(selected).action}</strong><span>{recommendation(selected).delta}</span></div><button className="primary wide" onClick={()=>alert('SAFE MODE: nessuna modifica inviata a Meta.')}>Approva simulazione</button></div></div>}
  </main>
}

function Kpi({title,value,sub,hot}){return <div className="card kpi"><small>{title}</small><strong className={hot?'positive':''}>{value}</strong><span>{sub}</span></div>}
function Rule({a,b}){return <div className="rule"><span>{a}</span><b>{b}</b></div>}
