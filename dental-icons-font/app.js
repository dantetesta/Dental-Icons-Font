const completeCodes=["M3","M2","M1","P2","P1","C","L","I","I","L","C","P1","P2","M1","M2","M3"];
const presets={complete:"M3 M2 M1 P2 P1 C L I | I L C P1 P2 M1 M2 M3",anterior:"C L I | I L C",posterior:"M3 M2 M1 P2 P1 | P1 P2 M1 M2 M3",hemi:"I L C P1 P2 M1 M2 M3"};
const state={arch:"upper",view:"profile",layout:"linear",size:72,spacing:4,color:"#087f6a",labels:true,context:"document"};
const $=selector=>document.querySelector(selector);const $$=selector=>[...document.querySelectorAll(selector)];
function glyphFile(arch,view,index,code){return `assets/glyphs/${arch}-${view}-${String(index+1).padStart(2,"0")}-${code.toLowerCase()}.svg`}
function parseSequence(value){const valid=new Set(["I","L","C","P1","P2","M1","M2","M3","|"]);return value.replace(/\s*\|\s*/g," | ").trim().split(/\s+/).filter(token=>valid.has(token.toUpperCase()))}
function positionFor(code,side){const half=side==="left"?completeCodes.slice(0,8):completeCodes.slice(8);const local=half.indexOf(code);return local<0?(side==="left"?0:15):(side==="left"?local:local+8)}
function visibleCode(code){return state.view==="occlusal"?code.toLowerCase():code}

