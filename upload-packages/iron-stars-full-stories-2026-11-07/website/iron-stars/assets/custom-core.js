(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.IronCustom=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function policy(faction,data){return data.custom.transform_policy?.factions[faction]||null;}
  function allowed(part,faction,data,subfaction=null){return !data.custom.custom_forbidden.includes(faction)&&(!part.allowed_factions||part.allowed_factions.includes(faction))&&(!part.allowed_subfactions||part.allowed_subfactions.includes(subfaction))&&(part.name!=='Transform'||!!policy(faction,data));}
  function baseDefence(chassis,faction,transform){return transform&&faction==='unmc'&&chassis.mech_defence?chassis.mech_defence:chassis.defence;}
  function melee(part){return part.kind==='weapon'&&part.details.some(d=>d.label.toLowerCase()==='me'||/\b(?:ME\s+\d|melee)\b/i.test(d.text));}
  function weaponAllowedInForm(part,faction,index){return !(faction==='unmc'&&index===2&&melee(part));}
  function parts(data,faction,kind,subfaction=null){return data.custom.parts.filter(p=>p.kind===kind&&allowed(p,faction,data,subfaction));}
  function linked(base,n){return Array.from({length:n},(_,i)=>base*(i<3?1:i-1)).reduce((a,b)=>a+b,0);}
  function calculate(input,faction,data,options={}){
    if(!data.custom||data.custom.custom_forbidden.includes(faction))throw Error('Southern Cross uses stock imports only; custom units are not allowed.');
    if(!data.factions.some(f=>f.id===faction))throw Error('Unknown faction.');
    const subfaction=options.subfaction||null;
    if(subfaction&&!data.factions.find(f=>f.id===faction).subfactions?.some(s=>s.id===subfaction))throw Error('This subfaction does not belong to the selected faction.');
    if(!input||typeof input.name!=='string'||!input.name.trim()||input.name.length>100)throw Error('Give your custom unit a name (up to 100 characters).');
    const find=(id,kind)=>{const p=data.custom.parts.find(p=>p.id===id&&p.kind===kind);if(!p||!allowed(p,faction,data,subfaction))throw Error('A component is unavailable or locked to another faction or subfaction.');return p;};
    const chassis=find(input.chassis,'chassis');
    const within=(n,range)=>Number.isFinite(n)&&n>=range[0]&&n<=range[1];
    if(!within(input.movement,chassis.movement)||!Number.isSafeInteger(input.structure)||!within(input.structure,chassis.structure))throw Error('Choose movement and Structure from the chassis values.');
    if(!Array.isArray(input.weapons)||input.weapons.length>100||!Array.isArray(input.systems)||input.systems.length>data.custom.parts.length)throw Error('Invalid component list.');
    const breakdown=[{component_id:chassis.id,name:chassis.name,quantity:1,unit_price:chassis.price,total:chassis.price,source_ref:chassis.source_ref}];
    const weapons=input.weapons.map(w=>{
      const p=find(w.component,'weapon');
      if(!Number.isSafeInteger(w.quantity)||w.quantity<1||w.quantity>99||typeof w.linked!=='boolean')throw Error('Weapon quantities must be whole numbers from 1 to 99.');
      if(w.linked&&(!p.fp||w.quantity<2))throw Error('Link at least two identical ranged weapons in a group.');
      const copyPrices=Array.from({length:w.quantity},(_,i)=>p.price*(w.linked&&i>=3?i-1:1));
      breakdown.push({component_id:p.id,name:p.name+(p.variant?' — '+p.variant:''),quantity:w.quantity,unit_price:p.price,total:w.linked?linked(p.price,w.quantity):p.price*w.quantity,linked:w.linked,copy_prices:copyPrices,fp:p.fp?p.fp*w.quantity:null,source_ref:p.source_ref});
      return {component:p.id,quantity:w.quantity,linked:w.linked};
    });
    const seen=new Set();let unique=0,needsAmmo=false;
    const systems=input.systems.map(id=>{
      if(seen.has(id))throw Error('A system is already selected.');seen.add(id);
      const p=find(id,'system');if(p.unique)unique++;if(p.requires_ammunition)needsAmmo=true;
      breakdown.push({component_id:p.id,name:p.name+(p.variant?' — '+p.variant:''),quantity:1,unit_price:p.price,total:p.price,source_ref:p.source_ref});return p.id;
    });
    if(unique>1)throw Error('A unit may include only one Unique trait/system.');
    let ammoTarget=null;
    if(needsAmmo){
      if(!Number.isSafeInteger(input.ammo_target)||!weapons[input.ammo_target])throw Error('Ammo Bin requires a weapon with Ammunition.');
      const p=find(weapons[input.ammo_target].component,'weapon');
      if(!p.details.some(d=>/\bAmmunition\b/i.test(d.text)))throw Error('Ammo Bin requires a weapon with Ammunition.');
      ammoTarget=input.ammo_target;
    }
    const unit={name:input.name.trim(),chassis:chassis.id,movement:input.movement,structure:input.structure,weapons,systems};
    if(needsAmmo)unit.ammo_target=ammoTarget;
    const transform=systems.find(id=>find(id,'system').name==='Transform');
    let forms=[],initialized=false;
    if(input.flyer!==undefined&&typeof input.flyer!=='boolean')throw Error('Flyer unit selection must be true or false.');
    if(faction==='unmc')unit.flyer=input.flyer===true||!!transform&&input.flyer===undefined;
    const defence=baseDefence(chassis,faction,transform);
    if(transform){
      const config=policy(faction,data);
      if(!config)throw Error('Only UNMC and Cybernetic Rebellion may use Transform.');
      if(config.flyer_only&&!unit.flyer)throw Error('UNMC Transform is available to flyer units only.');
      let definitions=input.forms;
      if(definitions===undefined){
        initialized=true;
        definitions=config.form_names.map((name,formIndex)=>({name,weapon_groups:weapons.map((_,i)=>i).filter(i=>weaponAllowedInForm(find(weapons[i].component,'weapon'),faction,formIndex)),systems:[...systems]}));
      }
      // Earlier UNMC customs had two generic modes. Preserve those loadouts as
      // Mech/Flyer and insert a Hybrid initialized from Mech.
      if(faction==='unmc'&&input.transform_version!==2&&Array.isArray(definitions)&&definitions.length===2){initialized=true;definitions=[definitions[0],{...definitions[0],weapon_groups:[...definitions[0].weapon_groups]},definitions[1]];}
      if(!Array.isArray(definitions)||definitions.length!==config.form_names.length)throw Error(`Transform requires exactly ${config.form_names.length} forms for this faction.`);
      const names=new Set();
      unit.forms=definitions.map((form,i)=>{
        if(!form||typeof form.name!=='string'||!form.name.trim()||form.name.length>60)throw Error('Give each form a name (up to 60 characters).');
        const name=config.fixed_names?config.form_names[i]:form.name.trim();
        if(names.has(name.toLocaleLowerCase()))throw Error('Give the forms different names.');names.add(name.toLocaleLowerCase());
        if(!Array.isArray(form.weapon_groups)||new Set(form.weapon_groups).size!==form.weapon_groups.length||form.weapon_groups.some(n=>!Number.isSafeInteger(n)||n<0||n>=weapons.length))throw Error('A form refers to an invalid weapon group.');
        if(form.weapon_groups.some(n=>!weaponAllowedInForm(find(weapons[n].component,'weapon'),faction,i)))throw Error('UNMC Flyer form cannot use melee weapons. Assign them to Mech or Hybrid instead.');
        if(form.systems!==undefined&&(!Array.isArray(form.systems)||new Set(form.systems).size!==form.systems.length||form.systems.some(id=>!systems.includes(id))))throw Error('A form refers to an uninstalled system.');
        const result={name,movement:input.movement+config.movement_offsets[i],structure:input.structure,weapon_groups:[...form.weapon_groups],systems:[...systems]};
        if(faction==='cybernetic-rebellion'&&i===1){
          const type=form.movement_type===undefined?'standard':form.movement_type;
          if(type!=='standard'&&!data.custom.movement_types.some(t=>t.id===type))throw Error('Choose a supported alternate-form movement type.');
          result.movement_type=type;
        }else if(form.movement_type!==undefined&&form.movement_type!=='standard')throw Error('Movement type selection applies only to the Cybernetic alternate form.');
        return result;
      });
      unit.transform_version=2;
      if(weapons.some((_,i)=>!unit.forms.some(f=>f.weapon_groups.includes(i))))throw Error('Assign each installed weapon group to at least one form.');
      forms=unit.forms.map((f,i)=>{
        const type=data.custom.movement_types.find(t=>t.id===f.movement_type);
        return {...f,defence:`${Number.parseInt(defence,10)+config.defence_offsets[i]}+`,movement_type:f.movement_type||config.form_names[i],
          movement_label:type?.name||(f.movement_type==='standard'?'Unchanged Mech movement':config.form_names[i]),movement_rules:type?.rules||[],
          flyer:!!config.flyer_only&&i===2||f.movement_type==='flyer'};
      });
      breakdown[0].forms=forms.map(f=>f.name);
      weapons.forEach((_,i)=>breakdown[i+1].forms=forms.filter(f=>f.weapon_groups.includes(i)).map(f=>f.name));
      systems.forEach((id,i)=>breakdown[weapons.length+i+1].forms=forms.filter(f=>f.systems.includes(id)).map(f=>f.name));
    }else if(input.forms!==undefined&&(!Array.isArray(input.forms)||input.forms.length))throw Error('Select the Transform system before defining alternate forms.');
    return {unit,total:breakdown.reduce((sum,r)=>sum+r.total,0),breakdown,defence,forms,
      warnings:initialized?['Forms were updated to the current faction rules. Review their weapon assignments.']:[]};
  }
  return {allowed,parts,calculate,linked,policy,baseDefence,melee,weaponAllowedInForm};
});
