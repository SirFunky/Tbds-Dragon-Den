(function(root, factory) {
  const api = factory(typeof module === 'object' && module.exports ? require('./custom-core.js') : root.IronCustom);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.IronRoster = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function(custom) {
  'use strict';
  function blank(faction) { return {schema:1, faction, subfaction:null, name:'My force', limit:500, lines:[]}; }
  function affiliation(faction,id,data){
    const f=data.factions.find(f=>f.id===faction);
    if(!f)throw Error('Unknown faction.');
    if(id===undefined||id===null||id==='')return null;
    const selected=f.subfactions?.find(s=>s.id===id);
    if(!selected)throw Error('This subfaction does not belong to the selected faction.');
    return selected;
  }
  function benefits(roster,data){
    const selected=affiliation(roster.faction,roster.subfaction,data),f=data.factions.find(f=>f.id===roster.faction);
    return [...(f.shared_traits||[]),...(selected?.trait?[selected.trait]:[])];
  }
  function cost(unit, faction, data) {
    if (unit.faction === faction) return {base:unit.points,chassisTax:0,sourceModifier:0,total:unit.points,imported:false};
    const rules=data.import_rules, policy=unit.southern_cross;
    if (!rules || faction!==rules.faction || !policy || !policy.eligible) return null;
    const chassisTax=rules.chassis_tax[policy.tier], sourceModifier=rules.source_modifier[unit.faction];
    if (!Number.isSafeInteger(chassisTax) || !Number.isSafeInteger(sourceModifier)) return null;
    return {base:unit.points,chassisTax,sourceModifier,total:unit.points+chassisTax+sourceModifier,imported:true};
  }
  function resolve(line,faction,data,subfaction=null){
    if(line.custom){
      if(typeof line.id!=='string'||!/^custom-[a-zA-Z0-9-]{1,80}$/.test(line.id))throw Error('Invalid custom unit identity.');
      const calculation=custom.calculate(line.custom,faction,data,{subfaction});
      return {id:line.id,name:calculation.unit.name,faction,points:calculation.total,custom:calculation.unit,calculation};
    }
    return data.units.find(u=>u.id===line.id);
  }
  function normalizeTags(value){
    if(value===undefined)return [];
    if(!Array.isArray(value)||value.length>1000)throw Error('Roster tags must be a list.');
    const tags=[],seen=new Set();
    for(const item of value){
      if(typeof item!=='string')throw Error('Tags must be text.');
      const tag=item.normalize('NFC').trim().replace(/\s+/g,' ');
      if(!tag)continue;
      if(tag.length>40)throw Error('Keep each tag to 40 characters or fewer.');
      const key=tag.toLowerCase();if(!seen.has(key)){seen.add(key);tags.push(tag);}
    }
    if(tags.length>20)throw Error('Use at most 20 tags per roster.');
    return tags;
  }
  function validate(value, data) {
    if (!value || value.schema !== 1 || !data.factions.some(f => f.id === value.faction)) throw Error('Unknown roster format or faction.');
    const selected=affiliation(value.faction,value.subfaction,data);
    if (typeof value.name !== 'string' || value.name.length > 100) throw Error('Roster name must be 100 characters or fewer.');
    if (!Number.isSafeInteger(value.limit) || value.limit < 1 || value.limit > 1000000) throw Error('Enter a whole points limit between 1 and 1,000,000.');
    if (!Array.isArray(value.lines) || value.lines.length > 1000) throw Error('Invalid unit list.');
    const seen = new Set();
    const lines = value.lines.map(line => {
      if(!line||typeof line!=='object')throw Error('Invalid unit row.');
      const unit = resolve(line,value.faction,data,selected?.id||null);
      if (!unit || !cost(unit,value.faction,data)) throw Error('A unit is unavailable, unresolved, or cannot be used by this faction.');
      if (seen.has(line.id)) throw Error('Duplicate unit rows. Use the quantity field.');
      seen.add(line.id);
      if (!Number.isSafeInteger(line.quantity) || line.quantity < 1 || line.quantity > 999) throw Error('Unit quantities must be whole numbers from 1 to 999.');
      return unit.custom?{id:line.id,quantity:line.quantity,custom:unit.custom}:{id:line.id, quantity:line.quantity};
    });
    return {schema:1, faction:value.faction, subfaction:selected?.id||null, name:value.name, limit:value.limit, lines,...(value.tags!==undefined?{tags:normalizeTags(value.tags)}:{})};
  }
  function summarize(roster, data) {
    const safe = validate(roster, data);
    const total = safe.lines.reduce((sum, line) => sum + cost(resolve(line,safe.faction,data,safe.subfaction),safe.faction,data).total * line.quantity, 0);
    return {total, count:safe.lines.reduce((n,l) => n+l.quantity,0), remaining:safe.limit-total, overLimit:total>safe.limit};
  }
  function add(roster, id, data) {
    const copy = validate(roster, data);
    const line = copy.lines.find(l => l.id === id);
    if (line) line.quantity++;
    else copy.lines.push({id,quantity:1});
    return validate(copy, data);
  }
  function encode(roster, data) { return JSON.stringify(validate(roster, data), null, 2); }
  function decode(text, data) { return validate(JSON.parse(text), data); }
  function saveCustom(roster,id,definition,data){
    const copy=validate(roster,data),line=copy.lines.find(l=>l.id===id);
    if(line){if(!line.custom)throw Error('Cannot replace a premade.');line.custom=definition;}
    else copy.lines.push({id,quantity:1,custom:definition});
    return validate(copy,data);
  }
  function duplicateCustom(roster,sourceId,newId,data){
    const copy=validate(roster,data),index=copy.lines.findIndex(line=>line.id===sourceId),source=copy.lines[index];
    if(!source?.custom)throw Error('Choose a custom unit to duplicate.');
    if(copy.lines.some(line=>line.id===newId))throw Error('The copy needs a new unit identity.');
    const definition=JSON.parse(JSON.stringify(source.custom)),names=new Set(copy.lines.filter(line=>line.custom).map(line=>line.custom.name.toLocaleLowerCase()));
    let number=1,name;
    do{const suffix=number===1?' (copy)':` (copy ${number})`;name=source.custom.name.slice(0,100-suffix.length).trimEnd()+suffix;number++;}while(names.has(name.toLocaleLowerCase()));
    definition.name=name;
    copy.lines.splice(index+1,0,{id:newId,quantity:1,custom:definition});
    return validate(copy,data);
  }
  function repairLegacyTransforms(value,data){
    const copy=JSON.parse(JSON.stringify(value));
    if(copy.faction==='unmc')for(const line of copy.lines||[]){
      const unit=line.custom;
      if(!unit||unit.forms?.length!==3||!Array.isArray(unit.forms[2].weapon_groups))continue;
      const removed=unit.forms[2].weapon_groups.filter(n=>{
        const part=data.custom.parts.find(p=>p.id===unit.weapons[n]?.component);
        return part&&custom.melee(part);
      });
      unit.forms[2].weapon_groups=unit.forms[2].weapon_groups.filter(n=>!removed.includes(n));
      for(const n of removed)if(!unit.forms.some(f=>f.weapon_groups.includes(n)))unit.forms[0].weapon_groups.push(n);
    }
    const transform=data.custom.parts.find(p=>p.kind==='system'&&p.name==='Transform');
    if(transform&&!data.custom.transform_policy.allowed_factions.includes(copy.faction)){
      for(const line of copy.lines||[])if(line.custom?.systems?.includes(transform.id)){
        line.custom.systems=line.custom.systems.filter(id=>id!==transform.id);
        delete line.custom.forms;delete line.custom.transform_version;
      }
    }
    return validate(copy,data);
  }
  function cardProfiles(value,data,id=null){
    const roster=validate(value,data),cards=[];
    for(const line of roster.lines){
      if(!line.custom||(id!==null&&line.id!==id))continue;
      const result=custom.calculate(line.custom,roster.faction,data,{subfaction:roster.subfaction});
      const part=id=>data.custom.parts.find(p=>p.id===id);
      const profiles=result.forms.length?result.forms:[{name:null,movement:result.unit.movement,defence:result.defence,structure:result.unit.structure,weapon_groups:result.unit.weapons.map((_,i)=>i),flyer:false}];
      for(const profile of profiles)cards.push({id:line.id,name:result.unit.name,quantity:line.quantity,points:result.total,
        faction:roster.faction,subfaction:roster.subfaction,chassis:part(result.unit.chassis),profile,
        weapons:profile.weapon_groups.map(i=>({group:i+1,part:part(result.unit.weapons[i].component),cost:result.breakdown[i+1],...result.unit.weapons[i]})),
        systems:result.unit.systems.map(part),ammo_target:result.unit.ammo_target,
        transform:result.forms.length>0});
    }
    return cards;
  }
  function validateLibrary(value){
    if(!value||value.schema!==1||!Array.isArray(value.designs)||value.designs.length>1000)throw Error('Unknown library format or too many designs.');
    const ids=new Set();
    for(const entry of value.designs){
      if(!entry||typeof entry.id!=='string'||!/^design-[a-zA-Z0-9-]{1,80}$/.test(entry.id)||ids.has(entry.id)||typeof entry.faction!=='string'||!entry.custom||typeof entry.custom.name!=='string'||entry.custom.name.length>100||(entry.subfaction!=null&&typeof entry.subfaction!=='string'))throw Error('Invalid saved design.');
      ids.add(entry.id);
    }
    // Keep unavailable designs intact; their component rules are checked when
    // displayed or added, rather than discarding older library entries.
    return JSON.parse(JSON.stringify({schema:1,designs:value.designs}));
  }
  function designSignature(entry){return JSON.stringify([entry.faction,entry.subfaction||null,entry.custom]);}
  function saveDesign(library,roster,sourceId,newId,data){
    const safe=validateLibrary(library),force=validate(roster,data),line=force.lines.find(l=>l.id===sourceId);
    if(!line?.custom)throw Error('Choose a custom unit to save.');
    const entry={id:newId,faction:force.faction,subfaction:force.subfaction,custom:line.custom};
    if(safe.designs.some(saved=>designSignature(saved)===designSignature(entry)))return safe;
    safe.designs.push(entry);return validateLibrary(safe);
  }
  function addDesign(roster,entry,newId,data){
    const force=validate(roster,data);
    if(entry.faction!==force.faction)throw Error('Switch to this design’s faction to add it.');
    if(force.lines.some(line=>line.id===newId))throw Error('The design needs a new unit identity.');
    return saveCustom(force,newId,JSON.parse(JSON.stringify(entry.custom)),data);
  }
  function mergeLibrary(library,incoming,newId){
    const safe=validateLibrary(library),imported=validateLibrary(incoming);
    for(const entry of imported.designs){
      if(safe.designs.some(saved=>designSignature(saved)===designSignature(entry)))continue;
      if(safe.designs.some(saved=>saved.id===entry.id))entry.id=newId();
      safe.designs.push(entry);
    }
    return validateLibrary(safe);
  }
  function rosterCollection(value){
    if(value?.schema===1&&value.drafts&&typeof value.drafts==='object'&&!Array.isArray(value.drafts)){
      const rosters=Object.entries(value.drafts).map(([faction,roster],i)=>({id:'roster-legacy-'+i,faction,roster}));
      value={schema:2,activeFaction:value.activeFaction,activeByFaction:Object.fromEntries(rosters.map(r=>[r.faction,r.id])),rosters};
    }
    if(!value||value.schema!==2||!Array.isArray(value.rosters)||value.rosters.length>1000||!value.activeByFaction||typeof value.activeByFaction!=='object'||Array.isArray(value.activeByFaction))throw Error('Unknown saved roster collection.');
    const ids=new Set();
    for(const entry of value.rosters){
      if(!entry||typeof entry.id!=='string'||!/^roster-[a-zA-Z0-9-]{1,80}$/.test(entry.id)||ids.has(entry.id)||typeof entry.faction!=='string'||!Object.hasOwn(entry,'roster'))throw Error('Invalid saved roster identity.');
      ids.add(entry.id);
    }
    // Game-invalid rosters remain intact for export/repair on selection.
    return JSON.parse(JSON.stringify({schema:2,activeFaction:value.activeFaction,activeByFaction:value.activeByFaction,rosters:value.rosters}));
  }
  function addRoster(collection,roster,id,data){
    const safe=rosterCollection(collection),force=validate(roster,data);
    if(safe.rosters.some(r=>r.id===id))throw Error('Choose a new roster identity.');
    const names=new Set(safe.rosters.filter(r=>r.faction===force.faction).map(r=>String(r.roster?.name||'').toLocaleLowerCase()));
    const base=force.name.trim()||'My force';let name=base,n=2;
    while(names.has(name.toLocaleLowerCase())){const suffix=` (${n++})`;name=base.slice(0,100-suffix.length).trimEnd()+suffix;}
    force.name=name;safe.rosters.push({id,faction:force.faction,roster:force});safe.activeFaction=force.faction;safe.activeByFaction[force.faction]=id;
    return rosterCollection(safe);
  }
  function removeRoster(collection,id){
    const safe=rosterCollection(collection),entry=safe.rosters.find(r=>r.id===id);
    if(!entry)throw Error('Roster not found.');
    safe.rosters=safe.rosters.filter(r=>r.id!==id);
    if(safe.activeByFaction[entry.faction]===id){const next=safe.rosters.find(r=>r.faction===entry.faction);if(next)safe.activeByFaction[entry.faction]=next.id;else delete safe.activeByFaction[entry.faction];}
    return safe;
  }
  function mergeRosters(collection,incoming,newId){
    const safe=rosterCollection(collection),imported=rosterCollection(incoming);
    for(const entry of imported.rosters){
      if(safe.rosters.some(r=>JSON.stringify([r.faction,r.roster])===JSON.stringify([entry.faction,entry.roster])))continue;
      if(safe.rosters.some(r=>r.id===entry.id))entry.id=newId();
      safe.rosters.push(entry);
    }
    return rosterCollection(safe);
  }
  function findRosters(collection,options,data){
    const clean=text=>String(text||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const words=clean(options.query).trim().split(/\s+/).filter(Boolean),tag=clean(options.tag).trim();
    return rosterCollection(collection).rosters.filter(entry=>{
      if(options.faction&&entry.faction!==options.faction)return false;
      let tags=[];try{tags=normalizeTags(entry.roster?.tags);}catch(e){/* Preserve unavailable records and still search their names. */}
      if(tag&&!tags.some(value=>clean(value)===tag))return false;
      const faction=data.factions.find(f=>f.id===entry.faction),affiliation=faction?.subfactions?.find(s=>s.id===entry.roster?.subfaction);
      const text=clean([entry.roster?.name,faction?.name||entry.faction,affiliation?.name,entry.roster?.limit,...tags].join(' '));
      return words.every(word=>text.includes(word));
    });
  }
  function quickReference(value,data){
    const roster=validate(value,data),rules=new Map();
    const add=(category,name,text,refs,unit)=>{
      if(!text?.trim())return;
      const key=JSON.stringify([category,name,text.replace(/\s+/g,' ').trim()]);
      if(!rules.has(key))rules.set(key,{category,name,text,source_refs:[],used_by:[]});
      const item=rules.get(key);for(const ref of refs||[])if(ref&&!item.source_refs.includes(ref))item.source_refs.push(ref);
      if(unit&&!item.used_by.includes(unit))item.used_by.push(unit);
    };
    if(!roster.lines.length)return [];
    for(const rule of benefits(roster,data))add('Faction & affiliation',rule.name,rule.text,rule.source_ref?[rule.source_ref]:rule.source_refs,'Entire force');
    for(const line of roster.lines){
      const unit=resolve(line,roster.faction,data,roster.subfaction);
      if(!unit.custom){for(const rule of unit.reference.quick_rules||[])if(!rule.source_faction_bonus)add(rule.category,rule.name,rule.text,rule.source_refs,unit.name);continue;}
      const result=unit.calculation;
      for(const row of result.breakdown.slice(1)){
        const part=data.custom.parts.find(p=>p.id===row.component_id),category=part.kind==='weapon'?'Weapons':'Systems & traits';
        if(part.name==='Transform'){for(const rule of data.custom.transform_rules)add(category,'Transform',rule.text,[rule.source_ref],unit.name);}
        else add(category,part.name+(part.variant?' — '+part.variant:''),part.details.map(d=>d.label+': '+d.text).join('\n'),part.details.map(d=>d.source_ref),unit.name);
        for(const rule of part.help_keywords||[])add('Weapon keywords',rule.label,rule.text,[rule.source_ref],unit.name);
        for(const rule of part.help_rules||[])add(category,part.name,rule.text,[rule.source_ref],unit.name);
        if(part.name==='Jetpack'&&data.custom.jetpack_rule)add('Movement','Jetpack',data.custom.jetpack_rule.text,[data.custom.jetpack_rule.source_ref],unit.name);
        if(row.linked&&data.custom.linked_rule)add('Weapon keywords','Linked',data.custom.linked_rule.text,[data.custom.linked_rule.source_ref],unit.name);
      }
      for(const form of result.forms){
        for(const rule of form.movement_rules||[])add('Movement',form.movement_label,rule.text,[rule.source_ref],unit.name+' · '+form.name);
        if(form.flyer)add('Movement','Flyer',data.custom.flyer_rule.text,[data.custom.flyer_rule.source_ref],unit.name+' · '+form.name);
        if(form.flyer&&roster.faction==='unmc')add('Movement','UNMC Flyer','UNMC Flyer form cannot use melee weapons.',['user:2026-11-07-unmc-flyer-melee'],unit.name+' · '+form.name);
      }
    }
    const order=['Faction & affiliation','Movement','Weapons','Weapon keywords','Systems & traits','Unit rules'];
    return [...rules.values()].sort((a,b)=>order.indexOf(a.category)-order.indexOf(b.category)||a.name.localeCompare(b.name));
  }
  return {blank, validate, summarize, add, encode, decode, cost, resolve, saveCustom, duplicateCustom, affiliation, benefits, repairLegacyTransforms, cardProfiles, validateLibrary, saveDesign, addDesign, mergeLibrary, rosterCollection, addRoster, removeRoster, mergeRosters, quickReference, normalizeTags, findRosters};
});