function visibleHeroCode(code,view){return view==="occlusal"?code.toLowerCase():code}
const heroCollections=[
  {arch:"upper",view:"profile",label:"Superior · perfil",short:"SUP / PERFIL"},
  {arch:"upper",view:"occlusal",label:"Superior · oclusal",short:"SUP / OCLUSAL"},
  {arch:"lower",view:"profile",label:"Inferior · perfil",short:"INF / PERFIL"},
  {arch:"lower",view:"occlusal",label:"Inferior · oclusal",short:"INF / OCLUSAL"}
];
const heroItems=heroCollections.flatMap((collection,collectionIndex)=>completeCodes.map((code,index)=>({...collection,collectionIndex,code,index,src:glyphFile(collection.arch,collection.view,index,code)})));
let heroIndex=2,heroTimer=0,heroSwapTimer=0;
function showHeroSpecimen(nextIndex,{animate=true,restart=true}={}){
  heroIndex=(nextIndex+heroItems.length)%heroItems.length;const item=heroItems[heroIndex],art=$("#hero-specimen-art"),card=$("#hero-specimen-card"),apply=()=>{
    art.src=item.src;art.alt=`${item.code}, arco ${item.arch==="upper"?"superior":"inferior"}, vista ${item.view==="profile"?"de perfil":"oclusal"}`;
    card.classList.toggle("is-occlusal",item.view==="occlusal");$("#hero-specimen-code").textContent=visibleHeroCode(item.code,item.view);$("#hero-specimen-title").textContent=item.label;$("#hero-specimen-count").textContent=`${String(heroIndex+1).padStart(2,"0")} / 64`;
    $$("[data-hero-collection]").forEach(button=>{const active=Number(button.dataset.heroCollection)===item.collectionIndex;button.classList.toggle("active",active);button.setAttribute("aria-pressed",String(active))});
    $("#hero-focus-code").textContent=visibleHeroCode(item.code,item.view);$("#hero-focus-label").textContent=item.label.toLowerCase();
    requestAnimationFrame(()=>card.classList.remove("is-changing"));
    const following=heroItems[(heroIndex+1)%heroItems.length],preload=new Image();preload.src=following.src;
  };
  clearTimeout(heroSwapTimer);if(animate){card.classList.add("is-changing");heroSwapTimer=setTimeout(apply,170)}else apply();if(restart)startHeroRotation();
}
function startHeroRotation(){clearInterval(heroTimer);if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;heroTimer=setInterval(()=>showHeroSpecimen(heroIndex+1,{restart:false}),2800)}
function renderHero(){
  $("#hero-arch").innerHTML=`<div class="specimen-stage">
    <div class="specimen-measure" aria-hidden="true"><span>01</span><i></i><span>64</span></div>
    <article class="specimen-card" id="hero-specimen-card">
      <div class="specimen-meta"><span id="hero-specimen-title">Superior · perfil</span><b id="hero-specimen-count">03 / 64</b></div>
      <div class="specimen-art"><span class="specimen-watermark" id="hero-specimen-code">M1</span><img id="hero-specimen-art" src="${glyphFile("upper","profile",2,"M1")}" alt="Primeiro molar superior em perfil"></div>
      <div class="specimen-caption"><span>GLIFO VETORIAL</span><b>Dental Icons</b></div>
    </article>
    <nav class="specimen-collections" aria-label="Coleções de glifos">${heroCollections.map((collection,index)=>`<button type="button" data-hero-collection="${index}" aria-pressed="false"><i>0${index+1}</i><span>${collection.short}</span></button>`).join("")}</nav>
    <div class="specimen-controls"><button type="button" id="hero-prev" aria-label="Glifo anterior">←</button><span><i></i> EXIBIÇÃO AUTOMÁTICA</span><button type="button" id="hero-next" aria-label="Próximo glifo">→</button></div>
  </div>`;
  $$("[data-hero-collection]").forEach(button=>button.addEventListener("click",()=>showHeroSpecimen(Number(button.dataset.heroCollection)*16)));
  $("#hero-prev").addEventListener("click",()=>showHeroSpecimen(heroIndex-1));$("#hero-next").addEventListener("click",()=>showHeroSpecimen(heroIndex+1));
  showHeroSpecimen(heroIndex,{animate:false});
}
function renderOdontogram(){
  const tokens=parseSequence($("#sequence-input").value),divider=tokens.indexOf("|"),teeth=tokens.filter(t=>t!=="|"),normalizedTeeth=teeth.map(token=>token.toUpperCase()),hasExplicitLowercase=teeth.some(token=>token!==token.toUpperCase()),rightOrder=teeth.length>1&&RIGHT_SEQUENCE_SCORE(normalizedTeeth)>0,viewFor=token=>hasExplicitLowercase?(token===token.toLowerCase()?"occlusal":"profile"):state.view;let toothIndex=0;
  const target=$("#live-odontogram");target.className=`live-odontogram layout-${state.layout}${state.labels?"":" hide-labels"}`;target.style.setProperty("--glyph-size",`${state.size}px`);target.style.setProperty("--glyph-gap",`${state.layout==="compact"?Math.max(0,state.spacing-8):state.spacing}px`);target.style.setProperty("--glyph-color",state.color);
  target.innerHTML=tokens.map((token,tokenPosition)=>{if(token==="|")return '<span class="sim-divider" aria-hidden="true"></span>';const code=token.toUpperCase(),tokenView=viewFor(token),side=divider>=0?(tokenPosition<divider?"left":"right"):(rightOrder?"right":"left"),index=positionFor(code,side),curve=state.layout==="arch"?Math.pow((toothIndex-(teeth.length-1)/2)/Math.max(1,teeth.length/2),2)*34:0;toothIndex++;const file=glyphFile(state.arch,tokenView,index,code),label=tokenView==="occlusal"?code.toLowerCase():code;return `<span class="sim-glyph is-${tokenView}" style="--curve:${curve}px" data-file="${file}" data-view="${tokenView}"><span class="glyph-art" style="--glyph-url:url('${file}')"></span><span class="sim-code">${label}</span></span>`}).join("");
  const views=new Set(teeth.map(viewFor)),arch=state.arch==="upper"?"superior":"inferior",view=views.size>1?"perfil + face oclusal":views.has("occlusal")?"face oclusal":"perfil",rootDirection=state.arch==="upper"?"↑":"↓";$("#preview-title").textContent=`Arcada ${arch} — ${view}`;$("#position-count").textContent=views.size>1?`${teeth.length} POSIÇÕES · 2 VISTAS`:`${teeth.length} POSIÇÕES · ${view==="perfil"?`RAÍZES ${rootDirection}`:"FACE"}`;$("#typed-sequence").textContent=tokens.map(token=>{if(token==="|")return token;const code=token.toUpperCase();return viewFor(token)==="occlusal"?code.toLowerCase():code}).join(" ");
}
function RIGHT_SEQUENCE_SCORE(tokens){const order=["I","L","C","P1","P2","M1","M2","M3"],first=order.indexOf(tokens[0]),last=order.indexOf(tokens[tokens.length-1]);return last-first}
function activateGroup(group,button){group.querySelectorAll("button").forEach(item=>{const active=item===button;item.classList.toggle("active",active);item.setAttribute("aria-pressed",String(active))});state[group.dataset.control]=button.dataset.value;renderOdontogram()}
$$('.segment').forEach(group=>group.addEventListener('click',event=>{const button=event.target.closest('button');if(button)activateGroup(group,button)}));
$("#sequence-input").addEventListener("input",()=>{$$(".preset-list button").forEach(b=>b.classList.remove("active"));renderOdontogram()});
$$('[data-preset]').forEach(button=>button.addEventListener('click',()=>{$$('[data-preset]').forEach(b=>b.classList.toggle('active',b===button));$("#sequence-input").value=presets[button.dataset.preset];renderOdontogram()}));
$("#size-range").addEventListener("input",event=>{state.size=Number(event.target.value);$("#size-output").value=`${state.size} px`;renderOdontogram()});
$("#spacing-range").addEventListener("input",event=>{state.spacing=Number(event.target.value);$("#spacing-output").value=`${state.spacing} px`;renderOdontogram()});
$("#show-labels").addEventListener("change",event=>{state.labels=event.target.checked;renderOdontogram()});
$(".swatches").addEventListener("click",event=>{const button=event.target.closest("button[data-color]");if(!button)return;$$('.swatches button').forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active))});state.color=button.dataset.color;renderOdontogram()});
$$('[data-context]').forEach(button=>button.addEventListener('click',()=>{$$('[data-context]').forEach(b=>b.classList.toggle('active',b===button));state.context=button.dataset.context;$(".preview-workspace").dataset.contextView=state.context}));

