const assert = require('node:assert/strict');
const fs = require('node:fs');
const core = require('../iron-stars/assets/roster-core.js');
const data = JSON.parse(fs.readFileSync('iron-stars/data/army-builder.json','utf8'));
const all = JSON.parse(fs.readFileSync('iron-stars/data/units.json','utf8')).units;
assert.equal(data.units.length,26);
for(const unit of data.units) {
 const source=all.find(u=>u.id===unit.id);
 assert.equal(unit.points,source.points.calculation.total);
 assert.equal(source.review_notes.length,0);
 assert.equal(source.points.calculation.status,'complete');
}
const first=data.units.find(u=>u.id==='iron-concord-ironsworn-trooper');
let roster=core.blank('iron-concord');
const original=JSON.stringify(roster);
roster=core.add(roster,first.id,data);
assert.equal(original,JSON.stringify(core.blank('iron-concord')));
roster=core.add(roster,first.id,data);
assert.equal(roster.lines.length,1);
assert.equal(roster.lines[0].quantity,2);
assert.equal(core.summarize(roster,data).total,18);
roster.limit=17;
assert.equal(core.summarize(roster,data).overLimit,true);
assert.equal(core.summarize(roster,data).remaining,-1);
assert.deepEqual(core.decode(core.encode(roster,data),data),roster);
assert.equal(core.decode(JSON.stringify({...roster,total:0,lines:[{id:first.id,quantity:2,points:0}]}),data).lines[0].points,undefined);
assert.equal(core.summarize(core.decode(JSON.stringify({...roster,total:0}),data),data).total,18);
for(const quantity of [0,-1,1.2,1000,NaN,'2',null])assert.throws(()=>core.validate({...roster,lines:[{id:first.id,quantity}]},data));
for(const limit of [0,-1,1.5,'500',null])assert.throws(()=>core.validate({...roster,limit},data));
assert.throws(()=>core.decode('{broken',data));
assert.throws(()=>core.validate({...roster,schema:2},data));
assert.throws(()=>core.add(roster,'unmc-command-frame-archon',data));
assert.throws(()=>core.add(roster,'cybernetic-rebellion-ascendant-controller',data));
assert.throws(()=>core.validate({...roster,lines:[roster.lines[0],roster.lines[0]]},data));
const saved=JSON.stringify(roster);
assert.throws(()=>core.add(roster,'unknown',data));
assert.equal(JSON.stringify(roster),saved);
const hostile=core.decode(JSON.stringify({...roster,name:'<img src=x onerror=alert(1)>'}),data);
assert.equal(hostile.name,'<img src=x onerror=alert(1)>'); // UI inserts names with textContent.
console.log('PASS: 26 eligible premades; full costs, quantity math, budget, current-price import/export, invalid data and faction rejection.');

const scc='southern-cross-compact';
const expectedImports={
 'iron-concord-ironsworn-trooper':[9,2,1,12],
 'iron-concord-bastion-class-walker':[43,5,1,49],
 'unmc-command-frame-archon':[63,4,3,70],
 'new-avalon-knight-errant-frame':[25,3,5,33],
 'iron-concord-legate-class-linewalker':[34,4,1,39],
 'unmc-undf-vulture-stryker':[32,3,3,38]
};
assert.equal(data.units.filter(u=>core.cost(u,scc,data)).length,6);
for(const [id,expected] of Object.entries(expectedImports)) {
 const unit=data.units.find(u=>u.id===id), price=core.cost(unit,scc,data);
 assert.deepEqual([price.base,price.chassisTax,price.sourceModifier,price.total],expected);
 assert.equal(core.cost(unit,unit.faction,data).total,expected[0]);
}
let imported=core.blank(scc);
imported=core.add(imported,'iron-concord-bastion-class-walker',data);
imported=core.add(imported,'iron-concord-bastion-class-walker',data);
imported=core.add(imported,'unmc-command-frame-archon',data);
assert.equal(core.summarize(imported,data).total,168); // Every copy pays both taxes.
assert.deepEqual(core.decode(core.encode(imported,data),data),imported);
const forged=JSON.stringify({...imported,total:0,lines:imported.lines.map(l=>({...l,points:0,chassisTax:0,sourceModifier:0}))});
assert.equal(core.summarize(core.decode(forged,data),data).total,168);
assert.throws(()=>core.add(imported,'cybernetic-rebellion-drone-swarm-cluster-horde-unit',data));
assert.throws(()=>core.add(imported,'iron-concord-burning-purger',data)); // Unconfirmed tier.
assert.equal(core.summarize(core.add(core.blank(scc),'iron-concord-ironsworn-trooper',data),data).total,12);
assert.equal(core.cost({...data.units[0],southern_cross:{eligible:true,tier:'unknown'}},scc,data),null);
assert.equal(core.cost({...data.units[0],faction:'cybernetic-rebellion',southern_cross:{eligible:true,tier:'light'}},scc,data),null);
assert.throws(()=>core.decode(JSON.stringify({...imported,faction:'unmc'}),data));
const updated=JSON.parse(JSON.stringify(data));
updated.import_rules.chassis_tax.superheavy=6;
assert.equal(core.summarize(core.decode(core.encode(imported,data),updated),updated).total,170);
console.log('PASS: Southern Cross eligible sources, explicit chassis tiers, per-copy taxes, mixed-source rosters, current-price round trips and forged-cost rejection.');
