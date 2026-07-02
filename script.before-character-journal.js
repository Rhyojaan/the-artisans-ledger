
const R={"Beetle Scuttle":["Breach","Increase Armor","Protection","Vitality"],"Blessed Thistle":["Restore Stamina","Increase Weapon Power","Ravage Health","Speed"],"Blue Entoloma":["Ravage Magicka","Cowardice","Restore Health","Invisible"],"Bugloss":["Increase Spell Resist","Restore Health","Cowardice","Restore Magicka"],"Butterfly Wing":["Restore Health","Uncertainty","Lingering Health","Vitality"],"Chaurus Egg":["Timidity","Ravage Magicka","Restore Stamina","Detection"],"Clam Gall":["Increase Spell Resist","Hindrance","Vulnerability","Defile"],"Columbine":["Restore Health","Restore Magicka","Restore Stamina","Unstoppable"],"Corn Flower":["Restore Magicka","Increase Spell Power","Ravage Health","Detection"],"Crimson Nirnroot":["Timidity","Critical","Gradual Ravage Health","Restore Health"],"Dragon's Bile":["Heroism","Vulnerability","Invisible","Vitality"],"Dragon's Blood":["Lingering Health","Restore Stamina","Heroism","Defile"],"Dragon Rheum":["Restore Magicka","Heroism","Enervation","Speed"],"Dragonthorn":["Increase Weapon Power","Restore Stamina","Fracture","Critical"],"Emetic Russula":["Ravage Health","Ravage Magicka","Ravage Stamina","Entrapment"],"Fleshfly Larva":["Ravage Stamina","Gradual Ravage Health","Vulnerability","Vitality"],"Imp Stool":["Maim","Ravage Stamina","Increase Armor","Enervation"],"Lady's Smock":["Increase Spell Power","Restore Magicka","Breach","Critical"],"Luminous Russula":["Ravage Stamina","Maim","Restore Health","Hindrance"],"Mountain Flower":["Increase Armor","Restore Health","Maim","Restore Stamina"],"Mudcrab Chitin":["Increase Spell Resist","Protection","Increase Armor","Defile"],"Namira's Rot":["Critical","Speed","Invisible","Unstoppable"],"Nightshade":["Ravage Health","Gradual Ravage Health","Protection","Defile"],"Nirnroot":["Ravage Health","Uncertainty","Enervation","Invisible"],"Powdered Mother of Pearl":["Lingering Health","Speed","Vitality","Protection"],"Scrib Jelly":["Ravage Magicka","Vulnerability","Speed","Lingering Health"],"Spider Egg":["Hindrance","Invisible","Lingering Health","Defile"],"Stinkhorn":["Fracture","Ravage Health","Increase Weapon Power","Ravage Stamina"],"Torchbug Thorax":["Fracture","Enervation","Detection","Vitality"],"Vile Coagulant":["Timidity","Ravage Health","Restore Magicka","Protection"],"Violet Coprinus":["Breach","Ravage Health","Increase Spell Power","Ravage Magicka"],"Water Hyacinth":["Restore Health","Critical","Weapon Critical","Entrapment"],"White Cap":["Cowardice","Ravage Magicka","Increase Spell Resist","Detection"],"Wormwood":["Critical","Hindrance","Detection","Unstoppable"]};
const POTION_WATERS=["Natural Water","Clear Water","Pristine Water","Cleansed Water","Filtered Water","Purified Water","Cloud Mist","Star Dew","Lorkhan's Tears"];
const POISON_SOLVENTS=["Grease","Ichor","Slime","Gall","Terebinthine","Pitch-Bile","Tarblack","Night-Oil","Alkahest"];
const SAVE_KEY="TheAlchemistArchive_v1";let archive=loadArchive(),inventoryOnly=false,best=null,selectedEffects=[],history=JSON.parse(localStorage.TheAlchemistHistory_v1||"[]");
function initSolvents(){let s={};POTION_WATERS.concat(POISON_SOLVENTS).forEach(x=>s[x]={qty:0,reserve:20});return s}
function ensureProfileShape(){let p=profile();if(!p)return;if(!p.solvents)p.solvents=initSolvents();POTION_WATERS.concat(POISON_SOLVENTS).forEach(x=>{if(!p.solvents[x])p.solvents[x]={qty:0,reserve:20}});if(!p.favoriteRecipes)p.favoriteRecipes=[]}
function solventData(){ensureProfileShape();return profile().solvents}
function newProfile(name){let d={};for(const r in R)d[r]={learned:[false,false,false,false],qty:0,fav:false,reserve:20};return{id:"p_"+Date.now(),name:name||"Adventurer",created:new Date().toISOString(),lastOpen:new Date().toISOString(),data:d,solvents:initSolvents(),favoriteRecipes:[],session:{crafts:0,traits:0,complete:0},settings:{greeting:"normal"}}}
function loadArchive(){try{let a=JSON.parse(localStorage.getItem(SAVE_KEY));if(a&&a.profiles&&a.profiles.length)return a}catch(e){}return{version:"5.4",activeProfile:null,profiles:[],created:new Date().toISOString(),lastSaved:null}}
function profile(){return archive.profiles.find(p=>p.id===archive.activeProfile)}function data(){return profile().data}function session(){return profile().session}
function save(){archive.lastSaved=new Date().toISOString();let p=profile();if(p)p.lastOpen=new Date().toISOString();localStorage.setItem(SAVE_KEY,JSON.stringify(archive));render()}
function createFirstProfile(){let name=(profileName.value||"Adventurer").trim();let p=newProfile(name);archive.profiles.push(p);archive.activeProfile=p.id;save()}
function addProfile(){let name=(document.getElementById("newProfileName").value||"New Character").trim();let p=newProfile(name);archive.profiles.push(p);archive.activeProfile=p.id;document.getElementById("newProfileName").value="";save()}
function switchProfile(id){archive.activeProfile=id;save()}function renameActiveProfile(){let p=profile();let box=document.getElementById("renameProfileName");let name=(box.value||"").trim();if(!name){alert("Enter a new archive name first.");return}p.name=name;box.value="";save()}
function deleteActiveProfile(){if(archive.profiles.length<=1){alert("Aldren must keep at least one archive.");return}let p=profile();if(!confirm("Delete the archive for "+p.name+"?"))return;archive.profiles=archive.profiles.filter(x=>x.id!==p.id);archive.activeProfile=archive.profiles[0].id;save()}
function renderProfiles(){
 let box=document.getElementById("profileButtons");
 let current=document.getElementById("currentArchiveBox");
 let p=profile();
 if(current&&p)current.innerHTML=`<b>${p.name}</b><br><span class=small>Aldren is currently keeping this archive open.</span>`;
 if(!box)return;
 box.innerHTML=archive.profiles.map(p=>`<button class="${p.id===archive.activeProfile?'good':'secondary'}" onclick="switchProfile('${p.id}')">${p.name}</button>`).join("");
}
function ensureReady(){if(!archive.profiles.length){setup.style.display="block";app.style.display="none";return false}setup.style.display="none";app.style.display="block";return true}
function snapshot(){return JSON.stringify({archive})}function restore(s){archive=JSON.parse(s).archive}
function common(c){let m={};c.forEach(r=>[...new Set(R[r])].forEach(t=>m[t]=(m[t]||0)+1));return Object.keys(m).filter(t=>m[t]>1)}
function combos(){let a=Object.keys(R),o=[];for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){o.push([a[i],a[j]]);for(let k=j+1;k<a.length;k++)o.push([a[i],a[j],a[k]])}return o}const ALL=combos();
function scoreCombo(c,state=data(),invOnly=inventoryOnly){if(invOnly&&c.some(r=>Number(state[r].qty||0)<1))return null;let sh=common(c),disc=[];c.forEach(r=>R[r].forEach((t,i)=>{if(sh.includes(t)&&!state[r].learned[i])disc.push([r,t,i])}));if(!disc.length)return null;let ownedBonus=c.reduce((a,r)=>a+Math.min(Number(state[r].qty||0),3),0)/10;let favBonus=c.reduce((a,r)=>a+(state[r].fav?.15:0),0);return{c,sh,disc,score:disc.length+ownedBonus+favBonus}}
function ranked(state=data(),invOnly=inventoryOnly){return ALL.map(c=>scoreCombo(c,state,invOnly)).filter(Boolean).sort((a,b)=>b.score-a.score)}
function cloneState(x){return JSON.parse(JSON.stringify(x))}function applyCraftToState(state,craft){craft.disc.forEach(d=>state[d[0]].learned[d[2]]=true);craft.c.forEach(r=>state[r].qty=Math.max(0,Number(state[r].qty||0)-1))}
function countKnown(){return Object.values(data()).reduce((a,x)=>a+x.learned.filter(Boolean).length,0)}function countComplete(){return Object.keys(R).filter(r=>data()[r].learned.filter(Boolean).length==4).length}function esc(s){return s.replaceAll("'","\\'")}function setQty(r,n){data()[r].qty=Math.max(0,Number(data()[r].qty||0)+n);save()}
function chooseGreeting(name,known,total,low){
 let pct=Math.round(known/total*100),hour=new Date().getHours(),o=[];
 if(known===0){
  o.push(`Welcome, ${name}. The archives stand ready. Together, we shall begin recording Tamriel's alchemical secrets.`);
  o.push(`Welcome, ${name}. I have prepared a fresh ledger. The first discovery awaits.`);
  o.push(`The workshop is quiet, ${name}. A fine time to begin our archive.`);
 }
 if(pct>=100){
  o.push(`Welcome back, ${name}. Every known reagent has yielded its secrets.`);
  o.push(`There is no unfinished report today, ${name}. The archives stand complete.`);
 }
 if(low>0){
  o.push(`Welcome back, ${name}. Before today's research begins, ${low} reagent reserve${low>1?"s have":" has"} fallen below your preferred limit.`);
  o.push(`${name}, I have reviewed your satchel. ${low} reserve${low>1?"s need":" needs"} attention.`);
  o.push(`A brief note before we begin: your supplies are running light in ${low} place${low>1?"s":""}.`);
 }
 if(pct>0&&pct<50){
  o.push(`Welcome back, ${name}. The archives grow stronger with every discovery.`);
  o.push(`Good to see you, ${name}. Several mysteries remain, but our records are improving.`);
  o.push(`The early work is often the most important. Let us continue.`);
 }
 if(pct>=50&&pct<90){
  o.push(`Welcome back, ${name}. Few alchemists keep records this carefully. Let us continue.`);
  o.push(`Your archive has passed the halfway mark. Aldren approves of this diligence.`);
  o.push(`The shelves grow heavy with knowledge, ${name}. There is still work to do.`);
 }
 if(pct>=90&&pct<100){
  o.push(`Welcome back, ${name}. Only a handful of mysteries remain.`);
  o.push(`We are close now, ${name}. The remaining secrets will not hide forever.`);
  o.push(`The archive is nearly complete. Let us finish with care.`);
 }
 if(hour<5)o.push(`A late hour for research, ${name}. Still, the workshop is ready.`);
 else if(hour<12)o.push(`Good morning, ${name}. The reagents are sorted and today's notes are ready.`);
 else if(hour<18)o.push(`Good afternoon, ${name}. Aldren has prepared your report.`);
 else o.push(`Good evening, ${name}. The workshop lanterns are lit.`);
 o.push(`Good to see you, ${name}. Aldren the Archivist has prepared your report.`);
 o.push(`The workshop is ready. Let us see what the archives require today.`);
 o.push(`Welcome back, ${name}. Your records have been preserved.`);
 return o[Math.floor(Math.random()*o.length)]
}
function gatherAdvice(){let theoretical=ALL.map(c=>scoreCombo(c,data(),false)).filter(Boolean).sort((a,b)=>b.score-a.score)[0];if(!theoretical)return "The archives may be complete, or no useful experiment remains.";let missing=theoretical.c.filter(r=>Number(data()[r].qty||0)<1);return `Aldren found no useful discovery you can craft with your current reagents.<br><br><span class=small>To pursue the strongest next experiment, gather:</span><br>${missing.map(x=>`<span class=pill>${x}</span>`).join("")}`;}
function buildPlan(){let state=cloneState(data()),steps=[],safety=0;while(safety++<80){let r=ranked(state,inventoryOnly)[0];if(!r)break;steps.push(r);applyCraftToState(state,r)}planSummary.innerHTML=steps.length?`Plan found: <b>${steps.length}</b> experiments. Estimated new traits: <b>${steps.reduce((a,s)=>a+s.disc.length,0)}</b>.`:"No useful plan found. Try turning inventory-only OFF.";planList.innerHTML=steps.slice(0,30).map((s,i)=>`<div class=planStep><b>Experiment #${i+1}</b><br>${s.c.join(" + ")}<br><span class=small>${s.disc.length} discoveries: ${s.disc.map(d=>d[1]).join(", ")}</span></div>`).join("")}
function showTab(id,btn){document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));btn.classList.add('active');renderBuilder()}