function toast(message){const el=$("#toast");el.textContent=message;el.classList.add("visible");clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.remove("visible"),1800)}
$("#copy-sequence").addEventListener("click",async()=>{const text=$("#typed-sequence").textContent;try{await navigator.clipboard.writeText(text);toast("Sequência copiada")}catch{toast("Selecione e copie a sequência")}});
async function coloredGlyph(url,color){const svg=await fetch(url).then(r=>r.text()),colored=svg.replace(/color="[^"]+"/,`color="${color}"`);return new Promise((resolve,reject)=>{const image=new Image(),objectUrl=URL.createObjectURL(new Blob([colored],{type:"image/svg+xml"}));image.onload=()=>{URL.revokeObjectURL(objectUrl);resolve(image)};image.onerror=reject;image.src=objectUrl})}
$("#export-png").addEventListener("click",async()=>{
  const width=1200,height=600,scale=2,canvas=document.createElement("canvas"),glyphs=$$(".sim-glyph");canvas.width=width*scale;canvas.height=height*scale;const ctx=canvas.getContext("2d");ctx.scale(scale,scale);ctx.fillStyle=state.context==="slide"?"#eefaf7":"#ffffff";ctx.fillRect(0,0,width,height);
  ctx.fillStyle="#087f6a";ctx.font="700 12px monospace";ctx.fillText("ODONTOGRAMA",70,58);ctx.fillStyle="#102b28";ctx.font="700 26px sans-serif";ctx.fillText($("#preview-title").textContent,70,90);ctx.strokeStyle="#d9e5e2";ctx.beginPath();ctx.moveTo(70,118);ctx.lineTo(width-70,118);ctx.stroke();
  const cell=(width-140)/Math.max(glyphs.length,1),center=(glyphs.length-1)/2,top=180;
  for(let index=0;index<glyphs.length;index++){const glyph=glyphs[index],img=await coloredGlyph(glyph.dataset.file,state.color),glyphView=glyph.dataset.view,ratio=glyphView==="profile"?.58:1,boxWidth=Math.min(cell*.72,glyphView==="profile"?64:58),boxHeight=glyphView==="profile"?boxWidth/ratio:boxWidth,curve=state.layout==="arch"?Math.pow((index-center)/Math.max(1,glyphs.length/2),2)*45:0,x=70+cell*index+(cell-boxWidth)/2,y=top+curve+(glyphView==="profile"?0:42);ctx.drawImage(img,x,y,boxWidth,boxHeight);if(state.labels){ctx.fillStyle=state.color;ctx.font="700 12px monospace";ctx.textAlign="center";ctx.fillText(glyph.querySelector(".sim-code").textContent,x+boxWidth/2,top+210+curve)}}
  if(glyphs.length>1){ctx.strokeStyle="#9ebeb7";ctx.setLineDash([4,5]);ctx.beginPath();ctx.moveTo(width/2,165);ctx.lineTo(width/2,405);ctx.stroke();ctx.setLineDash([])}ctx.strokeStyle="#d9e5e2";ctx.beginPath();ctx.moveTo(70,480);ctx.lineTo(width-70,480);ctx.stroke();ctx.textAlign="left";ctx.fillStyle="#6f817d";ctx.font="600 12px monospace";ctx.fillText($("#typed-sequence").textContent,70,520);ctx.textAlign="right";ctx.fillStyle="#087f6a";ctx.fillText("Dental Icons Font · Dante Testa",width-70,520);
  canvas.toBlob(blob=>{const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download="odontograma-dental-icons.png";link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);toast("PNG exportado em 2400 × 1200 px")},"image/png");
});

