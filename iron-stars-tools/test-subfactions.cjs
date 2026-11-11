const assert=require('node:assert/strict');
const fs=require('node:fs');
const roster=require('../iron-stars/assets/roster-core.js');
const custom=require('../iron-stars/assets/custom-core.js');
const data=JSON.parse(fs.readFileSync('iron-stars/data/army-builder.json','utf8'));
const faction=id=>data.factions.find(f=>f.id===id);
const sub=(f,name)=>faction(f).subfactions.find(s=>s.name===name).id;
assert.equal(data.factions.reduce((n,f)=>n+f.subfactions.length,0),24);
assert.equal(faction('southern-cross-compact').subfactions.length,0);
const romanow=sub('iron-concord','House Romanow'),draughan=sub('iron-concord','House Draughan');
let force=roster.add(roster.blank('iron-concord'),'iron-concord-ironsworn-trooper',data);
const legacy=JSON.parse(JSON.stringify(force));delete legacy.subfaction;
assert.equal(roster.decode(JSON.stringify(legacy),data).subfaction,null);
force=roster.validate({...force,subfaction:romanow},data);
assert.equal(roster.benefits(force,data)[0].source_ref,'core:b0335');
assert(roster.benefits(force,data)[0].text.includes('morale/command'));
assert.equal(roster.summarize(force,data).total,9);
assert.deepEqual(roster.decode(roster.encode(force,data),data),force);
assert.throws(()=>roster.validate({...force,subfaction:sub('unmc','Atlas Dynamics')},data));
assert.throws(()=>roster.validate({...force,subfaction:'made-up-house'},data));
const forged=JSON.stringify({...force,traits:[{name:'Invented',text:'Free attacks'}],bonusPoints:-9});
assert.equal(roster.summarize(roster.decode(forged,data),data).total,9);
assert.equal(roster.benefits(roster.decode(forged,data),data)[0].name,'Iron Will');
for(const f of data.factions){
 for(const s of f.subfactions){
  const r={...roster.blank(f.id),subfaction:s.id};
  assert.deepEqual(roster.decode(roster.encode(r,data),data),r);
  for(const u of data.units.filter(u=>roster.cost(u,f.id,data))){
   const added=roster.add(r,u.id,data);
   assert.equal(roster.summarize(added,data).total,roster.cost(u,f.id,data).total,'Affiliations must not discount stock component costs');
  }
 }
}
const swarm=sub('cybernetic-rebellion','The Swarm Synod');
const warmachines=sub('cybernetic-rebellion','The Warmachines');
const reaper=roster.add({...roster.blank('cybernetic-rebellion'),subfaction:swarm},'cybernetic-rebellion-reaper-class-exactor-sniper-artillery-frame',data);
assert.equal(roster.benefits(reaper,data)[0].name,'Recursive Logic'); // No invented unit-family restriction.
assert.equal(roster.benefits({...reaper,subfaction:warmachines},data)[0].name,'Overdrive Surge');
assert.equal(roster.benefits({...reaper,subfaction:null},data).length,0);
for(const s of faction('living-dominion').subfactions){
 assert.equal(s.trait,null);
 const benefits=roster.benefits({...roster.blank('living-dominion'),subfaction:s.id},data);
 assert.deepEqual(benefits.map(b=>b.name),['Renewal of Flesh']);
 assert.equal(benefits[0].source_ref,'core:b0544');
}
const scc=roster.add(roster.blank('southern-cross-compact'),'iron-concord-ironsworn-trooper',data);
assert.deepEqual(roster.benefits(scc,data).map(b=>b.name),['Field Expedients']);
assert.equal(roster.summarize(scc,data).total,12);
assert.throws(()=>roster.validate({...scc,subfaction:romanow},data));
const paragon=data.units.find(u=>u.id==='cybernetic-rebellion-paragon-class-custodian-sentinels-leader-frame');
assert(paragon.reference.systems.find(s=>s.name==='Guardian Protocols').source_faction_bonus);
// A source-declared equipment lock must be enforced by construction and JSON import.
const fixture=JSON.parse(JSON.stringify(data));
const jetpack=fixture.custom.parts.find(p=>p.name==='Jetpack'&&p.source_id==='core');jetpack.allowed_subfactions=[romanow];
const chassis=fixture.custom.parts.find(p=>p.name==='Medium'&&p.kind==='chassis'&&p.source_id==='core');
const definition={name:'House test',chassis:chassis.id,movement:15,structure:4,weapons:[],systems:[jetpack.id]};
assert.equal(custom.calculate(definition,'iron-concord',fixture,{subfaction:romanow}).total,19);
assert.throws(()=>custom.calculate(definition,'iron-concord',fixture,{subfaction:draughan}));
assert(!custom.parts(fixture,'iron-concord','system',draughan).some(p=>p.id===jetpack.id));
const locked=roster.saveCustom({...roster.blank('iron-concord'),subfaction:romanow},'custom-house',definition,fixture);
assert.deepEqual(roster.decode(roster.encode(locked,fixture),fixture),locked);
assert.throws(()=>roster.decode(JSON.stringify({...locked,subfaction:draughan}),fixture));
assert.equal(locked.subfaction,romanow); // Rejected changes do not mutate the draft.
assert(!data.custom.parts.some(p=>['Black Budget (SynCo)','Deep Strike (Stratos)','Sponsor Protocol'].includes(p.name)));
console.log('PASS: 24 current-core affiliations, correct inherited traits, unchanged full costs, legacy migration, persistence, conditional Host rules, Southern Cross exclusion, and equipment-lock import checks.');