function renderFieldNote(allKnown,total,complete,owned,low){
 let box=document.getElementById("fieldNote");if(!box)return;
 let pct=Math.round(allKnown/total*100), notes=[];
 if(allKnown===0)notes.push("The first entry in any archive is the most important. Begin with what you can craft.");
 if(pct>=100)notes.push("Every known reagent has yielded its secrets. The archive stands complete.");
 if(pct>=75&&pct<100)notes.push("The archive is nearing completion. A careful final pass will serve us well.");
 if(complete>0)notes.push(`${complete} reagent${complete===1?" has":"s have"} been fully documented.`);
 if(low>0)notes.push(`${low} supply reserve${low===1?" is":"s are"} below your preferred limit. Review the Inventory Report when convenient.`);
 if(owned>0)notes.push("Your satchel contains enough material for Aldren to continue searching for useful experiments.");
 notes.push("A clean archive is built one accurate entry at a time.");
 box.textContent=notes[Math.floor(Math.random()*notes.length)];
}
function render(){if(!ensureReady())return;ensureProfileShape();renderProfiles();let d=data(),allKnown=0,complete=0,owned=0,total=Object.keys(R).length*4,low=0;for(const r in R){let k=d[r].learned.filter(Boolean).length;allKnown+=k;if(k==4)complete++;owned+=Number(d[r].qty||0);if(Number(d[r].qty||0)>0&&Number(d[r].qty||0)<Number(d[r].reserve||20))low++}let pc=Math.round(allKnown/total*100),ranks=ranked();best=ranks[0]||null;renderFieldNote(allKnown,total,complete,owned,low);traitStat.textContent=allKnown+"/"+total;ingStat.textContent=complete+"/"+Object.keys(R).length;ownedStat.textContent=owned;craftStat.textContent=ranks.length;pct.textContent=pc+"%";fill.style.width=pc+"%";remainingText.textContent=(total-allKnown)+" traits remain undocumented.";invMode.textContent=inventoryOnly?"ON":"OFF";if(document.getElementById("invMode2"))invMode2.textContent=inventoryOnly?"ON":"OFF";let p=profile();welcomeLine.textContent="Welcome back, "+p.name+".";greetingBox.textContent=chooseGreeting(p.name,allKnown,total,low);if(document.getElementById("lastSaved"))lastSaved.textContent=archive.lastSaved?"Archive updated: "+new Date(archive.lastSaved).toLocaleString():"";advisorText.innerHTML=best?`Your most useful craftable experiment can reveal <mark>${best.disc.length}</mark> new traits.<br><br><b>${best.c.join(" + ")}</b><br><br><span class=small>Why this recipe? It uses reagents you own and reveals the most new traits Aldren can find right now.</span><br><span class=small>Shared effects: ${best.sh.join(", ")}</span><br>${best.disc.map(d=>`<span class=pill>${d[0]}: ${d[1]}</span>`).join("")}`:gatherAdvice();nextFive.innerHTML=ranks.slice(0,5).map((x,i)=>`<div class=pill><b>#${i+1}</b> ${x.c.join(" + ")} — ${x.disc.length} discoveries</div>`).join("")||"No craftable discoveries found.";renderInventoryAlert();renderIngredients();renderSolvents();renderBuilder();renderSession(allKnown,complete,total);renderVerification()}

