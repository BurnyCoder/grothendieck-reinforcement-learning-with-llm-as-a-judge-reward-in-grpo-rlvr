/* Render only saved evidence. textContent prevents candidate responses becoming executable HTML. */
const $ = id => document.getElementById(id);
const number = value => value == null ? 'Pending' : typeof value === 'number' ? Number(value.toFixed(4)).toString() : value;
let snapshot;
function element(tag, text, className) { const node=document.createElement(tag); if(text!=null)node.textContent=text; if(className)node.className=className; return node; }
function choices(select, values) { const current=select.value; select.replaceChildren(...values.map(value=>{const option=element('option',value);option.value=value;return option;})); if(values.includes(current))select.value=current; }
function chart(title, points, bounded) {
  const box=element('div',null,'chart'); box.append(element('h3',title));
  if(!points.length){box.append(element('p','No recorded data.'));return box;}
  const ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 480 190');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);
  const xmin=Math.min(...points.map(p=>p[0])), xmax=Math.max(xmin+1,...points.map(p=>p[0]));
  const ymin=bounded?0:Math.min(0,...points.map(p=>p[1])), ymax=bounded?1:Math.max(.0001,...points.map(p=>p[1]));
  const sx=x=>45+(x-xmin)/(xmax-xmin)*420, sy=y=>155-(y-ymin)/(ymax-ymin)*130;
  for(let i=0;i<=4;i++){const y=ymin+(ymax-ymin)*i/4;const line=document.createElementNS(ns,'line');Object.entries({x1:45,x2:465,y1:sy(y),y2:sy(y),stroke:'#dce7e2'}).forEach(([k,v])=>line.setAttribute(k,v));svg.append(line);const text=document.createElementNS(ns,'text');text.setAttribute('x',2);text.setAttribute('y',sy(y)+4);text.setAttribute('font-size',10);text.textContent=Number(y.toFixed(3));svg.append(text);}
  const path=document.createElementNS(ns,'path');path.setAttribute('d',points.map(([x,y],i)=>`${i?'L':'M'}${sx(x)},${sy(y)}`).join(' '));path.setAttribute('stroke','#216c6f');path.setAttribute('stroke-width','2');path.setAttribute('fill','none');svg.append(path);
  for(const x of [xmin,xmax]){const label=document.createElementNS(ns,'text');label.setAttribute('x',sx(x));label.setAttribute('y',178);label.setAttribute('font-size',10);label.setAttribute('text-anchor','middle');label.textContent=x;svg.append(label);} box.append(svg);return box;
}
function renderTraining() {
  const events=snapshot.training[$('run').value]||[], last=(kind)=>events.filter(e=>e.kind===kind).at(-1);
  const batch=last('reward_batch'), metrics=last('training_metrics'), checkpoint=last('checkpoint');
  const development=Object.entries(snapshot.summaries).filter(([name])=>name.includes('dev')).at(-1)?.[1];
  const elapsed=metrics?.elapsed_seconds, tokens=metrics?.metrics?.num_tokens;
  const fields=[['Training correctness',batch?.accuracy],['Theory quality',batch?.theory],['Supported novelty',batch?.novelty],['Latest development accuracy',development?.accuracy],['Optimizer step',metrics?.step],['Latest checkpoint',checkpoint?.step],['Loss',metrics?.metrics?.loss],['KL',metrics?.metrics?.kl],['Mean completion tokens',metrics?.metrics?.['completions/mean_length']],['Tokens per second',tokens&&elapsed?tokens/elapsed:null],['Judge failures',events.filter(e=>e.kind==='judge_failure').length],['Elapsed seconds',elapsed]];
  $('metrics').replaceChildren(...fields.map(([label,value])=>{const card=element('div',null,'metric');card.append(element('small',label),element('strong',number(value)));return card;}));
  $('charts').replaceChildren(...[['Correctness','accuracy',true],['Theory quality','theory',true],['Supported novelty','novelty',true],['Loss','loss',false],['KL','kl',false]].map(([title,key,bounded])=>chart(title,events.map(e=>[e.step??e.reward_call,e[key]??e.metrics?.[key]]).filter(p=>p.every(Number.isFinite)),bounded)));
}
function renderExample(){const rows=snapshot.examples[$('example-arm').value]||[], row=rows.find(r=>r.task_id===$('example-task').value);$('response').textContent=row?JSON.stringify(row.prompt,null,2)+'\n\n'+row.response:'No evaluated outputs yet.';$('assessment').textContent=row?JSON.stringify({verification:row.verification,theory:row.theory,assessment:row.assessment},null,2):'Pending.';}
function exampleOptions(){choices($('example-task'),(snapshot.examples[$('example-arm').value]||[]).map(r=>r.task_id));renderExample();}
function render(){
  $('status').textContent=snapshot.primary.status==='pending'?'Preregistered · experiments pending':`Analysis: ${snapshot.primary.status}`;
  $('updated').textContent='Snapshot '+new Date(snapshot.generated_at).toLocaleString();
  const arms=['ordinary','prompted','correctness-seed42','theory-seed42','correctness-seed43','theory-seed43','correctness-seed44','theory-seed44','shuffled-seed42','rubric-seed42'];
  $('result-rows').replaceChildren(...[...new Set([...arms,...Object.keys(snapshot.summaries)])].map(arm=>{const row=element('tr'),s=snapshot.summaries[arm]||{};[arm,s.n,s.accuracy,s.metric,s.correctness_weighted_novelty,s.mean_response_tokens].forEach(value=>row.append(element('td',number(value))));return row;}));
  $('analysis').textContent=JSON.stringify(snapshot.primary,null,2);
  $('ood-analysis').textContent=JSON.stringify({secondary:snapshot.secondary_ood,families:snapshot.families},null,2);
  $('transfer-analysis').textContent=JSON.stringify(snapshot.transfer,null,2);
  $('development').textContent=JSON.stringify(snapshot.development||[],null,2);
  $('calibration').replaceChildren(...snapshot.calibration.map(c=>element('p',`${c.role} / ${c.variant} / ${c.split}: ${c.complete===false?'partial observed rates; ':''}ordering ${number(c.preference_accuracy)}, false-theory suppression ${number(c.false_theory_suppression)}, novelty ordering ${number(c.strata?.novelty?.preference_accuracy)} — ${c.passed?'passed':'failed'}${c.stopping_reason?' ('+c.stopping_reason+')':''}`)));
  for(const progress of snapshot.calibration_progress||[]){$('calibration').append(element('p',`${progress.role} / ${progress.variant} / ${progress.split}: ${progress.pairs_completed}/${progress.pairs_total} preference pairs; ${progress.false_cases_completed}/${progress.false_cases_total} false-theory cases completed.`));}
  choices($('run'),Object.keys(snapshot.training));choices($('example-arm'),Object.keys(snapshot.examples));renderTraining();exampleOptions();
}
async function refresh(){try{let response=await fetch('api/live',{cache:'no-store'});if(response.ok&&response.headers.get('content-type')?.includes('application/json')){$('live-status').textContent='Local live view · refreshes every 10 seconds';snapshot=await response.json();}else{response=await fetch('snapshot.json',{cache:'no-store'});snapshot=await response.json();}render();}catch(error){$('status').textContent='Evidence unavailable: '+error.message;}}
$('run').addEventListener('change',renderTraining);$('example-arm').addEventListener('change',exampleOptions);$('example-task').addEventListener('change',renderExample);refresh();setInterval(refresh,10000);
