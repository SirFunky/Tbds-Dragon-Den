const assert=require('node:assert/strict'),fs=require('node:fs');
const custom=require('../iron-stars/assets/custom-core.js'),roster=require('../iron-stars/assets/roster-core.js');
const data=JSON.parse(fs.readFileSync('iron-stars/data/army-builder.json','utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));
const part=(name,kind)=>data.custom.parts.find(p=>p.name===name&&p.kind===kind&&p.source_id==='core');
const frame=part('Medium','chassis'),laser=part('Medium Laser','weapon'),blade=part('Light Blade','weapon'),transform=part('Transform','system'),jetpack=part('Jetpack','system');
const unit={name:'Three-form flyer',chassis:frame.id,movement:15,structure:4,flyer:true,transform_version:2,
 weapons:[{component:laser.id,quantity:4,linked:true},{component:blade.id,quantity:1,linked:false}],systems:[transform.id,jetpack.id],
 forms:['Mech','Hybrid','Flyer'].map((name,i)=>({name,weapon_groups:i===0?[0,1]:[0],systems:[transform.id]}))};
const calc=custom.calculate(unit,'unmc',data);
assert.equal(calc.total,54);
assert.deepEqual(calc.forms.map(f=>[f.name,f.movement,f.defence,f.structure,f.flyer]),[['Mech',15,'4+',4,false],['Hybrid',25,'3+',4,false],['Flyer',25,'2+',4,true]]);
assert.deepEqual(calc.breakdown[1].copy_prices,[6,6,6,12]);assert.deepEqual(calc.breakdown[2].forms,['Mech']);
assert(calc.unit.forms.every(f=>JSON.stringify(f.systems)===JSON.stringify(unit.systems)));
const interceptor=data.custom.parts.find(p=>p.name==='UN Interceptor Frame'&&p.kind==='chassis');
const reference=custom.calculate({...unit,chassis:interceptor.id,movement:18,structure:5},'unmc',data);
assert.deepEqual(reference.forms.map(f=>[f.movement,f.defence,f.structure]),[[18,'5+',5],[28,'4+',5],[28,'3+',5]]);
for(const faction of data.factions.filter(f=>!['unmc','cybernetic-rebellion'].includes(f.id))){assert(!custom.parts(data,faction.id,'system').some(p=>p.name==='Transform'));assert.throws(()=>custom.calculate(unit,faction.id,data));}
function invalid(change,pattern){const x=clone(unit);change(x);assert.throws(()=>custom.calculate(x,'unmc',data),pattern);}
invalid(x=>x.flyer=false,/flyer units only/);invalid(x=>x.forms.pop(),/exactly 3/);
invalid(x=>x.forms[1].weapon_groups=[-1],/invalid weapon/);invalid(x=>x.forms[1].weapon_groups=[2],/invalid weapon/);invalid(x=>x.forms[1].weapon_groups=[0,0],/invalid weapon/);
invalid(x=>x.forms[0].weapon_groups=[0],/at least one form/);invalid(x=>x.forms[1].systems=[blade.id],/uninstalled system/);invalid(x=>x.systems=[jetpack.id],/Select the Transform/);
const forged=clone(unit);Object.assign(forged.forms[1],{movement:999,structure:999,defence:'1+',cost:0,name:'Forged'});assert.deepEqual(custom.calculate(forged,'unmc',data).unit,calc.unit);
const separate=clone(unit);separate.weapons.push({...unit.weapons[0]});separate.forms[2].weapon_groups=[2];assert.equal(custom.calculate(separate,'unmc',data).total,84);
const legacy=clone(unit);delete legacy.transform_version;delete legacy.flyer;legacy.forms.splice(1,1);
const migrated=custom.calculate(legacy,'unmc',data);assert.equal(migrated.unit.flyer,true);assert.equal(migrated.total,54);assert.deepEqual(migrated.unit.forms.map(f=>f.weapon_groups),[[0,1],[0,1],[0]]);assert.deepEqual(custom.calculate(migrated.unit,'unmc',data).unit,migrated.unit);
delete legacy.forms;assert.equal(custom.calculate(legacy,'unmc',data).forms.length,3);
const cyber=clone(unit);delete cyber.flyer;cyber.forms=[{name:'Mech',weapon_groups:[0,1]},{name:'Alternate',movement:100,structure:100,weapon_groups:[0]}];
assert.deepEqual(custom.calculate(cyber,'cybernetic-rebellion',data).forms.map(f=>[f.movement,f.defence,f.structure]),[[15,'4+',4],[15,'4+',4]]);
cyber.forms[1].name='Mech';assert.throws(()=>custom.calculate(cyber,'cybernetic-rebellion',data),/different names/);
let force=roster.saveCustom(roster.blank('unmc'),'custom-transform',unit,data);force.lines[0].quantity=2;assert.equal(roster.summarize(force,data).total,108);assert.deepEqual(roster.decode(roster.encode(force,data),data),force);
force=roster.saveCustom(force,'custom-transform',{...unit,name:'Edited flyer'},data);assert.equal(force.lines[0].quantity,2);
const altered=clone(data);altered.custom.parts.find(p=>p.id===laser.id).price=7;assert.equal(roster.summarize(roster.decode(roster.encode(force,data),altered),altered).total,118);
const banned=clone(force);banned.faction='iron-concord';assert.throws(()=>roster.validate(banned,data));const repaired=roster.repairLegacyTransforms(banned,data);
assert.equal(repaired.lines[0].quantity,2);assert.equal(repaired.lines[0].custom.weapons.length,2);assert(!repaired.lines[0].custom.forms);assert(!repaired.lines[0].custom.systems.includes(transform.id));assert.equal(roster.summarize(repaired,data).total,102);assert(banned.lines[0].custom.forms);
const fixture=clone(data),ammo=fixture.custom.parts.find(p=>p.requires_ammunition);fixture.custom.parts.find(p=>p.id===laser.id).details.push({label:'Test fixture',text:'Ammunition 2'});
const ammoUnit=clone(unit);ammoUnit.systems.push(ammo.id);ammoUnit.ammo_target=0;ammoUnit.forms[2].weapon_groups=[];assert.equal(custom.calculate(ammoUnit,'unmc',fixture).total,57);ammoUnit.ammo_target=1;assert.throws(()=>custom.calculate(ammoUnit,'unmc',fixture),/Ammunition/);
console.log('PASS: Transform faction/flyer restrictions, three UNMC reference profiles, two Cybernetic profiles, shared Structure/systems, assignments, full costs, legacy migration/recovery and current-price round trips.');

// Latest author clarification: only UNMC Flyer form forbids melee.
assert(custom.melee(blade));assert(!custom.melee(laser));
const badFlyer=clone(unit);badFlyer.forms[2].weapon_groups=[0,1];
assert.throws(()=>custom.calculate(badFlyer,'unmc',data),/UNMC Flyer form cannot use melee/);
const badImport=clone(force);badImport.lines[0].custom=badFlyer;
assert.throws(()=>roster.decode(JSON.stringify(badImport),data),/UNMC Flyer form cannot use melee/);
const fixedFlyer=roster.repairLegacyTransforms(badImport,data);
assert.deepEqual(fixedFlyer.lines[0].custom.forms[2].weapon_groups,[0]);
assert.equal(roster.summarize(fixedFlyer,data).total,108);
assert.deepEqual(badImport.lines[0].custom.forms[2].weapon_groups,[0,1]);
const flyerOnlyBlade=clone(badImport);flyerOnlyBlade.lines[0].custom.forms[0].weapon_groups=[0];
assert(roster.repairLegacyTransforms(flyerOnlyBlade,data).lines[0].custom.forms[0].weapon_groups.includes(1));
const autoForms=clone(unit);delete autoForms.forms;
assert.deepEqual(custom.calculate(autoForms,'unmc',data).unit.forms.map(f=>f.weapon_groups),[[0,1],[0,1],[0]]);
for(const faction of data.factions.filter(f=>f.id!=='unmc'))assert(custom.weaponAllowedInForm(blade,faction.id,2));
const cyberMelee=clone(unit);cyberMelee.forms=cyberMelee.forms.slice(0,2);cyberMelee.forms[1].weapon_groups=[1];
assert.equal(custom.calculate(cyberMelee,'cybernetic-rebellion',data).total,54);
console.log('PASS: UNMC-only Flyer melee ban, valid Mech/Hybrid and Cybernetic melee, rejected imports, safe default assignments and explicit saved-draft repair.');