function renderInventoryAlert(){
 let box=document.getElementById("aldrenInventoryAlert");
 if(!box)return;
 let d=data(), lows=[];
 for(const r in R){
  let qty=Number(d[r].qty||0), reserve=Number(d[r].reserve||20);
  if(qty>0 && qty<reserve)lows.push({name:r,qty,reserve,fav:d[r].fav});
 }
 let s=solventData();
 POTION_WATERS.concat(POISON_SOLVENTS).forEach(x=>{
  let qty=Number(s[x].qty||0), reserve=Number(s[x].reserve||20);
  if(qty>0 && qty<reserve)lows.push({name:x,qty,reserve,fav:false});
 });
 if(!lows.length){
  box.innerHTML="Your reagent shelves are well stocked. Nothing has fallen below its preferred reserve.";
  return;
 }
 lows.sort((a,b)=>(b.fav-a.fav)||(a.qty-a.reserve)-(b.qty-b.reserve)||a.name.localeCompare(b.name));
 let shown=lows.slice(0,8);
 box.innerHTML=`I've noticed ${lows.length} reagent reserve${lows.length>1?"s have":" has"} fallen below your preferred limit.<br>`+
 shown.map(x=>`<span class=pill>${x.fav?"⭐ ":""}${x.name}: ${x.qty}/${x.reserve}</span>`).join("")+
 (lows.length>8?`<br><span class=small>${lows.length-8} more below reserve.</span>`:"");
}
function renderIngredients(){let d=data(),q=(document.getElementById("search")?.value||"").toLowerCase(),f=(document.getElementById("filter")?.value||"all"),html="";for(const r of Object.keys(R).sort((a,b)=>(d[b].fav-d[a].fav)||a.localeCompare(b))){let k=d[r].learned.filter(Boolean).length,hay=(r+" "+R[r].join(" ")).toLowerCase();if(q&&!hay.includes(q))continue;if(f=="favorites"&&!d[r].fav)continue;if(f=="complete"&&k<4)continue;if(f=="incomplete"&&k==4)continue;if(f=="owned"&&Number(d[r].qty||0)<1)continue;if(f=="low"&&!(Number(d[r].qty||0)>0&&Number(d[r].qty||0)<Number(d[r].reserve||20)))continue;let cls=k==4?"done":k>0?"partial":"none";if(d[r].fav)cls+=" fav";let low=(Number(d[r].qty||0)>0&&Number(d[r].qty||0)<Number(d[r].reserve||20));html+=`<div class="card ${cls}"><div class=row><h3>${d[r].fav?"⭐ ":""}${r}</h3><span class=badge>${k}/4</span></div><div class=row><span class=small>Owned</span><input class=qty type=number min=0 value="${d[r].qty||0}" onchange="data()['${esc(r)}'].qty=this.value;save()"></div><div class=qtyBtns><button onclick="setQty('${esc(r)}',100)">+100</button><button onclick="setQty('${esc(r)}',10)">+10</button><button onclick="setQty('${esc(r)}',1)">+1</button><button onclick="setQty('${esc(r)}',-1)">-1</button><button onclick="setQty('${esc(r)}',-10)">-10</button><button onclick="setQty('${esc(r)}',-100)">-100</button><button onclick="data()['${esc(r)}'].fav=!data()['${esc(r)}'].fav;save()">⭐</button></div><div class=row><span class=small>Reserve</span><input class=qty type=number min=0 value="${d[r].reserve||20}" onchange="data()['${esc(r)}'].reserve=this.value;save()"></div>`;R[r].forEach((t,i)=>html+=`<label class=trait><input type=checkbox ${d[r].learned[i]?"checked":""} onchange="data()['${esc(r)}'].learned[${i}]=this.checked;save()"> ${t}</label>`);html+="</div>"}if(document.getElementById("list"))list.innerHTML=html}

