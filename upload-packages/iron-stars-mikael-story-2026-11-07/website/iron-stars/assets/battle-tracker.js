window.IronBattleUI=function(data,getRoster,getRosterId,download){
  'use strict';
  const core=window.IronBattle,key='iron-stars-battles-v1',app=document.getElementById('builder-app');
  let saved={schema:1,entries:{}},broken=false,raw=null,state=null,rosterId=null,saveMessage='';
  try{raw=localStorage.getItem(key);if(raw){const parsed=JSON.parse(raw);if(parsed.schema!==1||!parsed.entries||typeof parsed.entries!=='object'||Array.isArray(parsed.entries))throw Error();saved=parsed;}}catch(e){broken=true;saveMessage='Battle storage could not be read. Stored data is preserved; changes are session-only.';}
  const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
  const host=el('section');host.id='battle-tracker';host.className='battle-tracker';host.hidden=true;app.after(host);
  let status;
  function button(text,action){const b=el('button',text);b.type='button';b.onclick=()=>{try{action();}catch(e){status.textContent=e.message;}};return b;}
  function persist(){
    if(broken){saveMessage='Battle changes are session-only. Export this battle to keep them; unreadable stored data is unchanged.';return;}
    try{localStorage.setItem(key,JSON.stringify(saved));saveMessage='Battle saved in this browser. Roster designs are unchanged.';}catch(e){saveMessage='Battle changes are session-only. Browser saving failed; export this battle to keep them.';}
  }
  function commit(next,redraw=true){state=core.validate(next);saved.entries[rosterId]={...saved.entries[rosterId],battle:state};persist();if(redraw)render();else if(status)status.textContent=saveMessage;}
  function fresh(){const next=core.start(getRoster(),data),previous=saved.entries[rosterId]?.battle;saved.entries[rosterId]={battle:next,...(previous?{previous}: {})};state=next;persist();render();}
  function render(){
    const focus=document.activeElement?.id;host.replaceChildren();
    const title=el('h2','Battle tracker');title.id='battle-title';title.tabIndex=-1;host.setAttribute('aria-labelledby',title.id);host.append(title);
    const actions=el('div');actions.className='builder-actions';actions.append(button('Back to roster',()=>{host.hidden=true;app.hidden=false;document.getElementById('army-battle').focus();}),button('Start new battle from roster',fresh));
    const previous=saved.entries[rosterId]?.previous;
    if(previous)actions.append(button('Undo battle restart',()=>{const record=saved.entries[rosterId];saved.entries[rosterId]={battle:record.previous,previous:record.battle};try{state=core.validate(record.previous);}catch(e){state=null;}persist();render();}));
    actions.append(button('Export battle',()=>download(JSON.stringify(state||saved.entries[rosterId]?.battle,null,2),'iron-stars-battle.json')));
    if(broken&&raw)actions.append(button('Export stored battle data',()=>download(raw,'iron-stars-battle-storage.json')));
    const importLabel=el('label','Import battle'),input=el('input');importLabel.className='import-label';input.type='file';input.accept='.json,application/json';importLabel.append(input);actions.append(importLabel);
    input.onchange=async()=>{const file=input.files[0];if(!file)return;try{if(file.size>5000000)throw Error('Battle file is too large.');const incoming=core.validate(JSON.parse(await file.text()));if(incoming.faction!==getRoster().faction)throw Error('Choose a roster of the battle’s faction before importing.');const previous=saved.entries[rosterId]?.battle;saved.entries[rosterId]={battle:incoming,...(previous?{previous}:{})};state=incoming;persist();render();}catch(e){status.textContent='Import failed: '+e.message+' Existing battle is unchanged.';}finally{input.value='';}};
    host.append(actions);status=el('p',saveMessage);status.id='battle-status';status.setAttribute('role','status');host.append(status);
    if(!state){host.append(el('p','This saved battle could not be loaded. Export its original data or start a new battle; the previous snapshot remains available through Undo battle restart.'));return;}
    host.append(el('p',`${state.name||'My force'} · ${data.factions.find(f=>f.id===state.faction)?.name||state.faction} · ${state.points} points`));
    host.append(el('p','This battle uses a roster snapshot. Roster edits do not change it; start a new battle to use an updated force. Counters are manual and do not resolve attacks or enforce full army legality.'));
    const round=el('div');round.className='battle-round';const advance=button('Advance round',()=>commit(core.nextRound(state)));advance.id='battle-next-round';round.append(el('strong',`Round ${state.round}`),advance);host.append(round);
    host.append(el('p','Advancing the round clears Activated marks and replenishes once-per-round uses. Structure, suppression, removed marks and once-per-game uses stay unchanged.',''));
    if(state.traits?.length){const traits=el('details');traits.append(el('summary','Faction & affiliation rules'));for(const rule of state.traits)traits.append(el('h3',rule.name),el('p',rule.text));host.append(traits);}
    const list=el('div');list.className='battle-unit-list';
    for(const unit of state.units){
      const label=unit.name+' · unit '+unit.ordinal,article=el('article');article.className='battle-unit'+(unit.structure===0?' at-zero':'')+(unit.removed?' removed-unit':'');article.append(el('h3',label),el('p',`Copy ${unit.copy} of ${unit.total_copies}`));
      const profile=unit.profiles[unit.form];
      if(unit.profiles.length>1){const formLabel=el('label','Current form'),select=el('select');select.id='battle-form-'+unit.id;select.setAttribute('aria-label','Form for '+label);unit.profiles.forEach((p,i)=>{const option=el('option',p.name);option.value=i;select.append(option);});select.value=unit.form;select.onchange=()=>commit(core.form(state,unit.id,Number(select.value)));formLabel.append(select);article.append(formLabel);}
      article.append(el('p',`Move ${profile.movement} · Defence ${profile.defence}`));
      if(profile.movement_label&&profile.movement_rules?.length){article.append(el('strong',profile.movement_label));for(const rule of profile.movement_rules)article.append(el('p',rule.text));}
      if(profile.loadout)article.append(el('p','Weapons in this form: '+(profile.loadout.join('; ')||'None')));
      const max=core.maximum(unit);
      if(profile.structure===null){const label=el('label','Starting STR not specified in source — enter agreed value'),starting=el('input');starting.type='number';starting.min=1;starting.step=1;starting.value=unit.manual_max??'';starting.setAttribute('aria-label','Agreed starting Structure for '+unit.name+' unit '+unit.ordinal);label.append(starting);article.append(label,button('Set starting STR',()=>commit(core.manualMaximum(state,unit.id,Number(starting.value)))));}
      const structureLabel=el('label',`Remaining Structure${max===null?'':` / ${max}`}`),field=el('input');field.type='number';field.min=0;field.step=1;if(max!==null)field.max=max;field.value=unit.structure??'';field.disabled=max===null;field.id='battle-str-'+unit.id;field.setAttribute('aria-label','Structure for '+label);structureLabel.append(field);article.append(structureLabel);
      const controls=el('div');controls.className='battle-controls';
      const damage=button('−1 STR',()=>commit(core.structure(state,unit.id,unit.structure-1))),repair=button('+1 STR',()=>commit(core.structure(state,unit.id,unit.structure+1)));damage.id='battle-damage-'+unit.id;repair.id='battle-repair-'+unit.id;damage.setAttribute('aria-label','Damage '+label);repair.setAttribute('aria-label','Restore Structure for '+label);damage.disabled=max===null||unit.structure===0;repair.disabled=max===null||unit.structure===max;controls.append(damage,repair);article.append(controls);
      const zero=el('p','At 0 STR. Keep this unit on the tracker until removal or revival is resolved.');zero.className='battle-zero';zero.hidden=unit.structure!==0;article.append(zero);
      field.oninput=()=>{try{if(field.value==='')return;commit(core.structure(state,unit.id,Number(field.value)),false);field.setCustomValidity('');const updated=state.units.find(u=>u.id===unit.id);damage.disabled=updated.structure===0;repair.disabled=updated.structure===max;zero.hidden=updated.structure!==0;article.classList.toggle('at-zero',updated.structure===0);}catch(e){field.setCustomValidity(e.message);status.textContent=e.message;}};
      // Resolve the latest value after inline number edits without rebuilding
      // the focused input or letting button closures use an older counter.
      damage.onclick=()=>{try{const current=state.units.find(u=>u.id===unit.id);commit(core.structure(state,unit.id,current.structure-1));}catch(e){status.textContent=e.message;}};
      repair.onclick=()=>{try{const current=state.units.find(u=>u.id===unit.id);commit(core.structure(state,unit.id,current.structure+1));}catch(e){status.textContent=e.message;}};
      const flags=el('div');flags.className='battle-flags';for(const [key,name] of [['activated','Activated'],['suppressed','Suppressed (optional morale module)'],['removed','Removed from battlefield']]){const label=el('label'),check=el('input');check.type='checkbox';check.checked=unit[key];check.id='battle-'+key+'-'+unit.id;check.setAttribute('aria-label',name+' for '+unit.name+' unit '+unit.ordinal);check.onchange=()=>commit(core.flag(state,unit.id,key,check.checked));label.append(check,document.createTextNode(' '+name));flags.append(label);}article.append(flags);
      if(unit.ammo_bin){const label=el('label','Ammo Bin: choose one weapon copy'),select=el('select'),empty=el('option','Choose copy before spending ammunition');empty.value='';select.append(empty);for(const counter of unit.uses.filter(c=>c.ammunition&&c.group===unit.ammo_bin.group)){const option=el('option',counter.name);option.value=counter.copy;select.append(option);}select.value=unit.ammo_bin.copy??'';select.onchange=()=>{try{if(select.value==='')return;commit(core.ammoBin(state,unit.id,Number(select.value)));}catch(e){select.value=unit.ammo_bin.copy??'';status.textContent=e.message;}};label.append(select);article.append(label);}
      if(unit.uses.length){article.append(el('h4','Limited uses'));for(const counter of unit.uses){const group=el('div');group.className='battle-use';const label=el('label',`${counter.name} · per ${counter.period} · ${counter.limit} maximum`),remaining=el('input');remaining.type='number';remaining.min=0;remaining.max=counter.limit;remaining.step=1;remaining.value=counter.remaining;remaining.setAttribute('aria-label','Uses left for '+counter.name+' · '+unit.name+' unit '+unit.ordinal);label.append(remaining);group.append(label);remaining.oninput=()=>{try{if(remaining.value==='')return;commit(core.remaining(state,unit.id,counter.id,Number(remaining.value)),false);remaining.setCustomValidity('');spend.disabled=Number(remaining.value)===0;}catch(e){remaining.setCustomValidity(e.message);status.textContent=e.message;}};
        const spend=button('Use once',()=>{const current=state.units.find(u=>u.id===unit.id).uses.find(c=>c.id===counter.id);commit(core.remaining(state,unit.id,counter.id,current.remaining-1));});spend.id='battle-use-'+unit.id+'-'+counter.id;spend.setAttribute('aria-label','Use '+counter.name+' · '+unit.name+' unit '+unit.ordinal);spend.disabled=counter.remaining===0;group.append(spend);
        const source=el('details');source.append(el('summary','Usage rule'),el('p',counter.text));group.append(source);article.append(group);
      }if(unit.uses.some(c=>c.period==='activation'))article.append(button('Reset activation uses',()=>commit(core.activation(state,unit.id))));}
      const notesLabel=el('label','Battle notes'),notes=el('textarea');notes.maxLength=2000;notes.value=unit.notes;notes.setAttribute('aria-label','Notes for '+label);notes.oninput=()=>commit(core.notes(state,unit.id,notes.value),false);notesLabel.append(notes);article.append(notesLabel);
      const rules=el('details');rules.append(el('summary','Loadout & rules'));for(const rule of unit.rules){rules.append(el('strong',rule.name),el('p',rule.text));}article.append(rules);list.append(article);
    }
    host.append(list);if(focus)document.getElementById(focus)?.focus();
  }
  return {open(){rosterId=getRosterId();const record=saved.entries[rosterId];if(record){try{state=core.validate(record.battle);}catch(e){state=null;}}else{state=core.start(getRoster(),data);saved.entries[rosterId]={battle:state};persist();}app.hidden=true;document.getElementById('unit-card-view').hidden=true;host.hidden=false;render();document.getElementById('battle-title').focus();}};
};
