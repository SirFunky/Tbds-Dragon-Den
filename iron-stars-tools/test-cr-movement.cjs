const assert=require('node:assert/strict'),fs=require('node:fs');
const custom=require('../iron-stars/assets/custom-core.js'),roster=require('../iron-stars/assets/roster-core.js');
const data=JSON.parse(fs.readFileSync('iron-stars/data/army-builder.json','utf8'));
const part=(name,kind)=>data.custom.parts.find(p=>p.name===name&&p.kind===kind&&p.source_id==='core');
const frame=part('Medium','chassis'),blade=part('Light Blade','weapon'),transform=part('Transform','system');
const unit={name:'Animal or vehicle',chassis:frame.id,movement:15,structure:4,weapons:[{component:blade.id,quantity:1,linked:false}],systems:[transform.id],forms:[{name:'Mech',weapon_groups:[0]},{name:'Wolf',weapon_groups:[0]}]};
const clone=x=>JSON.parse(JSON.stringify(x));
assert.deepEqual(data.custom.movement_types.map(t=>t.id),['walker','wheeled','tracked','hover','flyer','burrower']);
const legacy=custom.calculate(unit,'cybernetic-rebellion',data);assert.equal(legacy.unit.forms[1].movement_type,'standard');assert.equal(legacy.forms[1].movement_rules.length,0);
for(const type of data.custom.movement_types){
 const def=clone(unit);def.forms[1].movement_type=type.id;
 const result=custom.calculate(def,'cybernetic-rebellion',data);
 assert.equal(result.total,20);assert.deepEqual(result.forms.map(f=>[f.movement,f.defence,f.structure]),[[15,'4+',4],[15,'4+',4]]);
 assert.equal(result.forms[1].movement_type,type.id);assert.equal(result.forms[1].flyer,type.id==='flyer');assert.deepEqual(result.forms[1].movement_rules,type.rules);
 let force=roster.saveCustom(roster.blank('cybernetic-rebellion'),'custom-movement',def,data);force.lines[0].quantity=2;
 force=roster.decode(roster.encode(force,data),data);assert.equal(force.lines[0].custom.forms[1].movement_type,type.id);assert.equal(roster.summarize(force,data).total,40);
 const card=roster.cardProfiles(force,data)[1];assert.equal(card.profile.movement_type,type.id);assert.equal(card.weapons[0].part.id,blade.id,'CR Flyer may keep melee');
}
const wheel=data.custom.movement_types.find(t=>t.id==='wheeled');assert(wheel.rules[0].text.includes('entire move stays on Open Ground'));
const tracked=data.custom.movement_types.find(t=>t.id==='tracked');assert.equal(tracked.rules.length,2);assert(tracked.rules[1].text.includes('Heavy'));
const forged=clone(unit);forged.forms[1].movement_type='teleport';assert.throws(()=>custom.calculate(forged,'cybernetic-rebellion',data),/supported/);
forged.forms[1].movement_type='walker';forged.forms[0].movement_type='flyer';assert.throws(()=>custom.calculate(forged,'cybernetic-rebellion',data),/only to the Cybernetic alternate/);
const original=JSON.stringify(unit);custom.calculate(unit,'cybernetic-rebellion',data);assert.equal(JSON.stringify(unit),original);
console.log('PASS: six CR movement types, unchanged base stats/costs, conditional Wheeled rule, Tracked Stable Platform, persistence/cards, legacy unchanged movement, rejected unknown/base-form types and CR Flyer melee access.');