function setSolventQty(name,n){let s=solventData();s[name].qty=Math.max(0,Number(s[name].qty||0)+n);save()}
function renderSolvents(){
 let box=document.getElementById("solventList");if(!box)return;
 let s=solventData();
 function card(name,type){
  let low=Number(s[name].qty||0)>0&&Number(s[name].qty||0)<Number(s[name].reserve||20);
  return `<div class="card ${low?'partial':''}"><h3>${type} ${name}</h3><div class=row><span class=small>Owned</span><input class=qty type=number min=0 value="${s[name].qty||0}" onchange="solventData()['${name.replaceAll("'","\\'")}'].qty=this.value;save()"></div><div class=qtyBtns><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',100)">+100</button><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',10)">+10</button><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',1)">+1</button><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',-1)">-1</button><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',-10)">-10</button><button onclick="setSolventQty('${name.replaceAll("'","\\'")}',-100)">-100</button></div><div class=row><span class=small>Reserve</span><input class=qty type=number min=0 value="${s[name].reserve||20}" onchange="solventData()['${name.replaceAll("'","\\'")}'].reserve=this.value;save()"></div></div>`;
 }
 box.innerHTML=POTION_WATERS.map(x=>card(x,"🧪")).join("")+POISON_SOLVENTS.map(x=>card(x,"☠️")).join("");
}
function canCraftCombo(combo,solvent){
 let d=data(), s=solventData();
 return combo.every(r=>Number(d[r].qty||0)>0) && (!solvent || Number(s[solvent]?.qty||0)>0);
}
function renderBuilder(){
 let allEffects=[...new Set(Object.values(R).flat())].sort(),effectsEl=document.getElementById("effects");if(!effectsEl)return;
 let mode=document.getElementById("labMode")?.value||"potion";
 let solventSelect=document.getElementById("labSolvent");
 let solvents=mode==="potion"?POTION_WATERS:POISON_SOLVENTS;
 if(solventSelect){
  let current=solventSelect.value;
  solventSelect.innerHTML=solvents.map(x=>`<option value="${x}">${x}</option>`).join("");
  if(solvents.includes(current))solventSelect.value=current;
 }
 let solvent=solventSelect?.value||solvents[0];
 effectsEl.innerHTML=allEffects.map(e=>`<label class=effectItem><input type=checkbox ${selectedEffects.includes(e)?"checked":""} onchange="toggleEffect('${esc(e)}')"> ${e}</label>`).join("");
 let matches=ALL.filter(c=>{let sh=common(c);return selectedEffects.length&&selectedEffects.every(e=>sh.includes(e))});
 matches.sort((a,b)=>(canCraftCombo(b,solvent)-canCraftCombo(a,solvent))||common(b).length-common(a).length);
 matches=matches.slice(0,80);
 recipes.innerHTML=selectedEffects.length?matches.map(c=>{
   let ok=canCraftCombo(c,solvent);
   return `<div class=recipeLine>${ok?"✅":"Missing"} ${solvent} + ${c.join(" + ")}<br><span class=small>${ok?"Craftable now":"Add missing solvent or reagents to craft this."}</span></div>`;
 }).join("")||"Aldren found no matching recipe. Try fewer effects.":"Pick an effect above.";
}
function renderVerification(){
 let vr=document.getElementById("verifyReagents"),vt=document.getElementById("verifyTraits"),vl=document.getElementById("verificationList"),audit=document.getElementById("dataAudit");
 if(!vr||!vt||!vl)return;
 let names=Object.keys(R), issues=[];
 names.forEach(r=>{
  if(!R[r]||R[r].length!==4)issues.push(`${r}: expected 4 traits, found ${R[r]?R[r].length:0}`);
 });
 vr.textContent=names.length;
 vt.textContent=names.length*4;
 if(audit){
  audit.innerHTML=`<span class=pill>${names.length} reagents</span><span class=pill>${names.length*4} trait slots</span><span class=pill>${issues.length?issues.length+" issues found":"No structural issues found"}</span>`+
  (issues.length?`<br>${issues.map(x=>`<span class=pill>${x}</span>`).join("")}`:`<br><span class=small>Every reagent currently has exactly four trait slots.</span>`);
 }
 vl.innerHTML=names.sort().map(r=>`<div class="card"><h3>${r}</h3><ol>${R[r].map(t=>`<li>${t}</li>`).join("")}</ol></div>`).join("");
}
function toggleEffect(e){selectedEffects=selectedEffects.includes(e)?selectedEffects.filter(x=>x!==e):selectedEffects.concat(e);renderBuilder()}function markBest(){if(!best)return;history.push(snapshot());if(history.length>20)history.shift();localStorage.TheAlchemistHistory_v1=JSON.stringify(history);let bk=countKnown(),bc=countComplete();best.disc.forEach(disc=>data()[disc[0]].learned[disc[2]]=true);best.c.forEach(r=>data()[r].qty=Math.max(0,Number(data()[r].qty||0)-1));session().crafts++;session().traits+=Math.max(0,countKnown()-bk);session().complete+=Math.max(0,countComplete()-bc);save()}
function undoLast(){if(!history.length){alert("Aldren found no previous record to restore.");return}restore(history.pop());localStorage.TheAlchemistHistory_v1=JSON.stringify(history);save()}function markOwnedFirstTrait(){history.push(snapshot());for(const r in R){if(Number(data()[r].qty||0)>0)data()[r].learned[0]=true}save()}function resetSession(){profile().session={crafts:0,traits:0,complete:0};save()}function exportSave(){prompt("Copy this archive text:",JSON.stringify(archive))}function importSave(){let x=prompt("Paste archive text:");if(x){archive=JSON.parse(x);save()}}function copyCorrectionTemplate(){let t=document.getElementById("correctionTemplate");if(!t)return;t.select();document.execCommand("copy");alert("Correction template copied.")}function resetAll(){if(confirm("Reset The Alchemist archive on this browser?")){localStorage.removeItem(SAVE_KEY);localStorage.removeItem("TheAlchemistHistory_v1");location.reload()}}function togglePlayMode(){document.body.classList.toggle("playing")}render();

