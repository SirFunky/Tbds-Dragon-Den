const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const engine = require('../iron-stars/assets/unit-filters.js');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../iron-stars/data/units.json'), 'utf8'));
const find = (name) => data.units.find((unit) => unit.name === name);
const mortar = find('Auxilia Mortar Team');
const purger = find('Burning Purger');
const draughan = find('Draughan Purifier (House Draughan Exclusive)');
const sentinel = find('Sentinel-Class Suppressor (Fire Support Frame)');
assert.equal(engine.matches(mortar, { faction: 'iron-concord', min: '14', max: '14' }), true);
assert.equal(engine.matches(mortar, { max: '13' }), false);
assert.equal(engine.matches(mortar, { faction: 'unmc' }), false);
assert.equal(engine.matches(draughan, { faction: 'iron-concord', subfaction: 'House Draughan', query: 'laser purifier' }), true);
assert.equal(engine.matches(draughan, { subfaction: 'House Romanow' }), false);
assert.equal(engine.matches(mortar, { subfaction: 'unspecified' }), true);
assert.equal(engine.matches(find('UNDF Interceptor (Exclusive)'), { query: 'missile carbine' }), true);
assert.equal(engine.matches(mortar, { query: 'nothing-in-the-source' }), false);
assert.equal(engine.matches(draughan, { role: 'Support' }), true);
assert.equal(engine.matches(purger, { status: 'review' }), false);
assert.equal(engine.matches(purger, { status: 'clear' }), true);
assert.equal(engine.matches(purger, { min: '19', max: '19' }), true, 'Use the recalculated component total');
assert.equal(engine.matches(find('Crawler-Class Enforcer'), { min: '0' }), false, 'Missing cost must not become a free unit');
const surveyor = find('UNDF Surveyor-5 “Crawler”');
assert.deepEqual(surveyor.points.observations.map((point) => point.value), [26], 'A weapon’s 4-point Cost line is not another unit total');
assert.equal(engine.matches(surveyor, { min: '26', max: '26' }), false, 'Unpriced systems prevent a complete recalculation');
assert.equal(engine.matches(sentinel, {}), true, 'Review entries remain discoverable');
assert.equal(engine.matches(sentinel, { min: '33', max: '33' }), true, 'The recalculation replaces inconsistent source totals');
for (const faction of ['fourth-imperium', 'living-dominion', 'southern-cross-compact']) {
  assert.equal(data.units.filter((unit) => engine.matches(unit, { faction })).length, 0, 'No invented rosters');
}
const original = data.units.map((unit) => unit.id);
const sorted = engine.sort(data.units, 'points-asc');
assert.deepEqual(data.units.map((unit) => unit.id), original, 'Sort must not mutate reusable data');
let unknown = false; let previous = -Infinity;
for (const unit of sorted) {
  if (unit.points.filter_value == null) unknown = true;
  else { assert.equal(unknown, false); assert.ok(unit.points.filter_value >= previous); previous = unit.points.filter_value; }
}
assert.equal(engine.normalize('DÉFENCE'), 'defence');
console.log('PASS: unit search, combined filters, inclusive point limits, missing/conflicting costs, development factions, and stable sorting.');
