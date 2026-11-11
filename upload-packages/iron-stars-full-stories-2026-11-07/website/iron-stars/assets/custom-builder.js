window.IronCustomUI = function(data, getRoster, onSave) {
  'use strict';
  const core=window.IronCustom, get=id=>document.getElementById(id);
  let editing=null,weapons=[],systems=new Set(),forms=null;
  function el(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
  function label(part){return part.name+(part.variant?' — '+part.variant:'')+` (${part.price} ${part.price===1?'pt':'pts'})`;}
  function options(select,parts){select.replaceChildren();for(const p of parts){const o=el('option',label(p));o.value=p.id;select.append(o);}}
  function find(id){return data.custom.parts.find(p=>p.id===id);}
  const help=(()=>{
    const tooltip=el('div');tooltip.id='component-help-tooltip';tooltip.className='component-tooltip';tooltip.setAttribute('role','tooltip');tooltip.hidden=true;document.body.append(tooltip);
    let active=null,pinned=false,timer;
    function hide(){clearTimeout(timer);if(active){active.button.removeAttribute('aria-describedby');active.button.setAttribute('aria-expanded','false');}active=null;pinned=false;tooltip.hidden=true;}
    function show(item,pin=false){
      const part=item.part();if(!part)return;clearTimeout(timer);
      if(active&&active!==item){active.button.removeAttribute('aria-describedby');active.button.setAttribute('aria-expanded','false');}
      active=item;pinned=pin;tooltip.replaceChildren(el('strong',label(part)));
      if(part.name==='Transform')tooltip.append(el('p',getRoster().faction==='unmc'?'Flyer units only: Mech → Hybrid → Flyer. Hybrid/Flyer: +10 cm movement, Defence -1/-2. Structure unchanged.':'Two forms. Alternate form can choose a movement type; base Move, Defence and Structure stay at Mech values.'));
      for(const d of [...(part.name==='Transform'?data.custom.transform_rules.map(r=>({...r,label:'Rule'})):part.details),...(part.help_rules||[])])tooltip.append(el('p',`${d.label}: ${d.text}`));
      if(part.help_keywords?.length){tooltip.append(el('strong','Weapon keywords'));for(const term of part.help_keywords)tooltip.append(el('p',`${term.label}: ${term.text}`));}
      tooltip.hidden=false;item.button.setAttribute('aria-describedby',tooltip.id);item.button.setAttribute('aria-expanded','true');
      const bounds=item.host.getBoundingClientRect(),box=tooltip.getBoundingClientRect();
      tooltip.style.left=Math.max(12,Math.min(bounds.left,innerWidth-box.width-12))+'px';
      const below=bounds.bottom+8,top=below+box.height<innerHeight-12?below:bounds.top-box.height-8;
      tooltip.style.top=Math.max(12,Math.min(top,innerHeight-box.height-12))+'px';
    }
    function leave(){clearTimeout(timer);timer=setTimeout(()=>{if(active&&!pinned&&!active.host.matches(':hover')&&!tooltip.matches(':hover')&&!active.host.contains(document.activeElement))hide();},180);}
    function attach(host,part){
      const button=el('button','ⓘ');button.type='button';button.className='component-help';button.setAttribute('aria-controls',tooltip.id);button.setAttribute('aria-expanded','false');
      const item={host,button,part};
      function refresh(){const p=part();button.setAttribute('aria-label',`Explain ${p?.name||'component'}`);if(active===item)show(item,pinned);}
      refresh();host.append(button);
      host.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')show(item);});host.addEventListener('pointerleave',leave);
      host.addEventListener('focusin',()=>show(item));host.addEventListener('focusout',leave);
      button.onclick=()=>{if(active===item&&pinned)hide();else show(item,true);};
      return refresh;
    }
    tooltip.addEventListener('pointerenter',()=>clearTimeout(timer));tooltip.addEventListener('pointerleave',leave);
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&active){hide();e.preventDefault();}else if(active&&document.activeElement===active.button&&['ArrowDown','ArrowUp','PageDown','PageUp'].includes(e.key)){tooltip.scrollBy({top:(e.key==='ArrowUp'||e.key==='PageUp'?-1:1)*(e.key.startsWith('Page')?tooltip.clientHeight:40)});e.preventDefault();}});
    document.addEventListener('pointerdown',e=>{if(active&&!active.host.contains(e.target)&&!tooltip.contains(e.target))hide();});
    window.addEventListener('resize',hide);window.addEventListener('scroll',e=>{if(!tooltip.contains(e.target))hide();},true);
    return {attach,hide};
  })();
  const refreshChassisHelp=help.attach(get('custom-chassis-help'),()=>find(get('custom-chassis').value));
  function showDetails(part){
    const box=get('custom-part-details');box.replaceChildren();if(!part)return;
    box.append(el('strong',label(part)));
    for(const d of part.name==='Transform'?data.custom.transform_rules.map(r=>({...r,label:'Rule'})):part.details)box.append(el('p',`${d.label}: ${d.text}`));
    const a=el('a','View in Armory ↗');a.href=`../armory/index.html#${part.armory_id}`;box.append(a);
  }
  function range(select,values,value){select.replaceChildren();for(let n=values[0];n<=values[1];n++){const o=el('option',String(n));o.value=n;select.append(o);}select.value=value===undefined?values[0]:value;}
  function chassisChanged(definition){
    const p=find(get('custom-chassis').value);if(!p)return;
    range(get('custom-movement'),p.movement,definition?.movement);range(get('custom-structure'),p.structure,definition?.structure);
    get('custom-defence').textContent=`Defence ${p.defence}`;showDetails(p);refreshChassisHelp();
  }
  function input(){const definition={name:get('custom-name').value,chassis:get('custom-chassis').value,movement:Number(get('custom-movement').value),structure:Number(get('custom-structure').value),weapons:weapons.map(w=>({...w})),systems:[...systems],ammo_target:Number(get('custom-ammo-target').value)};if(getRoster().faction==='unmc')definition.flyer=get('custom-flyer').checked;if(forms){definition.transform_version=2;definition.forms=forms.map(f=>({...f,weapon_groups:[...f.weapon_groups],systems:[...f.systems]}));}return definition;}
  function ensureForms(){
    const transform=[...systems].find(id=>find(id)?.name==='Transform'),section=get('custom-transform'),config=core.policy(getRoster().faction,data);section.hidden=!transform||!config;
    if(!transform||!config){const changed=!!forms;forms=null;return changed;}
    let created=false;
    if(!forms){created=true;forms=config.form_names.map((name,formIndex)=>({name,weapon_groups:weapons.map((_,i)=>i).filter(n=>core.weaponAllowedInForm(find(weapons[n].component),getRoster().faction,formIndex)),systems:[...systems]}));}
    const chassis=find(get('custom-chassis').value),defence=core.baseDefence(chassis,getRoster().faction,true);
    forms.forEach((f,i)=>{if(config.fixed_names)f.name=config.form_names[i];f.movement=Number(get('custom-movement').value)+config.movement_offsets[i];f.structure=Number(get('custom-structure').value);f.systems=[...systems];
      const stats=get(`custom-form-stats-${i}`);if(stats)stats.textContent=`Move ${f.movement} cm · Defence ${Number.parseInt(defence,10)+config.defence_offsets[i]}+ · STR ${f.structure}`;
    });
    get('custom-defence').textContent=`Mech Defence ${defence}`;
    return created;
  }
  function removeWeaponGroup(index){
    const target=get('custom-ammo-target'),previous=target.value;
    weapons.splice(index,1);
    if(forms)for(const f of forms)f.weapon_groups=f.weapon_groups.filter(n=>n!==index).map(n=>n>index?n-1:n);
    if(previous!=='')target.value=Number(previous)===index?'':String(Number(previous)>index?Number(previous)-1:Number(previous));
  }
  function weaponChoices(groupIndex=null,formIndex=null){
    return core.parts(data,getRoster().faction,'weapon',getRoster().subfaction).filter(p=>
      (formIndex===null||core.weaponAllowedInForm(p,getRoster().faction,formIndex))&&
      (!forms||groupIndex===null||forms.every((f,i)=>!f.weapon_groups.includes(groupIndex)||core.weaponAllowedInForm(p,getRoster().faction,i))));
  }
  function renderForms(){
    ensureForms();const box=get('custom-forms');box.replaceChildren();if(!forms)return;
    const config=core.policy(getRoster().faction,data);
    get('custom-transform-rules').textContent=(data.custom.transform_rules||[]).map(r=>r.text).join('\n')+'\n'+(config.flyer_only?'UNMC flyer units: Mech → Hybrid → Flyer. Hybrid and Flyer gain +10 cm movement; Defence is Mech -1 and Mech -2 respectively. Structure stays at its Mech value.':'Cybernetic Rebellion: two forms. Choose the alternate movement type below. Base Move, Defence and Structure stay at the Mech values; movement traits apply their own conditions.');
    const chassis=find(get('custom-chassis').value);
    forms.forEach((form,i)=>{
      const field=el('fieldset');field.className='custom-form-profile';field.append(el('legend',`Form ${i+1}`));
      const nameLabel=el('label','Form name'),name=el('input');name.value=form.name;name.maxLength=60;name.setAttribute('aria-label',`Name for form ${i+1}`);nameLabel.append(name);field.append(nameLabel);
      name.readOnly=config.fixed_names;name.oninput=()=>{form.name=name.value;calculate();};
      const stats=el('p');stats.id=`custom-form-stats-${i}`;stats.textContent=`Move ${form.movement} cm · Defence ${Number.parseInt(core.baseDefence(chassis,getRoster().faction,true),10)+config.defence_offsets[i]}+ · STR ${form.structure}`;field.append(stats);
      if(getRoster().faction==='cybernetic-rebellion'&&i===1){
        const label=el('label','Movement type'),select=el('select'),unchanged=el('option','Unchanged Mech movement');unchanged.value='standard';select.append(unchanged);
        for(const type of data.custom.movement_types){const option=el('option',type.name);option.value=type.id;select.append(option);}
        select.value=form.movement_type||'standard';select.setAttribute('aria-label','Alternate form movement type');label.append(select);field.append(label);
        const explanation=el('div');explanation.className='transform-source-rule';field.append(explanation);
        const explain=()=>{const type=data.custom.movement_types.find(t=>t.id===select.value);explanation.replaceChildren();for(const rule of type?.rules||[])explanation.append(el('p',rule.text));if(!type)explanation.append(el('p','Uses the Mech movement rules. Choose a type to give this alternate form its movement behavior.'));};
        explain();select.onchange=()=>{form.movement_type=select.value;explain();calculate();};
      }
      field.append(el('strong','Weapon loadout'));
      if(getRoster().faction==='unmc'&&i===2)field.append(el('p','UNMC Flyer form cannot use melee weapons.'));
      if(!form.weapon_groups.length)field.append(el('p','No weapons assigned to this form. Add a weapon below.'));
      weapons.forEach((w,n)=>{
        if(form.weapon_groups.includes(n)){
          const group=el('fieldset');group.className='form-weapon-editor';group.append(el('legend',`Weapon group ${n+1}`));
          const select=el('select');select.setAttribute('aria-label',`Weapon group ${n+1} weapon in form ${i+1}`);options(select,weaponChoices(n,i));select.value=w.component;
          const choice=el('div');choice.className='part-help';choice.append(select);help.attach(choice,()=>find(w.component));group.append(choice);
          const copies=el('label','Copies'),qty=el('input');qty.type='number';qty.min=1;qty.max=99;qty.step=1;qty.value=w.quantity;qty.setAttribute('aria-label',`Weapon group ${n+1} copies in form ${i+1}`);copies.append(qty);group.append(copies);
          const linkLabel=el('label',' Linked ranged weapons'),link=el('input');link.type='checkbox';link.checked=w.linked;link.disabled=!find(w.component)?.fp;link.setAttribute('aria-label',`Link weapon group ${n+1} in form ${i+1}`);linkLabel.prepend(link);group.append(linkLabel);
          const shared=forms.filter(f=>f.weapon_groups.includes(n));
          if(shared.length>1)group.append(el('p',`Shared with ${shared.filter(f=>f!==form).map(f=>f.name).join(' / ')}. Editing this group changes it in those forms too.`));
          const refresh=()=>{help.hide();renderWeapons();renderForms();calculate();};
          select.onchange=()=>{w.component=select.value;if(!find(w.component)?.fp)w.linked=false;refresh();};
          qty.oninput=()=>{w.quantity=Number(qty.value);calculate();};qty.onchange=refresh;
          link.onchange=()=>{w.linked=link.checked;refresh();};
          const remove=el('button','Remove from this form');remove.type='button';remove.onclick=()=>{
            form.weapon_groups=form.weapon_groups.filter(x=>x!==n);
            if(!forms.some(f=>f.weapon_groups.includes(n)))removeWeaponGroup(n);
            refresh();
          };group.append(remove);field.append(group);return;
        }
        const p=find(w.component);if(!core.weaponAllowedInForm(p,getRoster().faction,i))return;
        const label=el('label'),check=el('input');check.type='checkbox';check.checked=form.weapon_groups.includes(n);check.setAttribute('aria-label',`Weapon group ${n+1} in form ${i+1}`);
        label.className='form-equipment-choice';label.append(check,document.createTextNode(` Share group ${n+1}: ${p?.name||'Unavailable'} · ${w.quantity} ${w.quantity===1?'copy':'copies'}${w.linked?' (linked)':''}`));field.append(label);
        check.onchange=()=>{if(check.checked)form.weapon_groups.push(n);renderWeapons();renderForms();calculate();};
      });
      const add=el('button','Add weapon to this form');add.type='button';add.setAttribute('aria-label',`Add weapon to form ${i+1}`);add.onclick=()=>{
        const p=weaponChoices(null,i)[0];if(!p)return;
        weapons.push({component:p.id,quantity:1,linked:false});form.weapon_groups.push(weapons.length-1);renderWeapons();renderForms();calculate();
      };field.append(add);
      field.append(el('p','Installed systems are shared across forms. Their own conditions still apply.'));if(config.flyer_only&&i===2)field.append(el('strong','Flyer movement rules apply in this form.'));box.append(field);
    });
  }
  function labelPart(p){return p?p.name+(p.variant?' — '+p.variant:''):'Unavailable component';}
  function calculate(){
    if(ensureForms())renderForms();
    const ammo=systems.size&&[...systems].some(id=>find(id).requires_ammunition),target=get('custom-ammo-target'),previous=target.value;
    get('custom-ammo-label').hidden=!ammo;
    target.replaceChildren();
    const empty=el('option','Choose an Ammunition weapon');empty.value='';target.append(empty);
    weapons.forEach((w,i)=>{const p=find(w.component);if(p&&p.details.some(d=>/\bAmmunition\b/i.test(d.text))){const o=el('option',`${i+1}: ${p.name}`);o.value=i;target.append(o);}});
    if([...target.options].some(o=>o.value===previous))target.value=previous;
    const body=get('custom-breakdown');body.replaceChildren();
    try{
      const definition=input();if(ammo&&target.value==='')definition.ammo_target=null;
      const result=core.calculate(definition,getRoster().faction,data,{subfaction:getRoster().subfaction});
      get('custom-defence').textContent=`${result.forms.length?'Mech ':''}Defence ${result.defence}`;
      for(const row of result.breakdown){const line=el('li',`${row.name}: ${row.quantity} × ${row.unit_price} pts${row.linked?' (linked copies: '+row.copy_prices.join(' / ')+')':''} = ${row.total} pts${row.forms?' · '+row.forms.join(' / '):''}`);body.append(line);}
      get('custom-total').textContent=`${result.total} pts`;
      get('custom-error').textContent=result.warnings.join(' ');get('custom-save').disabled=false;
      return result.unit;
    }catch(e){get('custom-total').textContent='Incomplete unit';get('custom-error').textContent=e.message;get('custom-save').disabled=true;return null;}
  }
  function renderWeapons(){
    const container=get('custom-weapons');container.replaceChildren();
    
    weapons.forEach((w,i)=>{
      const row=el('fieldset'),legend=el('legend',`Weapon group ${i+1}`);row.append(legend);
      const select=el('select');select.setAttribute('aria-label',`Weapon in group ${i+1}`);options(select,weaponChoices(i));select.value=w.component;
      const choice=el('div');choice.className='part-help';choice.append(select);const refreshHelp=help.attach(choice,()=>find(w.component));
      const qtyLabel=el('label','Copies in this group'),qty=el('input');qty.type='number';qty.min=1;qty.max=99;qty.step=1;qty.value=w.quantity;qty.setAttribute('aria-label',`Weapon copies in group ${i+1}`);qtyLabel.append(qty);
      const linkedLabel=el('label',' Linked (identical ranged weapons)'),linked=el('input');linked.type='checkbox';linked.checked=w.linked;linked.disabled=!find(w.component)?.fp;linked.setAttribute('aria-label',`Link weapon group ${i+1}`);linkedLabel.prepend(linked);
      const remove=el('button','Remove group');remove.type='button';
      select.onchange=()=>{w.component=select.value;if(!find(w.component).fp){w.linked=false;linked.checked=false;}linked.disabled=!find(w.component).fp;showDetails(find(w.component));refreshHelp();renderForms();calculate();};
      qty.oninput=()=>{w.quantity=Number(qty.value);renderForms();calculate();};linked.onchange=()=>{w.linked=linked.checked;renderForms();calculate();};
      remove.onclick=()=>{help.hide();removeWeaponGroup(i);renderWeapons();renderForms();calculate();};row.append(choice,qtyLabel,linkedLabel,remove);container.append(row);
    });
  }
  function renderSystems(){
    const container=get('custom-systems');container.replaceChildren();
    for(const part of core.parts(data,getRoster().faction,'system',getRoster().subfaction)){
      const needsFlyer=part.name==='Transform'&&core.policy(getRoster().faction,data)?.flyer_only&&!get('custom-flyer').checked;
      const l=el('label'),box=el('input');box.type='checkbox';box.value=part.id;box.checked=systems.has(part.id);box.disabled=needsFlyer&&!box.checked;l.append(box,document.createTextNode(' '+label(part)+(part.unique?' · Unique':'')+(needsFlyer?' · Check “Flyer-capable unit” above to enable':'')));
      box.onchange=()=>{if(box.checked){systems.add(part.id);if(forms)for(const f of forms)f.systems.push(part.id);}else{systems.delete(part.id);if(forms)for(const f of forms)f.systems=f.systems.filter(id=>id!==part.id);}showDetails(part);renderForms();calculate();};
      const choice=el('div');choice.className='system-choice';choice.append(l);help.attach(choice,()=>part);container.append(choice);
    }
  }
  function reset(definition,id){
    help.hide();
    editing=id||null;weapons=definition?definition.weapons.map(w=>({...w})):[];systems=new Set(definition?.systems||[]);forms=definition?.forms?definition.forms.map(f=>({...f,weapon_groups:[...f.weapon_groups],systems:[...f.systems]})):null;
    get('custom-flyer-label').hidden=getRoster().faction!=='unmc';get('custom-flyer').checked=definition?.flyer===true;
    options(get('custom-chassis'),core.parts(data,getRoster().faction,'chassis',getRoster().subfaction));
    if(definition)get('custom-chassis').value=definition.chassis;
    get('custom-name').value=definition?.name||'Custom unit';get('custom-save').textContent=editing?'Save unit changes':'Add custom unit to roster';
    chassisChanged(definition);renderWeapons();renderSystems();renderForms();calculate();
    if(definition?.ammo_target!==undefined){get('custom-ammo-target').value=definition.ammo_target;calculate();}
  }
  function refresh(){
    help.hide();
    const forbidden=data.custom.custom_forbidden.includes(getRoster().faction);
    get('custom-locked').hidden=!forbidden;get('custom-editor').hidden=forbidden;get('custom-editor').open=false;
    if(!forbidden)reset();
  }
  get('custom-chassis').onchange=()=>{chassisChanged();renderForms();calculate();};
  get('custom-flyer').onchange=()=>{renderSystems();renderForms();calculate();};
  for(const id of ['custom-name','custom-movement','custom-structure','custom-ammo-target'])get(id).oninput=calculate;
  get('custom-add-weapon').onclick=()=>{const p=core.parts(data,getRoster().faction,'weapon',getRoster().subfaction)[0];if(p){weapons.push({component:p.id,quantity:1,linked:false});if(forms)forms.forEach((f,i)=>{if(core.weaponAllowedInForm(p,getRoster().faction,i))f.weapon_groups.push(weapons.length-1);});renderWeapons();renderForms();showDetails(p);calculate();}};
  get('custom-cancel').onclick=()=>{reset();get('custom-editor').open=false;};
  get('custom-form').onsubmit=e=>{e.preventDefault();const definition=calculate();if(!definition)return;try{onSave(editing||'custom-'+crypto.randomUUID(),definition);reset();get('custom-editor').open=false;}catch(error){get('custom-error').textContent=error.message;}};
  return {refresh,affiliationChanged(){if(get('custom-editor').hidden)return;const open=get('custom-editor').open;reset(input(),editing);get('custom-editor').open=open;},edit(line){reset(line.custom,line.id);get('custom-editor').open=true;get('custom-name').focus();}};
};