const tabs=$$(".install-tabs button");tabs.forEach((tab,index)=>{tab.addEventListener("click",()=>activateTab(tab));tab.addEventListener("keydown",event=>{if(!["ArrowLeft","ArrowRight"].includes(event.key))return;event.preventDefault();const next=tabs[(index+(event.key==="ArrowRight"?1:-1)+tabs.length)%tabs.length];activateTab(next);next.focus()})});
function activateTab(selected){tabs.forEach(tab=>{const active=tab===selected;tab.setAttribute("aria-selected",String(active));$(`#panel-${tab.dataset.tab}`).hidden=!active})}
$("#copy-code").addEventListener("click",async event=>{try{await navigator.clipboard.writeText($("#webfont-code").textContent);event.currentTarget.textContent="Copiado"}catch{event.currentTarget.textContent="Selecione"}setTimeout(()=>event.currentTarget.textContent="Copiar",1600)});
const compareState={code:"M1",arch:"upper",side:"left"};
function renderComparator(){const code=compareState.code,leftIndex=completeCodes.slice(0,8).indexOf(code),rightIndex=completeCodes.slice(8).indexOf(code),index=compareState.side==="left"?Math.max(0,leftIndex):Math.max(0,rightIndex)+8,profile=glyphFile(compareState.arch,"profile",index,code),occlusal=glyphFile(compareState.arch,"occlusal",index,code);$("#compare-profile-code").textContent=code;$("#compare-occlusal-code").textContent=code.toLowerCase();$("#compare-profile-art").src=profile;$("#compare-occlusal-art").src=occlusal;const arch=compareState.arch==="upper"?"superior":"inferior",side=compareState.side==="left"?"esquerdo":"direito";$("#compare-profile-art").alt=`${code}, arco ${arch}, lado ${side}, perfil`;$("#compare-occlusal-art").alt=`${code.toLowerCase()}, arco ${arch}, lado ${side}, vista oclusal`}
function setCompareCode(value){const normalized=value.trim().toUpperCase(),valid=new Set(["I","L","C","P1","P2","M1","M2","M3"]);if(!valid.has(normalized)){$("#compare-code").classList.add("invalid");return}compareState.code=normalized;$("#compare-code").classList.remove("invalid");$$('[data-compare-code]').forEach(button=>button.classList.toggle('active',button.dataset.compareCode===normalized));renderComparator()}
$("#compare-code").addEventListener("input",event=>setCompareCode(event.target.value));$$('[data-compare-code]').forEach(button=>button.addEventListener('click',()=>{$("#compare-code").value=button.dataset.compareCode;setCompareCode(button.dataset.compareCode)}));$$('[data-compare]').forEach(group=>group.addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;group.querySelectorAll('button').forEach(item=>item.classList.toggle('active',item===button));compareState[group.dataset.compare]=button.dataset.value;renderComparator()}));
$$('[data-open-download]').forEach(button=>button.addEventListener('click',()=>{const link=document.createElement('a');link.href='downloads/dental-icons-font.zip';link.download='dental-icons-font.zip';document.body.appendChild(link);link.click();link.remove();toast('Download iniciado: TTF, OTF e WOFF2')}));
const hero=$("#hero-visual");hero.addEventListener("pointermove",event=>{const r=hero.getBoundingClientRect(),x=(event.clientX-r.left)/r.width-.5,y=(event.clientY-r.top)/r.height-.5,card=$("#hero-specimen-card");hero.style.setProperty('--mx',`${(x+.5)*100}%`);hero.style.setProperty('--my',`${(y+.5)*100}%`);if(card)card.style.transform=`rotateY(${x*4.5}deg) rotateX(${-y*3.5}deg) translateY(-3px)`});hero.addEventListener("pointerenter",()=>clearInterval(heroTimer));hero.addEventListener("pointerleave",()=>{const card=$("#hero-specimen-card");if(card)card.style.transform="";startHeroRotation()});
function drawField(){const canvas=$("#hero-field"),ctx=canvas.getContext("2d"),dpr=Math.min(devicePixelRatio,2),r=canvas.getBoundingClientRect();canvas.width=r.width*dpr;canvas.height=r.height*dpr;ctx.scale(dpr,dpr);ctx.clearRect(0,0,r.width,r.height);ctx.fillStyle="rgba(8,127,106,.22)";for(let i=0;i<34;i++){const a=i*2.399,radius=65+(i%9)*27,x=r.width/2+Math.cos(a)*radius,y=r.height/2+Math.sin(a)*radius*.78;ctx.beginPath();ctx.arc(x,y,i%5===0?2:1,0,Math.PI*2);ctx.fill()}}
window.addEventListener("resize",drawField);renderHero();renderOdontogram();renderComparator();drawField();
