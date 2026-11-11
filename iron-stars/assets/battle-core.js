(function(root,factory){const api=factory(typeof module==='object'&&module.exports?require('./roster-core.js'):root.IronRoster);if(typeof module==='object'&&module.exports)module.exports=api;else root.IronBattle=api;})(typeof globalThis!=='undefined'?globalThis:this,function(rosterCore){
  'use strict';
  const clone=value=>JSON.parse(JSON.stringify(value));
  const integer=(n,min,max)=>Number.isSafeInteger(n)&&n>=min&&n<=max;
  function limit(text){
    const ammo=/\bAmmunition\s*[:(]?\s*(\d+)\b/i.exec(text);
    if(ammo)return {limit:Number(ammo[1]),period:'game',ammunition:true};
    if(/\bone[- ]use\b|\bsingle[- ]use\b|\bonce per game\b|\bfirst hit[^.\n]*each game\b/i.test(text))return {limit:1,period:'game'};
    if(/\bonce per round\b/i.test(text))return {limit:1,period:'round'};
    if(/\bonce per activation\b/i.test(text))return {limit:1,period:'activation'};
    return null;
  }
  function maximum(unit){return unit.profiles[unit.form].structure??unit.manual_max;}
  function start(value,data){
    const roster=rosterCore.validate(value,data),summary=rosterCore.summarize(roster,data);
    if(!summary.count)throw Error('Add units to the roster before starting a battle.');
    if(summary.count>5000)throw Error('This roster exceeds the browser tracker’s 5,000-copy capacity.');
    const units=[];
    for(const line of roster.lines){
      const resolved=rosterCore.resolve(line,roster.faction,data,roster.subfaction),calc=resolved.calculation;
      let profiles,equipment=[];
      if(calc){
        profiles=calc.forms.length?calc.forms.map(f=>({name:f.name,movement:`${f.movement} cm`,defence:f.defence,structure:f.structure,movement_label:f.movement_label,movement_rules:f.movement_rules,weapon_groups:f.weapon_groups})): [{name:'Standard',movement:`${calc.unit.movement} cm`,defence:calc.defence,structure:calc.unit.structure,weapon_groups:calc.unit.weapons.map((_,i)=>i)}];
        for(const profile of profiles)profile.loadout=profile.weapon_groups.map(i=>{const w=calc.unit.weapons[i],p=data.custom.parts.find(p=>p.id===w.component);return `${w.quantity}× ${p.name}${w.linked?' (linked)':''}`;});
        calc.unit.weapons.forEach((w,i)=>{const p=data.custom.parts.find(p=>p.id===w.component);equipment.push({name:p.name,quantity:w.quantity,text:p.details.map(d=>d.text).join('\n'),source_refs:p.details.map(d=>d.source_ref),group:i,weapon:true});});
        calc.unit.systems.forEach(id=>{const p=data.custom.parts.find(p=>p.id===id);equipment.push({name:p.name,quantity:1,text:[...p.details,...p.help_rules].map(d=>d.text).join('\n'),source_refs:[...p.details,...p.help_rules].map(d=>d.source_ref),weapon:false});});
      }else{
        profiles=resolved.reference.profiles.map(p=>{const text=p.fields.structure?.text?.trim(),n=/^\d+$/.test(text||'')?Number(text):null;return {name:p.name,movement:p.fields.movement?.text||'Not specified',defence:p.fields.defence?.text||'Not specified',structure:n};});
        if(!profiles.length){
          const transform=resolved.reference.systems.some(s=>s.name==='Transform'&&!s.source_faction_bonus),policy=data.custom.transform_policy.factions[resolved.faction];
          profiles=(transform&&policy?policy.form_names:['Standard']).map(name=>({name,movement:'Not specified',defence:'Not specified',structure:null}));
        }
        equipment=(resolved.reference.battle_weapons||[]).map((p,i)=>({...p,group:i,weapon:true}));
        for(const p of resolved.reference.systems)if(!p.source_faction_bonus)equipment.push({name:p.name,quantity:1,text:p.rules.map(r=>r.text).join('\n'),source_refs:p.rules.map(r=>r.source_ref),weapon:false});
      }
      const uses=[];
      equipment.forEach((p,group)=>{if(p.name.startsWith('Ammo Bin'))return;const usage=limit(p.text);if(!usage)return;for(let copy=0;copy<(p.weapon?p.quantity:1);copy++)uses.push({id:`use-${group}-${copy}`,name:p.name+(p.weapon&&p.quantity>1?` · copy ${copy+1}`:''),limit:usage.limit,base_limit:usage.limit,remaining:usage.limit,period:usage.period,ammunition:!!usage.ammunition,group:p.weapon?p.group:null,copy:copy,text:p.text,source_refs:p.source_refs});});
      let ammo_bin=null;
      if(calc?.unit.ammo_target!==undefined){const group=calc.unit.ammo_target,candidates=uses.filter(u=>u.ammunition&&u.group===group);if(candidates.length)ammo_bin={group,copy:candidates.length===1?candidates[0].copy:null};if(ammo_bin?.copy!==null){const chosen=uses.find(u=>u.ammunition&&u.group===group&&u.copy===ammo_bin.copy);if(chosen){chosen.limit++;chosen.remaining++;}}}
      const rules=calc?rosterCore.quickReference({...roster,lines:[line]},data):resolved.reference.quick_rules.filter(r=>!r.source_faction_bonus);
      for(let copy=1;copy<=line.quantity;copy++)units.push({id:line.id+'--'+copy,name:resolved.name,ordinal:units.length+1,copy,total_copies:line.quantity,profiles:clone(profiles),form:0,structure:profiles[0].structure,manual_max:null,activated:false,suppressed:false,removed:false,notes:'',uses:clone(uses),ammo_bin:clone(ammo_bin),rules:clone(rules)});
    }
    return validate({schema:1,name:roster.name,faction:roster.faction,round:1,points:summary.total,traits:rosterCore.benefits(roster,data),units});
  }
  function validate(value){
    if(!value||value.schema!==1||typeof value.name!=='string'||value.name.length>100||typeof value.faction!=='string'||!integer(value.round,1,1000000)||!integer(value.points,0,Number.MAX_SAFE_INTEGER)||!Array.isArray(value.traits)||!Array.isArray(value.units)||!value.units.length||value.units.length>5000)throw Error('Invalid battle snapshot.');
    const ids=new Set();
    for(const u of value.units){
      if(!u||typeof u.id!=='string'||ids.has(u.id)||typeof u.name!=='string'||!integer(u.ordinal,1,5000)||!integer(u.total_copies,1,999)||!integer(u.copy,1,u.total_copies)||!Array.isArray(u.profiles)||!u.profiles.length||!integer(u.form,0,u.profiles.length-1))throw Error('Invalid battle unit.');ids.add(u.id);
      if(u.profiles.some(p=>typeof p.name!=='string'||p.structure!==null&&!integer(p.structure,1,1000000)))throw Error('Invalid sourced profile.');
      if(u.manual_max!==null&&!integer(u.manual_max,1,1000000))throw Error('Invalid manual starting Structure.');
      const max=maximum(u);if(max===null?u.structure!==null&&!integer(u.structure,0,1000000):!integer(u.structure,0,max))throw Error('Structure must stay between zero and starting Structure.');
      if(['activated','suppressed','removed'].some(k=>typeof u[k]!=='boolean')||typeof u.notes!=='string'||u.notes.length>2000||!Array.isArray(u.uses)||!Array.isArray(u.rules))throw Error('Invalid battle counters.');
      const counters=new Set();for(const c of u.uses){if(typeof c.id!=='string'||counters.has(c.id)||typeof c.name!=='string'||!integer(c.limit,0,1000000)||!integer(c.base_limit,0,1000000)||!integer(c.remaining,0,c.limit)||!['game','round','activation'].includes(c.period)||typeof c.text!=='string'||!Array.isArray(c.source_refs))throw Error('Invalid limited-use counter.');counters.add(c.id);}
      if(u.ammo_bin!==null&&(!u.ammo_bin||!integer(u.ammo_bin.group,0,99)||u.ammo_bin.copy!==null&&!integer(u.ammo_bin.copy,0,98)))throw Error('Invalid Ammo Bin selection.');
    }
    return clone(value);
  }
  function change(value,id,fn){const battle=validate(value),unit=battle.units.find(u=>u.id===id);if(!unit)throw Error('Battle unit not found.');fn(unit);return validate(battle);}
  function structure(value,id,n){return change(value,id,u=>{if(maximum(u)===null)throw Error('Set an agreed starting Structure first.');u.structure=n;});}
  function manualMaximum(value,id,n){return change(value,id,u=>{if(u.profiles[u.form].structure!==null)throw Error('Starting Structure is already specified by the source.');if(!integer(n,1,1000000))throw Error('Enter a positive starting Structure.');u.manual_max=n;u.structure=u.structure===null?n:Math.min(u.structure,n);});}
  function form(value,id,index){return change(value,id,u=>{if(!integer(index,0,u.profiles.length-1))throw Error('Unknown form.');u.form=index;const max=maximum(u);u.structure=max===null?u.structure:u.structure===null?max:Math.min(u.structure,max);});}
  function flag(value,id,key,state){return change(value,id,u=>{if(!['activated','suppressed','removed'].includes(key)||typeof state!=='boolean')throw Error('Invalid status.');u[key]=state;});}
  function notes(value,id,text){return change(value,id,u=>{u.notes=text;});}
  function remaining(value,id,counter,n){return change(value,id,u=>{const c=u.uses.find(c=>c.id===counter);if(!c)throw Error('Counter not found.');c.remaining=n;});}
  function activation(value,id){return change(value,id,u=>{u.uses.filter(c=>c.period==='activation').forEach(c=>c.remaining=c.limit);});}
  function ammoBin(value,id,copy){return change(value,id,u=>{if(!u.ammo_bin)throw Error('No numeric Ammunition target for Ammo Bin.');const candidates=u.uses.filter(c=>c.ammunition&&c.group===u.ammo_bin.group);if(candidates.some(c=>c.remaining!==c.limit))throw Error('Choose the Ammo Bin copy before spending this group’s ammunition.');if(!candidates.some(c=>c.copy===copy))throw Error('Choose an installed weapon copy.');u.ammo_bin.copy=copy;for(const c of candidates){c.limit=c.base_limit+(c.copy===copy?1:0);c.remaining=c.limit;}});}
  function nextRound(value){const battle=validate(value);battle.round++;for(const u of battle.units){u.activated=false;u.uses.filter(c=>c.period==='round').forEach(c=>c.remaining=c.limit);}return validate(battle);}
  return {start,validate,maximum,structure,manualMaximum,form,flag,notes,remaining,activation,ammoBin,nextRound,limit};
});
