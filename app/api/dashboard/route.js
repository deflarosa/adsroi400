import { NextResponse } from 'next/server';

const demoRows = [
  { id:'cmp_1', campaign:'VAPORTEK ES', country:'ES', spend:184.20, revenue:438.00, leads:32, bid:8.50, budget:250, roi30:128, roi60:116, trend:-18 },
  { id:'cmp_2', campaign:'SpeedSteam PT', country:'PT', spend:146.90, revenue:284.00, leads:21, bid:7.80, budget:220, roi30:74, roi60:92, trend:-31 },
  { id:'cmp_3', campaign:'VacuFresh PL', country:'PL', spend:211.40, revenue:512.00, leads:39, bid:6.90, budget:300, roi30:142, roi60:133, trend:12 },
  { id:'cmp_4', campaign:'SliceMaster DE', country:'DE', spend:159.30, revenue:235.00, leads:17, bid:9.20, budget:220, roi30:41, roi60:58, trend:-39 }
];

export async function GET(){
  const metaToken = process.env.META_ACCESS_TOKEN;
  const adAccount = process.env.META_AD_ACCOUNT_ID;
  const tmBase = process.env.TM_BASE_URL;
  const tmKey = process.env.TM_API_KEY;
  const tmUser = process.env.TM_USER_ID;

  if(!metaToken || !adAccount || !tmBase || !tmKey || !tmUser){
    return NextResponse.json({ rows: demoRows, source: 'Demo · configura Environment Variables su Vercel', live:false });
  }

  try{
    const graphVersion = process.env.META_GRAPH_VERSION || 'v24.0';
    const metaUrl = new URL(`https://graph.facebook.com/${graphVersion}/${adAccount}/insights`);
    metaUrl.searchParams.set('level','adset');
    metaUrl.searchParams.set('date_preset','today');
    metaUrl.searchParams.set('fields','campaign_id,campaign_name,adset_id,adset_name,spend,actions');
    metaUrl.searchParams.set('limit','200');
    metaUrl.searchParams.set('access_token',metaToken);

    const metaRes = await fetch(metaUrl,{cache:'no-store'});
    if(!metaRes.ok) throw new Error(`Meta ${metaRes.status}`);
    const meta = await metaRes.json();

    const tmUrl = `${tmBase.replace(/\/$/,'')}/api/v1/offerConversions/today/now/?fields=id,status,timestamp,clickid,payout,offer_id,offer_name,cc,subid,subid2,subid3,subid4,utm_campaign`;
    const tmRes = await fetch(tmUrl,{headers:{'x-api-key':tmKey,'x-user-id':tmUser},cache:'no-store'});
    if(!tmRes.ok) throw new Error(`TrafficManager ${tmRes.status}`);
    const tm = await tmRes.json();
    const conversions = Array.isArray(tm) ? tm : (tm.data || tm.rows || []);

    const revenueByAdset = new Map();
    const leadsByAdset = new Map();
    for(const c of conversions){
      const key = String(c.subid2 || c.utm_campaign || '');
      if(!key) continue;
      const status = String(c.status || '').toLowerCase();
      if(status === 'canceled' || status === 'cancelled') continue;
      revenueByAdset.set(key,(revenueByAdset.get(key)||0)+Number(c.payout||0));
      leadsByAdset.set(key,(leadsByAdset.get(key)||0)+1);
    }

    const rows = (meta.data || []).map((r,i)=>{
      const key = String(r.adset_id || '');
      const spend = Number(r.spend||0);
      return {
        id:key || `meta_${i}`,
        campaign:r.campaign_name || r.adset_name || 'Meta Ad Set',
        country:'—',
        spend,
        revenue:Number(revenueByAdset.get(key)||0),
        leads:Number(leadsByAdset.get(key)||0),
        bid:0,
        budget:0,
        roi30:0,
        roi60:0,
        trend:0
      };
    });

    return NextResponse.json({rows:rows.length?rows:demoRows,source:'Meta + TrafficManager LIVE',live:true});
  }catch(error){
    return NextResponse.json({rows:demoRows,source:`Fallback demo · ${error.message}`,live:false},{status:200});
  }
}
