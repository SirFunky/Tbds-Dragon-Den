(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('army-data').textContent);
  const core = window.IronRoster;
  const get = id => document.getElementById(id);
  const storageKey='iron-stars-rosters-v2',legacyKey='iron-stars-rosters-v1';
  let collection={schema:2,activeFaction:data.factions[0].id,activeByFaction:{},rosters:[]},activeId=null,heldRecord=null,current=core.blank(data.factions[0].id),restoreError='',collectionBroken=false,storedOriginal=null,removedRoster=null;
  try{
    storedOriginal=localStorage.getItem(storageKey);
    if(storedOriginal===null)storedOriginal=localStorage.getItem(legacyKey);
    if(storedOriginal)collection=core.rosterCollection(JSON.parse(storedOriginal));
  }catch(error){collectionBroken=true;restoreError='Saved rosters could not be read. Their stored data is unchanged; new edits are session-only. Export the stored backup before recovery.';}
  function chooseFaction(faction){
    const remembered=collection.activeByFaction[faction];
    let entry=collection.rosters.find(r=>r.id===remembered&&r.faction===faction)||collection.rosters.find(r=>r.faction===faction);
    if(!entry){const id='roster-'+crypto.randomUUID();collection=core.addRoster(collection,core.blank(faction),id,data);entry=collection.rosters.find(r=>r.id===id);}
    activateRoster(entry.id);
  }
  function activateRoster(id){
    const entry=collection.rosters.find(r=>r.id===id);
    if(!entry||!data.factions.some(f=>f.id===entry.faction))throw Error('This roster’s faction is unavailable.');
    activeId=id;heldRecord=null;collection.activeFaction=entry.faction;collection.activeByFaction[entry.faction]=id;
    try{current=core.validate(entry.roster,data);if(current.faction!==entry.faction)throw Error('Saved faction does not match.');}
    catch(error){heldRecord=entry;current=core.blank(entry.faction);}
  }
  chooseFaction(data.factions.some(f=>f.id===collection.activeFaction)?collection.activeFaction:data.factions[0].id);
  function save(){
    const entry=collection.rosters.find(r=>r.id===activeId);
    if(entry&&!heldRecord)entry.roster=core.validate(current,data);
    if(collectionBroken){get('save-status').textContent=restoreError;return;}
    try{localStorage.setItem(storageKey,JSON.stringify(collection));get('save-status').textContent='Roster saved in this browser.';}
    catch(error){get('save-status').textContent='Browser saving is unavailable. Export your roster to keep it.';}
  }
  function element(tag,text,cls) { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e; }
  const manager=element('section',undefined,'roster-manager');manager.id='roster-manager';manager.setAttribute('aria-label','Saved rosters');
  const rosterLabel=element('label','Saved roster'),rosterSelect=element('select');rosterSelect.id='saved-roster';rosterLabel.append(rosterSelect);manager.append(rosterLabel);
  const rosterActions=element('div',undefined,'builder-actions');
  const newRoster=element('button','New roster'),copyRoster=element('button','Duplicate roster'),deleteRoster=element('button','Remove roster'),undoRoster=element('button','Undo roster removal');
  for(const button of [newRoster,copyRoster,deleteRoster,undoRoster]){button.type='button';rosterActions.append(button);}manager.append(rosterActions);
  const tagsPanel=element('section',undefined,'roster-tags');tagsPanel.setAttribute('aria-label','Tags for selected roster');tagsPanel.append(element('h2','Roster tags'));
  const tagChips=element('div',undefined,'roster-tag-chips');tagChips.id='roster-tag-chips';tagsPanel.append(tagChips);
  const tagControls=element('div',undefined,'roster-tag-controls'),tagLabel=element('label','Add tags (separate with commas)'),tagInput=element('input'),addTags=element('button','Add tags');tagInput.type='text';tagInput.id='roster-tag-input';tagInput.maxLength=1000;tagInput.placeholder='500 points, Work in progress';tagLabel.append(tagInput);addTags.type='button';tagControls.append(tagLabel,addTags);tagsPanel.append(tagControls);manager.append(tagsPanel);
  const finder=element('details',undefined,'roster-finder');finder.append(element('summary','Find saved rosters'));
  const searchControls=element('div',undefined,'roster-search-controls'),rosterSearchLabel=element('label','Search roster names or tags'),rosterSearch=element('input');rosterSearch.type='search';rosterSearch.id='roster-search';rosterSearchLabel.append(rosterSearch);
  const scopeLabel=element('label','Search in'),rosterScope=element('select');rosterScope.id='roster-search-scope';for(const [value,text] of [['current','Current faction'],['all','All factions']]){const option=element('option',text);option.value=value;rosterScope.append(option);}scopeLabel.append(rosterScope);
  const tagFilterLabel=element('label','Tag filter'),tagFilter=element('select');tagFilter.id='roster-tag-filter';tagFilterLabel.append(tagFilter);searchControls.append(rosterSearchLabel,scopeLabel,tagFilterLabel);finder.append(searchControls);
  const searchCount=element('p');searchCount.id='roster-search-count';searchCount.setAttribute('role','status');searchCount.setAttribute('aria-live','polite');const searchResults=element('ul',undefined,'roster-search-results');searchResults.id='roster-search-results';finder.append(searchCount,searchResults);manager.append(finder);
  const backups=element('details',undefined,'roster-backups');backups.append(element('summary','Saved roster backups'));const backupActions=element('div',undefined,'builder-actions'),exportRosters=element('button','Export saved rosters'),importRostersLabel=element('label','Import saved rosters'),importRosters=element('input');exportRosters.type='button';importRostersLabel.className='import-label';importRosters.type='file';importRosters.accept='.json,application/json';importRostersLabel.append(importRosters);backupActions.append(exportRosters,importRostersLabel);backups.append(backupActions);manager.append(backups);
  manager.append(element('p','Each faction can keep several forces. Roster name below renames the selected force. Export saves a backup; imports add rosters without replacing your current force.','small-note'));
  const managerStatus=element('p');managerStatus.id='roster-manager-status';managerStatus.setAttribute('role','status');manager.append(managerStatus);document.querySelector('.builder-settings').before(manager);
  function renderRosterManager(){
    rosterSelect.replaceChildren();const entries=collection.rosters.filter(r=>r.faction===current.faction);
    entries.forEach((entry,index)=>{const name=typeof entry.roster?.name==='string'&&entry.roster.name.trim()?entry.roster.name:'My force';const duplicate=entries.some(other=>other!==entry&&other.roster?.name===entry.roster?.name);const option=element('option',name+(duplicate?` · ${index+1}`:''));option.value=entry.id;rosterSelect.append(option);});rosterSelect.value=activeId;
    copyRoster.disabled=!!heldRecord;undoRoster.hidden=!removedRoster;importRosters.disabled=collectionBroken;
    tagInput.disabled=addTags.disabled=!!heldRecord;tagChips.replaceChildren();
    const tags=core.normalizeTags(current.tags);
    if(!tags.length)tagChips.append(element('span','No tags yet.','small-note'));
    for(const tag of tags){const chip=element('span',tag,'roster-tag'),remove=element('button','×');remove.type='button';remove.disabled=!!heldRecord;remove.setAttribute('aria-label',`Remove roster tag ${tag}`);remove.onclick=()=>{current=core.validate({...current,tags:tags.filter(value=>value!==tag)},data);save();renderRosterManager();managerStatus.textContent='Tag removed.';};chip.append(remove);tagChips.append(chip);}
    renderRosterSearch();
  }
  function renderRosterSearch(){
    const scope=rosterScope.value==='current'?current.faction:null,previous=tagFilter.value,tags=new Map();
    for(const entry of collection.rosters){if(scope&&entry.faction!==scope)continue;try{for(const tag of core.normalizeTags(entry.roster?.tags))if(!tags.has(tag.toLowerCase()))tags.set(tag.toLowerCase(),tag);}catch(e){}}
    tagFilter.replaceChildren();const all=element('option','All tags');all.value='';tagFilter.append(all);
    for(const [key,name] of [...tags].sort((a,b)=>a[1].localeCompare(b[1]))){const option=element('option',name);option.value=key;tagFilter.append(option);}tagFilter.value=tags.has(previous)?previous:'';
    const results=core.findRosters(collection,{faction:scope,query:rosterSearch.value,tag:tagFilter.value},data);searchResults.replaceChildren();
    searchCount.textContent=`${results.length} matching ${results.length===1?'roster':'rosters'}. Your selected roster stays unchanged until you choose a result.`;
    if(!results.length)searchResults.append(element('li','No matches. Try another name, tag or faction scope.'));
    for(const entry of results){const item=element('li'),name=typeof entry.roster?.name==='string'&&entry.roster.name.trim()?entry.roster.name:'My force',button=element('button',name);button.type='button';button.setAttribute('aria-label',`Open saved roster ${name}`);if(entry.id===activeId)button.setAttribute('aria-current','true');
      button.onclick=()=>{try{save();activateRoster(entry.id);finishRosterSwitch('Saved roster selected.');}catch(e){managerStatus.textContent=e.message;}};item.append(button);
      let entryTags=[];try{entryTags=core.normalizeTags(entry.roster?.tags);}catch(e){}
      const faction=data.factions.find(f=>f.id===entry.faction)?.name||entry.faction;const meta=element('span',[faction,Number.isSafeInteger(entry.roster?.limit)?entry.roster.limit+' pt limit':null,...entryTags,entry.id===activeId?'Selected':null].filter(Boolean).join(' · '),'small-note');meta.id='roster-search-meta-'+entry.id;button.setAttribute('aria-describedby',meta.id);item.append(meta);searchResults.append(item);
    }
  }
  function applyTags(){try{const proposed=tagInput.value.split(',');if(!proposed.some(t=>t.trim()))return;current=core.validate({...current,tags:core.normalizeTags([...core.normalizeTags(current.tags),...proposed])},data);save();tagInput.value='';renderRosterManager();managerStatus.textContent='Roster tags saved.';tagInput.focus();}catch(e){managerStatus.textContent=e.message;}}
  addTags.onclick=applyTags;tagInput.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();applyTags();}};
  rosterSearch.oninput=renderRosterSearch;rosterScope.onchange=renderRosterSearch;tagFilter.onchange=renderRosterSearch;
  function finishRosterSwitch(message){tagInput.value='';get('army-search').value='';get('transfer-status').textContent='';get('army-limit').setCustomValidity('');save();render();customUI.refresh();managerStatus.textContent=message;}
  rosterSelect.onchange=()=>{try{save();activateRoster(rosterSelect.value);finishRosterSwitch('Roster selected.');}catch(e){rosterSelect.value=activeId;managerStatus.textContent=e.message;}};
  newRoster.onclick=()=>{try{save();const id='roster-'+crypto.randomUUID();collection=core.addRoster(collection,{...core.blank(current.faction),name:'New force'},id,data);activateRoster(id);finishRosterSwitch('New roster created. Enter its name below.');get('army-name').focus();get('army-name').select();}catch(e){managerStatus.textContent=e.message;}};
  copyRoster.onclick=()=>{try{save();const id='roster-'+crypto.randomUUID(),copy={...current,name:current.name.slice(0,93)+' (copy)'};collection=core.addRoster(collection,copy,id,data);activateRoster(id);finishRosterSwitch('Independent roster copy created, including quantities and loadouts.');get('army-name').focus();get('army-name').select();}catch(e){managerStatus.textContent=e.message;}};
  deleteRoster.onclick=()=>{try{save();const entry=collection.rosters.find(r=>r.id===activeId),faction=current.faction;collection=core.removeRoster(collection,activeId);removedRoster=entry;chooseFaction(faction);finishRosterSwitch('Roster removed. Use Undo roster removal to restore it. An empty roster is created if none remain for this faction.');}catch(e){managerStatus.textContent=e.message;}};
  undoRoster.onclick=()=>{if(!removedRoster)return;try{const entry=JSON.parse(JSON.stringify(removedRoster));if(collection.rosters.some(r=>r.id===entry.id))entry.id='roster-'+crypto.randomUUID();collection=core.rosterCollection({...collection,rosters:[...collection.rosters,entry]});activateRoster(entry.id);removedRoster=null;finishRosterSwitch('Removed roster restored.');}catch(e){managerStatus.textContent=e.message;}};
  exportRosters.onclick=()=>{save();download(collectionBroken&&storedOriginal?storedOriginal:JSON.stringify(collection,null,2),'iron-stars-saved-rosters.json');};
  importRosters.onchange=async()=>{const file=importRosters.files[0];if(!file)return;try{if(file.size>5000000)throw Error('Saved-roster backup is too large.');const value=JSON.parse(await file.text());save();const next=core.mergeRosters(collection,value,()=> 'roster-'+crypto.randomUUID());collection=next;save();render();managerStatus.textContent='Saved rosters imported. Existing forces and your current selection are preserved.';}catch(e){managerStatus.textContent='Import failed: '+e.message+' Existing rosters are unchanged.';}finally{importRosters.value='';}};
  const libraryKey='iron-stars-unit-library-v1';let library={schema:1,designs:[]},libraryMessage='',libraryRaw=null,libraryBroken=false,undoDesign=null;
  try{libraryRaw=localStorage.getItem(libraryKey);if(libraryRaw)library=core.validateLibrary(JSON.parse(libraryRaw));}catch(e){libraryBroken=true;libraryMessage='The saved library could not be read. Export its stored data to keep it; it has not been overwritten.';}
  const libraryPanel=element('details',undefined,'unit-library');libraryPanel.id='unit-library';libraryPanel.append(element('summary','Saved custom-unit library'));
  libraryPanel.append(element('p','Save designs from your roster, then add them to any roster of the same faction. Added units use current prices and equipment restrictions. This library is saved in this browser; export it for a backup.','small-note'));
  const libraryTools=element('div',undefined,'library-tools'),searchLabel=element('label','Find a design'),librarySearch=element('input');librarySearch.type='search';librarySearch.id='library-search';searchLabel.append(librarySearch);
  const filterLabel=element('label','Show'),libraryFilter=element('select');libraryFilter.id='library-filter';for(const [value,text] of [['current','Current faction'],['all','All factions']]){const option=element('option',text);option.value=value;libraryFilter.append(option);}filterLabel.append(libraryFilter);libraryTools.append(searchLabel,filterLabel);libraryPanel.append(libraryTools);
  const libraryActions=element('div',undefined,'builder-actions'),exportLibrary=element('button','Export library'),importLabel=element('label','Import library'),importLibrary=element('input');exportLibrary.type='button';importLabel.className='import-label';importLibrary.type='file';importLibrary.accept='.json,application/json';importLabel.append(importLibrary);libraryActions.append(exportLibrary,importLabel);
  const undoLibrary=element('button','Undo removal');undoLibrary.type='button';undoLibrary.hidden=true;libraryActions.append(undoLibrary);libraryPanel.append(libraryActions);
  const libraryStatus=element('p');libraryStatus.id='library-status';libraryStatus.setAttribute('role','status');libraryPanel.append(libraryStatus);
  const libraryList=element('div',undefined,'library-list');libraryPanel.append(libraryList);get('save-status').before(libraryPanel);
  function storeLibrary(next,message){
    library=core.validateLibrary(next);
    try{localStorage.setItem(libraryKey,JSON.stringify(library));libraryRaw=JSON.stringify(library);libraryMessage=message;}catch(e){libraryMessage='Library changes are available for this session only. Browser saving failed; export the library to keep them.';}
    renderLibrary();
  }
  function renderLibrary(){
    libraryList.replaceChildren();libraryStatus.textContent=libraryMessage;importLibrary.disabled=libraryBroken;
    undoLibrary.hidden=!undoDesign;
    const query=librarySearch.value.trim().toLocaleLowerCase();
    const visible=library.designs.filter(entry=>(libraryFilter.value==='all'||entry.faction===current.faction)&&[entry.custom.name,data.factions.find(f=>f.id===entry.faction)?.name||entry.faction].join(' ').toLocaleLowerCase().includes(query));
    if(!visible.length)libraryList.append(element('p',library.designs.length?'No matching designs. Change the search or faction filter.':'No saved designs yet. Use “Save to library” on a custom unit in your roster.'));
    for(const entry of visible){
      const card=element('article',undefined,'library-design');card.append(element('h3',entry.custom.name));
      const faction=data.factions.find(f=>f.id===entry.faction),origin=faction?.subfactions?.find(s=>s.id===entry.subfaction);card.append(element('p',(faction?.name||entry.faction)+(origin?' · Saved under '+origin.name:''),'small-note'));
      let error='',result;try{result=window.IronCustom.calculate(entry.custom,entry.faction,data,{subfaction:entry.faction===current.faction?current.subfaction:entry.subfaction});}catch(e){error=e.message;}
      if(result){
        card.append(element('strong',`${result.total} pts`));if(result.forms.length)card.append(element('p',result.forms.map(f=>f.name+(f.movement_rules.length?' · '+f.movement_label:'')).join(' / '),'small-note'));
        const details=element('details'),list=element('ul');details.append(element('summary','Design loadout'),list);
        for(const part of result.breakdown)list.append(element('li',`${part.quantity}× ${part.name}${part.linked?' · Linked':''}${part.forms?' · '+part.forms.join(' / '):''}`));
        if(result.unit.ammo_target!==undefined)details.append(element('p',`Ammo Bin target: weapon group ${result.unit.ammo_target+1}.`));card.append(details);
      }
      else card.append(element('p','Unavailable for this selection: '+error,'small-note'));
      const actions=element('div',undefined,'builder-actions'),add=element('button','Add to roster');add.type='button';add.setAttribute('aria-label',`Add saved ${entry.custom.name}`);add.disabled=!!error||entry.faction!==current.faction||!!heldRecord;
      add.onclick=()=>{try{current=core.addDesign(current,entry,'custom-'+crypto.randomUUID(),data);save();renderRoster();libraryMessage='Design added as one independent unit. Edit it in your roster to make a variant.';renderLibrary();}catch(e){libraryMessage=e.message;renderLibrary();}};actions.append(add);
      if(entry.faction!==current.faction)card.append(element('p','Switch to this design’s faction to add it.','small-note'));
      const remove=element('button','Remove from library');remove.type='button';remove.setAttribute('aria-label',`Remove saved ${entry.custom.name}`);remove.disabled=libraryBroken;remove.onclick=()=>{undoDesign=entry;storeLibrary({schema:1,designs:library.designs.filter(d=>d.id!==entry.id)},'Design removed from library. Its roster copies are unchanged. Use Undo removal to restore it.');};actions.append(remove);card.append(actions);libraryList.append(card);
    }
  }
  librarySearch.oninput=renderLibrary;libraryFilter.onchange=renderLibrary;
  exportLibrary.onclick=()=>download(libraryBroken&&libraryRaw?libraryRaw:JSON.stringify(library,null,2),'iron-stars-unit-library.json');
  importLibrary.onchange=async()=>{const file=importLibrary.files[0];if(!file)return;try{if(file.size>1000000)throw Error('Library file is too large.');const next=core.mergeLibrary(library,JSON.parse(await file.text()),()=> 'design-'+crypto.randomUUID());storeLibrary(next,'Library imported. Matching designs were kept once; existing designs were preserved.');}catch(e){libraryMessage='Import failed: '+e.message+' Your library is unchanged.';renderLibrary();}finally{importLibrary.value='';}};
  undoLibrary.onclick=()=>{if(!undoDesign)return;try{const next=core.mergeLibrary(library,{schema:1,designs:[undoDesign]},()=> 'design-'+crypto.randomUUID());undoDesign=null;storeLibrary(next,'Removed design restored.');}catch(e){libraryMessage=e.message;renderLibrary();}};
  function profile(unit) { if(unit.custom)return element('span',unit.name+' · Custom');const a=element('a',unit.name);a.href=`../units/${unit.id}/index.html`;return a; }
  const cardView=element('section',undefined,'unit-card-view');cardView.hidden=true;cardView.id='unit-card-view';cardView.setAttribute('aria-labelledby','unit-card-title');get('builder-app').after(cardView);
  function showCards(id=null){
    cardView.replaceChildren();
    const heading=element('h2','Custom unit cards');heading.id='unit-card-title';heading.tabIndex=-1;cardView.append(heading);
    cardView.append(element('p','Beta · Core v0.0.14 · One card per profile. Points are for the complete unit; forms share its installed equipment.','card-note'));
    const actions=element('div',undefined,'builder-actions'),back=element('button','Back to roster'),print=element('button','Print unit cards','button');back.type=print.type='button';
    back.onclick=()=>{cardView.hidden=true;get('builder-app').hidden=false;get('army-cards').focus();};print.onclick=()=>{document.body.classList.add('printing-unit-cards');window.print();};actions.append(back,print);cardView.append(actions);
    const grid=element('div',undefined,'unit-card-grid'),rules=new Map();
    const addRule=(name,text,ref)=>{const key=ref||name+'|'+text;if(!rules.has(key))rules.set(key,{name,text,ref});};
    const cards=core.cardProfiles(current,data,id);
    print.disabled=!cards.length;
    for(const card of cards){
      const article=element('article',undefined,'unit-card');
      article.append(element('p','IRON STARS · BETA','card-brand'),element('h3',card.name+(card.profile.name?' · '+card.profile.name:'')));
      const faction=data.factions.find(f=>f.id===card.faction),selected=core.affiliation(card.faction,card.subfaction,data);
      article.append(element('p',`${faction.name}${selected?' · '+selected.name:''}`,'card-meta'),element('p',`${card.points} pts per unit · ${card.quantity} in roster · ${card.chassis.name}`,'card-meta'));
      const stats=element('dl',undefined,'card-stats');for(const [label,value] of [['Move',`${card.profile.movement} cm`],['Defence',card.profile.defence],['Structure',String(card.profile.structure)]]){const item=element('div');item.append(element('dt',label),element('dd',value));stats.append(item);}article.append(stats);
      if(card.profile.movement_rules?.length){article.append(element('p',`Movement: ${card.profile.movement_label}${card.profile.movement_type==='wheeled'?' · +5 cm only on entirely Open Ground moves':''}`,'card-mode-rule'));for(const rule of card.profile.movement_rules)addRule(card.profile.movement_label,rule.text,rule.source_ref);}
      article.append(element('h4','Weapons'));
      if(!card.weapons.length)article.append(element('p','No weapons in this profile.'));
      for(const weapon of card.weapons){
        const section=element('div',undefined,'card-equipment');section.append(element('strong',`${weapon.quantity}× ${weapon.part.name}${weapon.part.variant?' — '+weapon.part.variant:''}${weapon.linked?' · Linked · total FP '+weapon.cost.fp:''}`));
        for(const detail of weapon.part.details)section.append(element('p',`${detail.label}: ${detail.text}`));
        if(card.ammo_target===weapon.group-1)section.append(element('p','Ammo Bin target'));
        for(const rule of [...(weapon.part.help_keywords||[]),...(weapon.part.help_rules||[])])addRule(rule.label,rule.text,rule.source_ref);
        if(weapon.linked&&data.custom.linked_rule)addRule('Linked',data.custom.linked_rule.text,data.custom.linked_rule.source_ref);
        article.append(section);
      }
      if(card.systems.length){article.append(element('h4','Systems & traits'));for(const part of card.systems){const section=element('div',undefined,'card-equipment');section.append(element('strong',part.name));if(part.name!=='Transform')for(const detail of part.details)section.append(element('p',`${detail.label}: ${detail.text}`));for(const rule of part.help_rules||[])addRule(part.name,rule.text,rule.source_ref);article.append(section);}}
      if(card.transform)for(const rule of data.custom.transform_rules||[])article.append(element('p',rule.text,'card-mode-rule'));
      if(card.profile.flyer){article.append(element('p',`Flyer${card.faction==='unmc'?' · No melee weapons':''}. See Flyer rules on the reference sheet.`,'card-mode-rule'));addRule('Flyer',data.custom.flyer_rule.text,data.custom.flyer_rule.source_ref);}
      article.append(element('p','Weapon keyword and faction rules follow on the reference sheet.','card-note'));grid.append(article);
    }
    cardView.append(grid);
    if(!cards.length)cardView.append(element('p','Add a custom unit to your roster to create its cards.'));
    if(cards.length)for(const rule of core.benefits(current,data))addRule(rule.name,rule.text,rule.source_ref);
    if(rules.size){const reference=element('section',undefined,'card-rule-reference');reference.append(element('h3','Rules reference'));for(const rule of rules.values()){const section=element('section');section.append(element('h4',rule.name),element('p',rule.text));if(rule.ref)section.dataset.sourceRef=rule.ref;reference.append(section);}cardView.append(reference);}
    get('builder-app').hidden=true;cardView.hidden=false;heading.focus();
  }
  function importDetails(unit, price) {
    const origin=data.factions.find(f=>f.id===unit.faction).name;
    return element('p',`Southern Cross import from ${origin}. ${price.base} base + ${price.chassisTax} chassis tax (${unit.southern_cross.tier}) + ${price.sourceModifier} source modifier = ${price.total} pts. Original faction, subfaction, and detachment bonuses do not apply.`,'small-note');
  }
  function showQuickReference(){
    cardView.replaceChildren();const heading=element('h2','Army quick reference');heading.id='unit-card-title';heading.tabIndex=-1;cardView.append(heading);
    const faction=data.factions.find(f=>f.id===current.faction),summary=core.summarize(current,data);
    cardView.append(element('p',`${current.name.trim()||'My force'} · ${faction.name} · ${summary.total} / ${current.limit} pts`),element('p','Beta · Core v0.0.14 and approved author additions. Rules used by this selected force; conditions and source wording are retained.','card-note'));
    const actions=element('div',undefined,'builder-actions'),back=element('button','Back to roster'),print=element('button','Print quick reference','button');back.type=print.type='button';back.onclick=()=>{cardView.hidden=true;get('builder-app').hidden=false;get('army-reference').focus();};print.onclick=()=>{document.body.classList.add('printing-unit-cards');window.print();};actions.append(back,print);cardView.append(actions);
    const rules=core.quickReference(current,data);print.disabled=!rules.length;
    if(!rules.length)cardView.append(element('p','Add units to this roster to create its quick reference.'));
    let category=null,group;
    for(const rule of rules){
      if(rule.category!==category){category=rule.category;group=element('section',undefined,'army-reference-group');group.append(element('h3',category));cardView.append(group);}
      const article=element('article',undefined,'army-reference-rule');article.dataset.sourceRefs=rule.source_refs.join(' ');article.append(element('h4',rule.name),element('p',rule.text),element('p','Used by: '+rule.used_by.join('; '),'card-note'));group.append(article);
    }
    get('builder-app').hidden=true;cardView.hidden=false;heading.focus();
  }
  function renderAvailable() {
    const query=get('army-search').value.toLocaleLowerCase().trim();
    const factionUnits=data.units.filter(u=>core.cost(u,current.faction,data));
    const importing=current.faction===data.import_rules.faction;
    const selected=core.affiliation(current.faction,current.subfaction,data);
    get('import-rules').hidden=!importing;
    const visible=factionUnits.filter(u=>[u.name,u.role,importing?data.factions.find(f=>f.id===u.faction).name:selected?.name||''].join(' ').toLocaleLowerCase().includes(query));
    const container=get('army-available');container.replaceChildren();
    get('available-count').textContent=`${visible.length} of ${factionUnits.length} available premades`;
    if(!factionUnits.length) container.append(element('p', ['fourth-imperium','living-dominion'].includes(current.faction) ? 'This faction is still in development; no premades are available yet.' : 'No premades with complete costs and resolved profiles are available for this faction yet.'));
    else if(!visible.length) container.append(element('p','No matching units. Try another search.'));
    for(const unit of visible) {
      const card=element('article',undefined,'builder-unit');
      const h=element('h3');h.append(profile(unit));card.append(h);
      const price=core.cost(unit,current.faction,data);
      card.append(element('p',[unit.role,price.imported?null:selected?.name].filter(Boolean).join(' · '),'small-note'));
      if(price.imported)card.append(importDetails(unit,price));
      const bottom=element('div',undefined,'builder-unit-bottom');bottom.append(element('strong',`${price.total} pts`));
      const button=element('button','Add unit','button');button.type='button';button.setAttribute('aria-label',`Add ${unit.name}`);
      button.onclick=()=>{try{current=core.add(current,unit.id,data);save();renderRoster();}catch(e){get('transfer-status').textContent=e.message;}};
      bottom.append(button);card.append(bottom);container.append(card);
    }
  }
  function renderSummary() {
    const summary=core.summarize(current,data);
    get('roster-title').textContent=current.name.trim()||'My force';
    get('army-faction-name').textContent=data.factions.find(f=>f.id===current.faction).name;
    const selected=core.affiliation(current.faction,current.subfaction,data),traits=get('army-traits');traits.replaceChildren();
    if(selected)traits.append(element('h3',selected.name));
    for(const rule of core.benefits(current,data)){
      if(!rule.text.startsWith('Trait:'))traits.append(element('h4',rule.name));
      const body=element('p',rule.text);body.dataset.sourceRef=rule.source_ref||(rule.source_refs||[]).join(' ');traits.append(body);
    }
    if(selected&&!selected.trait)traits.append(element('p','All Wild Hosts use Renewal of Flesh; this Host has no separate trait.','small-note'));
    get('army-budget').textContent=`${summary.total} / ${current.limit} pts`;
    get('army-budget').classList.toggle('over-limit',summary.overLimit);
    get('army-validation').textContent=summary.overLimit?`${-summary.remaining} points over limit.`:`${summary.remaining} points remaining · ${summary.count} ${summary.count===1?'unit':'units'}`;
  }
  function premadeReference(unit,imported){
    const ref=unit.reference,details=element('details',undefined,'premade-reference');
    details.append(element('summary','Unit profile and loadout'));
    if(!ref){details.append(element('p','Open the unit profile for its source details.'));return details;}
    if(ref.chassis)details.append(element('p',`Chassis: ${ref.chassis.text}`));
    for(const p of ref.profiles){
      const fields=[['movement','Move'],['defence','Defence'],['structure','STR']].map(([key,label])=>`${label} ${p.fields[key]?.text||'not specified'}`);
      details.append(element('p',`${p.name}: ${fields.join(' · ')}`,'roster-profile'));
    }
    if(!ref.profiles.length)details.append(element('p','Movement, Defence, and Structure are not specified in this source profile.'));
    function rules(title,items){if(!items.length)return;details.append(element('h4',title));const list=element('ul');for(const item of items){const li=element('li',item.text);li.dataset.sourceRef=item.source_ref;list.append(li);}details.append(list);}
    if(ref.weapons.length){details.append(element('h4','Weapons'));for(const w of ref.weapons){const entry=element('div',undefined,'roster-weapon');if(w.mode)entry.append(element('strong',w.mode));for(const f of w.fields){const p=element('p',(f.label==='Profile'?'':f.label+': ')+f.text);p.dataset.sourceRef=f.source_ref;entry.append(p);}for(const note of [...w.availability,...w.drawbacks])entry.append(element('p',note.text));details.append(entry);}}
    // Source-era subfaction grants are replaced by the selected current-core
    // affiliation. Paid stock systems remain part of the complete premade.
    const systems=ref.systems.filter(s=>!s.source_faction_bonus);
    if(systems.length){details.append(element('h4','Systems & traits'));for(const s of systems){details.append(element('strong',s.name));for(const rule of s.rules){const p=element('p',rule.text);p.dataset.sourceRef=rule.source_ref;details.append(p);}}}
    rules('Mode rules',ref.mode_rules);rules('Special rules',ref.special_rules);
    for(const child of ref.spawned_units)rules(`Spawned unit: ${child.name}`,child.rules);
    return details;
  }
  function renderRoster() {
    renderSummary();
    const container=get('army-lines');container.replaceChildren();
    if(!current.lines.length)container.append(element('p','Your roster is empty. Add a premade to start.'));
    for(const line of current.lines) {
      const unit=core.resolve(line,current.faction,data,current.subfaction), row=element('article',undefined,'roster-line');
      const h=element('h3');h.append(profile(unit));row.append(h);
      const selected=core.affiliation(current.faction,current.subfaction,data);
      if(selected)row.append(element('p',selected.name+(selected.trait?' · '+selected.trait.name:''),'roster-affiliation'));
      const price=core.cost(unit,current.faction,data);
      if(price.imported)row.append(importDetails(unit,price));
      if(unit.custom){
        if(unit.calculation.forms?.length){
          const table=element('table',undefined,'roster-forms');table.append(element('caption','Transform profiles'));
          const head=element('thead'),headRow=element('tr');for(const title of ['Form','Move','Def.','STR']){const cell=element('th',title);cell.scope='col';if(title==='Def.')cell.setAttribute('aria-label','Defence');headRow.append(cell);}head.append(headRow);table.append(head);
          const body=element('tbody');for(const form of unit.calculation.forms){const tr=element('tr'),name=element('th',form.name);name.scope='row';tr.append(name,element('td',`${form.movement} cm`),element('td',form.defence),element('td',String(form.structure)));body.append(tr);}table.append(body);row.append(table);
          for(const rule of data.custom.transform_rules||[])row.append(element('p',rule.text,'transform-source-rule'));
          for(const form of unit.calculation.forms)if(form.movement_rules?.length){row.append(element('p',`${form.name} movement: ${form.movement_label}`,'transform-source-rule'));for(const rule of form.movement_rules)row.append(element('p',rule.text,'transform-source-rule'));}
          if(current.faction==='unmc'&&unit.calculation.forms.some(f=>f.flyer))row.append(element('p',`Flyer form: ${data.custom.flyer_rule.text}`,'transform-source-rule'));
        }else row.append(element('p',`Move ${unit.custom.movement} cm · Defence ${unit.calculation.defence} · STR ${unit.custom.structure}`));
        const details=element('details'),summary=element('summary','Custom loadout and costs'),list=element('ul');details.append(summary,list);
        for(const part of unit.calculation.breakdown){
          const li=element('li',`${part.name}: ${part.quantity} ${part.quantity===1?'copy':'copies'}${part.linked?' (linked, total FP '+part.fp+')':''} = ${part.total} pts`);
          if(part.forms)li.append(element('p',`Available in: ${part.forms.join(' / ')}`,'form-availability'));
          const definition=data.custom.parts.find(p=>p.id===part.component_id);
          for(const detail of definition.details){
            const profileStat=definition.kind==='chassis'&&unit.calculation.forms.length&&/^(move|movement|m|defence|def|d|structure|str)$/i.test(detail.label);
            if(definition.name!=='Transform'&&!profileStat)li.append(element('p',`${detail.label}: ${detail.text}`,'small-note'));
          }
          const link=element('a','Armory reference ↗');link.href=`../armory/index.html#${definition.armory_id}`;li.append(link);list.append(li);
        }
        if(unit.custom.ammo_target!==undefined)details.append(element('p',`Ammo Bin applies to weapon group ${unit.custom.ammo_target+1}.`));
        for(const note of unit.calculation.warnings)details.append(element('p',note));row.append(details);
        const unitActions=element('div',undefined,'builder-actions');row.append(unitActions);
        const edit=element('button','Edit custom unit');edit.type='button';edit.onclick=()=>customUI.edit(line);unitActions.append(edit);
        const duplicate=element('button','Duplicate');duplicate.type='button';duplicate.setAttribute('aria-label',`Duplicate ${unit.name}`);duplicate.onclick=()=>{try{const id='custom-'+crypto.randomUUID();current=core.duplicateCustom(current,line.id,id,data);save();renderRoster();customUI.edit(current.lines.find(l=>l.id===id));get('custom-name').select();get('transfer-status').textContent='Copy added as one unit. Edit its name and equipment above; the original is unchanged.';}catch(e){get('transfer-status').textContent=e.message;}};unitActions.append(duplicate);
        const cards=element('button','View unit cards');cards.type='button';cards.onclick=()=>showCards(line.id);unitActions.append(cards);
        const saveDesign=element('button','Save to library');saveDesign.type='button';saveDesign.disabled=libraryBroken;saveDesign.setAttribute('aria-label',`Save ${unit.name} to library`);saveDesign.onclick=()=>{try{const next=core.saveDesign(library,current,line.id,'design-'+crypto.randomUUID(),data);const message=next.designs.length===library.designs.length?'This design is already saved in your library.':'Design saved to your library.';storeLibrary(next,message);get('transfer-status').textContent=message;}catch(e){get('transfer-status').textContent=e.message;}};unitActions.append(saveDesign);
      }else row.append(premadeReference(unit,price.imported));
      const controls=element('div',undefined,'roster-controls');
      const label=element('label','Quantity '),input=element('input');input.type='number';input.min='1';input.max='999';input.step='1';input.value=line.quantity;input.setAttribute('aria-label',`Quantity for ${unit.name}`);
      const subtotal=element('span',`${line.quantity} × ${price.total} pts = ${price.total*line.quantity} pts`);
      input.oninput=()=>{const qty=Number(input.value);if(!Number.isInteger(qty)||qty<1||qty>999){input.setCustomValidity('Enter a whole quantity from 1 to 999.');get('transfer-status').textContent='Enter a whole quantity from 1 to 999; the previous quantity is still used.';return;}input.setCustomValidity('');line.quantity=qty;get('transfer-status').textContent='';subtotal.textContent=`${qty} × ${price.total} pts = ${price.total*qty} pts`;save();renderSummary();};
      label.append(input);controls.append(label,subtotal);
      const remove=element('button','Remove');remove.type='button';remove.setAttribute('aria-label',`Remove ${unit.name}`);remove.onclick=()=>{current.lines=current.lines.filter(l=>l.id!==unit.id);save();renderRoster();};
      controls.append(remove);row.append(controls);container.append(row);
    }
  }
  function render() {
    get('army-faction').value=current.faction;get('army-name').value=current.name;get('army-limit').value=current.limit;
    const faction=data.factions.find(f=>f.id===current.faction),select=get('army-subfaction');select.replaceChildren();
    get('army-subfaction-label').textContent=faction.affiliation_label||'Subfaction';
    const none=element('option',faction.subfactions?.length?'None selected':'No formal subfactions');none.value='';select.append(none);
    for(const s of faction.subfactions||[]){const option=element('option',s.name);option.value=s.id;select.append(option);}
    select.disabled=!faction.subfactions?.length;select.value=current.subfaction||'';renderAvailable();renderRoster();renderLibrary();
    const held=heldRecord?.roster;
    renderRosterManager();
    document.querySelector('.builder-layout').inert=!!heldRecord;
    get('custom-editor').inert=!!heldRecord;
    for(const id of ['army-name','army-limit'])get(id).disabled=!!heldRecord;
    if(heldRecord)select.disabled=true;
    recovery.hidden=!heldRecord;recovery.replaceChildren();
    if(heldRecord){
      recovery.append(element('p','This saved roster uses options that are no longer supported. Its original copy is preserved. You can export it or repair the unsupported options: remove Transform from unsupported factions and move UNMC Flyer melee assignments to Mech when needed. Installed weapons and quantities are kept.'));
      const exportOriginal=element('button','Export original roster');exportOriginal.type='button';exportOriginal.onclick=()=>download(JSON.stringify(held,null,2),'iron-stars-original-roster.json');recovery.append(exportOriginal);
      const repair=element('button','Repair unsupported options and keep roster');repair.type='button';repair.onclick=()=>{try{const repaired=core.repairLegacyTransforms(held,data);if(repaired.faction!==current.faction)throw Error('Saved faction does not match.');current=repaired;heldRecord=null;save();render();customUI.refresh();}catch(e){get('save-status').textContent=`Roster preserved: ${e.message}`;}};recovery.append(repair);
    }
  }
  const recovery=element('section',undefined,'pending');recovery.id='roster-recovery';recovery.setAttribute('aria-label','Saved roster recovery');get('save-status').after(recovery);
  function download(text,name){const url=URL.createObjectURL(new Blob([text],{type:'application/json'})),a=element('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  get('army-faction').onchange=()=>{try{save();chooseFaction(get('army-faction').value);finishRosterSwitch('Faction selected.');}catch(e){get('army-faction').value=current.faction;managerStatus.textContent=e.message;}};
  get('army-subfaction').onchange=()=>{try{current=core.validate({...current,subfaction:get('army-subfaction').value||null},data);save();render();customUI.affiliationChanged();}catch(error){get('army-subfaction').value=current.subfaction||'';get('transfer-status').textContent=error.message;}};
  get('army-name').oninput=()=>{current.name=get('army-name').value;save();renderRoster();renderRosterManager();};
  get('army-limit').oninput=()=>{const n=Number(get('army-limit').value);if(!Number.isSafeInteger(n)||n<1||n>1000000){get('army-limit').setCustomValidity('Enter a whole limit from 1 to 1,000,000.');get('army-validation').textContent='Enter a valid points limit; the previous limit is still used.';return;}get('army-limit').setCustomValidity('');current.limit=n;save();renderRoster();renderRosterManager();};
  get('army-search').oninput=renderAvailable;
  const cardsButton=element('button','Custom unit cards');cardsButton.type='button';cardsButton.id='army-cards';cardsButton.onclick=()=>showCards();get('army-print').after(cardsButton);
  const referenceButton=element('button','Army quick reference');referenceButton.type='button';referenceButton.id='army-reference';referenceButton.onclick=showQuickReference;cardsButton.after(referenceButton);
  const battleButton=element('button','Battle tracker');battleButton.type='button';battleButton.id='army-battle';referenceButton.after(battleButton);
  get('army-export').onclick=()=>{const url=URL.createObjectURL(new Blob([core.encode(current,data)],{type:'application/json'}));const a=element('a');a.href=url;a.download='iron-stars-roster.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);get('transfer-status').textContent='Roster exported with current unit selections.';};
  get('army-import').onchange=async()=>{const file=get('army-import').files[0];if(!file)return;try{if(file.size>1000000)throw Error('Roster file is too large.');const roster=core.decode(await file.text(),data);save();const id='roster-'+crypto.randomUUID();collection=core.addRoster(collection,roster,id,data);activateRoster(id);get('army-search').value='';save();render();customUI.refresh();get('transfer-status').textContent='Roster imported as a new saved force. Points recalculated using current prices.';}catch(e){get('transfer-status').textContent=`Import failed: ${e.message} Your current roster is unchanged.`;}finally{get('army-import').value='';}};
  let printClosed=[],printing=false;
  function preparePrint(){if(!cardView.hidden){document.body.classList.add('printing-unit-cards');return;}if(printing)return;printing=true;printClosed=[...document.querySelectorAll('#army-lines details:not([open])')];printClosed.forEach(d=>d.open=true);}
  window.addEventListener('beforeprint',preparePrint);
  window.addEventListener('afterprint',()=>{document.body.classList.remove('printing-unit-cards');printClosed.forEach(d=>d.open=false);printClosed=[];printing=false;});
  get('army-print').onclick=()=>{preparePrint();window.print();};
  const customUI=window.IronCustomUI(data,()=>current,(id,definition)=>{current=core.saveCustom(current,id,definition,data);save();renderRoster();get('transfer-status').textContent='Custom unit saved to roster.';});
  const battleUI=window.IronBattleUI(data,()=>current,()=>activeId,download);
  battleButton.onclick=()=>{try{battleUI.open();}catch(e){get('transfer-status').textContent=e.message;}};
  const guide=get('builder-guide');
  if(guide){
    guide.open=!storedOriginal&&!collectionBroken;
    const summary=guide.querySelector('summary'),dismiss=get('builder-guide-dismiss');dismiss.hidden=false;
    dismiss.onclick=()=>{guide.open=false;summary.focus();};
    guide.addEventListener('keydown',e=>{if(e.key==='Escape'&&guide.open){guide.open=false;summary.focus();e.preventDefault();}});
    for(const button of guide.querySelectorAll('[data-guide-target]')){
      button.hidden=false;button.onclick=()=>{
        let target=get(button.dataset.guideTarget);
        if(button.dataset.guideTarget==='custom-editor'&&target?.hidden){target=get('custom-locked');get('builder-guide-status').textContent='Southern Cross uses stock imports. Use Find premades for this faction.';}
        else get('builder-guide-status').textContent='';
        if(!target||target.hidden)return;
        if(target.tagName==='DETAILS')target.open=true;
        const focus=target.tagName==='DETAILS'?target.querySelector('summary'):target;
        if(!focus.matches('a,button,input,select,textarea,summary'))focus.tabIndex=-1;
        document.querySelectorAll('.builder-guide-target').forEach(node=>node.classList.remove('builder-guide-target'));
        focus.classList.add('builder-guide-target');focus.scrollIntoView({block:'center'});focus.focus({preventScroll:true});
      };
    }
  }
  get('builder-app').hidden=false;render();customUI.refresh();save();
})();
