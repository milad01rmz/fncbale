(() => {
  'use strict';
  const {pages,groups}=window.FNC_DOCS;
  const $=id=>document.getElementById(id);
  const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icons={layers:'M4 8l8-5 8 5-8 5Z M4 12l8 5 8-5 M4 16l8 5 8-5',terminal:'M4 6h16v13H4Z M7 10l3 3-3 3 M13 16h4',key:'M14 4a5 5 0 1 1-3 9l-7 7H2v-3l7-7a5 5 0 0 1 5-6Z',target:'M12 3a9 9 0 1 0 9 9 M12 7a5 5 0 1 0 5 5 M12 12l8-8 M16 4h4v4',message:'M4 4h16v12H9l-5 4Z',image:'M3 4h18v16H3Z M3 17l6-7 5 5 3-3 4 5 M16 7h.01',activity:'M2 12h5l3-8 4 16 3-8h5',shield:'M12 3l8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z M8 12l3 3 5-6',history:'M3 4v6h6 M3 10a9 9 0 1 1 1 8 M12 7v5l3 2',copy:'M8 8h12v13H8Z M16 8V3H3v13h5',users:'M16 21v-3c0-3-3-4-6-4s-6 1-6 4v3 M10 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M17 4c4 1 4 6 0 7 M19 15c3 1 3 3 3 6',eye:'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6',braces:'M8 3H6v7l-3 2 3 2v7h2 M16 3h2v7l3 2-3 2v7h-2',help:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M9 9a3 3 0 1 1 4 3c-1 0-1 1-1 2 M12 17h.01',check:'M4 12l5 5L20 6'};
  const icon=name=>`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${icons[name]||icons.layers}"/></svg>`;
  const ui={fa:{docs:'مستندات',search:'جست‌وجوی راهنما',placeholder:'مثلاً چت‌آیدی، آلبوم یا edit…',outline:'در این صفحه',outlineNote:'مثال‌ها برای حساب کاربری بله هستند. نخست session بساز، سپس مقصد را resolve کن.',copy:'کپی',copied:'کپی شد',copyFailed:'کپی خودکار ممکن نیست؛ متن را انتخاب و کپی کن.',prev:'قبلی',next:'ادامهٔ راهنما',footer:'مستندات نسخهٔ ۰.۱.۳۶ · MIT',searchFooter:'جست‌وجوی محلی · بدون ارسال عبارت به سرور',empty:'نتیجه‌ای پیدا نشد. نام متد یا عبارت کوتاه‌تری را امتحان کن.',browse:'یک راهنما انتخاب کن یا جست‌وجو کن.',themeDark:'فعال‌کردن حالت تاریک',themeLight:'فعال‌کردن حالت روشن',menu:'فهرست راهنما',link:'پیوند این بخش',read:'خواندن راهنما',edit:'گزارش مشکل در راهنما ↗'},en:{docs:'Documentation',search:'Search the guides',placeholder:'Try chat ID, albums, or edit…',outline:'On this page',outlineNote:'Examples use a Bale user account. Create a session first, then resolve your destination.',copy:'Copy',copied:'Copied',copyFailed:'Clipboard unavailable; select and copy the code.',prev:'Previous',next:'Next guide',footer:'Documentation for 0.1.36 · MIT',searchFooter:'Local search · your query stays in the browser',empty:'No results. Try a method name or a shorter phrase.',browse:'Choose a guide or type to search.',themeDark:'Switch to dark mode',themeLight:'Switch to light mode',menu:'Open navigation',link:'Link to this section',read:'Read guide',edit:'Report a documentation issue ↗'}};
  let lang='fa',page=null,codes=[],observer;
  const tr=value=>typeof value==='string'?value:(value?.[lang]||'');
  const path=(id,section='')=>`#${lang}/${id}${section?'/'+section:''}`;
  const inline=value=>esc(tr(value)).replace(/`([^`]+)`/g,'<code>$1</code>');
  function highlight(source,language){
    if(language!=='python') return esc(source);
    const token=/(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:async|await|def|from|import|as|with|try|except|finally|if|else|for|in|return|raise|None|True|False|class|print)\b|\b\d+(?:\.\d+)?\b)/g;
    let out='',last=0;
    for(const match of source.matchAll(token)){
      out+=esc(source.slice(last,match.index));
      const value=match[0],kind=value.startsWith('#')?'comment':/^["']/.test(value)?'string':/^\d/.test(value)?'number':'keyword';
      out+=`<span class="token-${kind}">${esc(value)}</span>`;
      last=match.index+value.length;
    }
    return out+esc(source.slice(last));
  }
  function block(b){
    if(b.type==='p')return `<p>${inline(b.text)}</p>`;
    if(b.type==='code'){
      const index=codes.push(b.source)-1;
      return `<div class="code-block"><div class="code-toolbar"><span>${esc(b.label)}</span><button class="copy-button" data-copy="${index}" aria-label="${esc(ui[lang].copy)} ${esc(b.label)}">${icon('copy')}<span>${ui[lang].copy}</span></button></div><pre dir="ltr"><code>${highlight(b.source,b.language)}</code></pre></div>`;
    }
    if(b.type==='note')return `<aside class="note ${b.tone==='caution'?'caution':''}"><strong>${esc(tr(b.title))}</strong><p>${inline(b.text)}</p></aside>`;
    if(b.type==='table')return `<div class="table-wrap"><table><thead><tr>${b.headers.map(x=>`<th scope="col">${inline(x)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(row=>`<tr>${row.map(x=>`<td>${inline(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    if(b.type==='cards')return `<div class="cards">${b.items.map(item=>`<a class="card card-link" href="${path(item.route)}"><span class="card-icon">${icon(item.icon)}</span><h3>${esc(tr(item.title))}</h3><p>${esc(tr(item.text))}</p><span class="card-arrow">${ui[lang].read} ${lang==='fa'?'←':'→'}</span></a>`).join('')}</div>`;
    if(b.type==='steps')return `<ol class="step-list">${b.items.map(item=>`<li><div><strong>${esc(tr(item.title))}</strong><p>${inline(item.text)}</p></div></li>`).join('')}</ol>`;
    if(b.type==='layers')return `<div class="layer-stack"><div class="layer-stack-head"><span>${esc(tr(b.title))}</span><span class="tag" dir="ltr">async · durable</span></div>${b.items.map((item,i)=>`<div class="layer-row"><span class="layer-number">${String(i+1).padStart(2,'0')}</span><strong>${esc(tr(item))}</strong><span dir="ltr">${esc(b.labels[i])}</span></div>`).join('')}</div>`;
    return '';
  }
  function navigation(){
    return groups.map(group=>`<div class="nav-group"><div class="nav-label">${esc(tr(group.title))}</div>${pages.filter(x=>x.group===group.id).map(x=>`<a href="${path(x.id)}" class="nav-link" ${page.id===x.id?'aria-current="page"':''}>${icon(x.icon)}<span>${esc(tr(x.nav||x.title))}</span></a>`).join('')}</div>`).join('');
  }
  function updateThemeLabel(){
    const dark=document.documentElement.dataset.theme==='dark';
    $('theme-toggle').setAttribute('aria-label',dark?ui[lang].themeLight:ui[lang].themeDark);
    $('theme-toggle').setAttribute('aria-pressed',String(dark));
    document.querySelector('meta[name="theme-color"]').content=dark?'#171c1a':'#f8f9f7';
  }
  function render(){
    const root=document.documentElement;root.lang=lang;root.dir=lang==='fa'?'rtl':'ltr';
    try{localStorage.setItem('fncbale-language',lang)}catch{}
    document.title=`${tr(page.title)} · fncbale`;
    $('brand-caption').textContent=ui[lang].docs;
    document.querySelector('.brand').href=path('overview');
    $('search-label').textContent=ui[lang].search;
    $('search-input').placeholder=ui[lang].placeholder;
    $('search-input-label').textContent=ui[lang].search;
    $('search-footer').textContent=ui[lang].searchFooter;
    $('outline-label').textContent=ui[lang].outline;
    $('outline-note').textContent=ui[lang].outlineNote;
    $('footer-note').textContent=ui[lang].footer;
    $('edit-link').textContent=ui[lang].edit;
    $('menu-open').setAttribute('aria-label',ui[lang].menu);
    $('lang-fa').setAttribute('aria-pressed',String(lang==='fa'));
    $('lang-en').setAttribute('aria-pressed',String(lang==='en'));
    document.querySelector('.sidebar').setAttribute('aria-label',ui[lang].docs);
    document.querySelector('.page-turner').setAttribute('aria-label',ui[lang].docs);
    updateThemeLabel();
    $('navigation').innerHTML=navigation();$('mobile-navigation').innerHTML=navigation();
    const group=groups.find(x=>x.id===page.group);
    $('breadcrumb').innerHTML=`<span>${esc(ui[lang].docs)}</span><span aria-hidden="true">/</span><span>${esc(tr(group.title))}</span>`;
    codes=[];
    $('article').innerHTML=`<header class="page-header"><div class="eyebrow">${icon(page.icon)}<span>${esc(tr(group.title))}</span><span class="tag" dir="ltr">0.1.36 alpha</span></div><h1>${esc(tr(page.title))}</h1><p class="lead">${esc(tr(page.summary))}</p>${page.tags?`<div class="page-meta">${page.tags.map(x=>`<span class="tag" dir="ltr">${esc(x)}</span>`).join('')}</div>`:''}</header>${page.sections.map(s=>`<section class="doc-section" aria-labelledby="${s.id}"><h2 id="${s.id}">${esc(tr(s.title))}<a class="heading-link" href="${path(page.id,s.id)}" aria-label="${ui[lang].link}">#</a></h2>${s.blocks.map(block).join('')}</section>`).join('')}`;
    $('outline').innerHTML=page.sections.map(s=>`<a href="${path(page.id,s.id)}" data-section="${s.id}">${esc(tr(s.title))}</a>`).join('');
    const index=pages.indexOf(page),prev=pages[index-1],next=pages[index+1];
    $('page-turner').innerHTML=(prev?`<a href="${path(prev.id)}"><small>${ui[lang].prev}</small>${lang==='fa'?'→':'←'} ${esc(tr(prev.nav||prev.title))}</a>`:'')+(next?`<a class="next" href="${path(next.id)}"><small>${ui[lang].next}</small>${esc(tr(next.nav||next.title))} ${lang==='fa'?'←':'→'}</a>`:'');
    observer?.disconnect();
    observer=new IntersectionObserver(entries=>{
      for(const item of entries){if(item.isIntersecting){document.querySelectorAll('#outline a').forEach(a=>a.classList.toggle('active',a.dataset.section===item.target.id))}}
    },{rootMargin:'-90px 0px -60% 0px'});
    document.querySelectorAll('.doc-section h2').forEach(heading=>observer.observe(heading));
    const current=$('navigation').querySelector('[aria-current="page"]');
    if(current){const side=document.querySelector('.sidebar');const offset=current.offsetTop;if(offset<side.scrollTop||offset>side.scrollTop+side.clientHeight-130)side.scrollTop=Math.max(0,offset-80)}
  }
  function route(){
    const parts=location.hash.slice(1).split('/');
    const nextLang=parts[0]==='en'?'en':'fa';
    const nextPage=pages.find(x=>x.id===parts[1])||pages[0];
    const changed=!page||lang!==nextLang||page.id!==nextPage.id;
    lang=nextLang;page=nextPage;
    if(changed){render();window.scrollTo({top:0,behavior:'instant'})}
    if(parts[2]&&page.sections.some(s=>s.id===parts[2]))requestAnimationFrame(()=>$(parts[2])?.scrollIntoView());
    if($('mobile-dialog').open)$('mobile-dialog').close();
  }
  function searchable(value){
    if(value===null||value===undefined)return '';
    if(typeof value==='string')return value;
    if(value.fa!==undefined)return tr(value);
    if(Array.isArray(value))return value.map(searchable).join(' ');
    return Object.values(value).map(searchable).join(' ');
  }
  const normalize=value=>value.toLocaleLowerCase().replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/آ/g,'ا').replace(/[\u200c\u200d]/g,' ');
  function search(){
    const query=normalize($('search-input').value.trim());
    const terms=query.split(/\s+/).filter(Boolean);
    const results=[];
    for(const entry of pages){
      if(!terms.length){results.push({entry,section:null});continue}
      const head=normalize(searchable([entry.title,entry.summary]));
      if(terms.every(term=>head.includes(term))){results.push({entry,section:null});continue}
      for(const sec of entry.sections){const text=normalize(searchable([entry.title,sec.title,sec.blocks]));if(terms.every(term=>text.includes(term)))results.push({entry,section:sec})}
    }
    $('search-results').innerHTML=results.length?results.slice(0,24).map(({entry,section:sec})=>`<a role="listitem" class="search-result" href="${path(entry.id,sec?.id)}"><strong>${esc(tr(sec?.title||entry.title))}</strong><small>${esc(tr(entry.title))}${sec?' · '+esc(tr(entry.summary)).slice(0,90):''}</small></a>`).join(''):`<p class="empty-search">${ui[lang].empty}</p>`;
  }
  function openSearch(){search();$('search-dialog').showModal();$('search-input').focus()}
  $('search-open').addEventListener('click',openSearch);
  document.querySelector('.skip').addEventListener('click',e=>{e.preventDefault();$('article').focus();$('article').scrollIntoView()});
  $('search-input').addEventListener('input',search);
  $('search-results').addEventListener('click',e=>{if(e.target.closest('a'))$('search-dialog').close()});
  $('menu-open').addEventListener('click',()=>$('mobile-dialog').showModal());
  document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}}));
  $('lang-fa').addEventListener('click',()=>{location.hash=`fa/${page.id}${location.hash.split('/')[2]?'/'+location.hash.split('/')[2]:''}`});
  $('lang-en').addEventListener('click',()=>{location.hash=`en/${page.id}${location.hash.split('/')[2]?'/'+location.hash.split('/')[2]:''}`});
  $('theme-toggle').addEventListener('click',()=>{const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=theme;try{localStorage.setItem('fncbale-theme',theme)}catch{}updateThemeLabel()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){for(const id of ['search-dialog','mobile-dialog']){if($(id).open){e.preventDefault();$(id).close()}}}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();if(!$('search-dialog').open)openSearch()}});
  $('article').addEventListener('click',async e=>{
    const button=e.target.closest('[data-copy]');if(!button)return;
    const source=codes[Number(button.dataset.copy)];
    try{await navigator.clipboard.writeText(source);button.querySelector('span').textContent=ui[lang].copied;$('announcer').textContent=ui[lang].copied;setTimeout(()=>{if(button.isConnected)button.querySelector('span').textContent=ui[lang].copy},1800)}
    catch{const range=document.createRange();range.selectNodeContents(button.closest('.code-block').querySelector('code'));getSelection().removeAllRanges();getSelection().addRange(range);$('announcer').textContent=ui[lang].copyFailed}
  });
  window.addEventListener('hashchange',route);
  if(!location.hash){let saved='fa';try{saved=localStorage.getItem('fncbale-language')==='en'?'en':'fa'}catch{}history.replaceState(null,'',`#${saved}/overview`)}
  route();
})();
