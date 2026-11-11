"""Regression checks for current prices, component coverage, and linked/group math."""
import json
from pathlib import Path
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
engine=runpy.run_path(str(ROOT/'iron-stars-tools/pricing.py'))
DATA=json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))
BY_REF={u['source_refs'][0]:u for u in DATA['units']}

class PricingTests(unittest.TestCase):
    def test_scout_lasers_are_individually_priced(self):
        prices=engine['Prices']()
        for ref,name,variant,price,subtotal in [
            ('avalon:b0065','Medium Laser (Scout)','prototype',10,53),
            ('avalon:b0077','Medium Laser+ (Scout)','experimental',15,70)]:
            with self.subTest(ref=ref):
                self.assertEqual(prices.find('avalon','weapon',name,variant)['unit_price'],price)
                calc=BY_REF[ref]['points']['calculation']
                laser=next(row for row in calc['components'] if row['name']==name)
                self.assertEqual(laser['quantity'],3)
                self.assertEqual(laser['total'],3*price)
                self.assertEqual(calc['known_subtotal'],subtotal)
                self.assertIsNone(calc['total']) # Other system prices remain unspecified.

    def test_linked_escalation(self):
        linked=engine['linked_cost']
        self.assertEqual([linked(4,n) for n in range(1,7)],[4,8,12,20,32,48])
        self.assertEqual(linked(6,4),30)
        with self.assertRaises(ValueError):linked(4,0)

    def test_expected_recalculations(self):
        expected={'concord:b0035':9,'concord:b0039':19,'concord:b0043':14,'concord:b0070':33,
          'concord:b0075':37,'concord:b0080':43,'unmc:b0046':27,'unmc:b0171':63,
          'rebellion:b0144':44,'rebellion:b0182':47,'rebellion:b0227':43,'rebellion:b0264':50,
          'rebellion:b0303':21,'rebellion:b0336':33,'rebellion:b0371':34,'rebellion:b0406':56,
          'rebellion:b0444':22,'rebellion:b0472':20,'rebellion:b0500':50,'rebellion:b0532':51,
          'rebellion:b0571':22,'rebellion:b0601':31,'rebellion:b0631':33,'rebellion:b0665':55,
          'avalon:b0108':81,'core:b0205':25,'core:b0212':34,'core:b0220':32}
        for ref,total in expected.items():
            with self.subTest(ref=ref):self.assertEqual(BY_REF[ref]['points']['calculation']['total'],total)

    def test_core_prices_override_shared_faction_prices(self):
        prices=engine['Prices']()
        core=prices.find('rebellion','system','Hardened Carapace')
        self.assertEqual(core['unit_price'],2)
        self.assertEqual(core['source_id'],'core')
        self.assertEqual(prices.find('avalon','weapon','Beam Rapier','prototype')['unit_price'],8)
        self.assertEqual(prices.find('core','weapon','Beam Rapier')['unit_price'],4)
        self.assertIsNone(prices.find('avalon','weapon','Judicator Blade+','experimental'))

    def test_unknown_not_free_or_backsolved(self):
        for ref in ['avalon:b0252','concord:b0211','core:b0399']:
            calc=BY_REF[ref]['points']['calculation']
            self.assertIsNone(calc['total'])
            self.assertTrue(calc['missing_components'])
            self.assertIsNone(BY_REF[ref]['points']['filter_value'])
        self.assertEqual(BY_REF['avalon:b0252']['points']['calculation']['known_subtotal'],103)

    def test_modes_not_double_charged(self):
        for ref,weapon in [('rebellion:b0264','Heavy Cannon'),('rebellion:b0336','Medium Laser')]:
            rows=BY_REF[ref]['points']['calculation']['components']
            self.assertEqual(sum(row['quantity'] for row in rows if row['name']==weapon),1)

    def test_grants_optional_and_keyword_no_double_charge(self):
        mortar=BY_REF['concord:b0043']['points']['calculation']
        option=next(r for r in mortar['components'] if r['name']=='March of Steel')
        self.assertFalse(option['included']);self.assertEqual(option['total'],2)
        self.assertEqual(mortar['total'],14)
        warden=BY_REF['rebellion:b0571']['points']['calculation']
        echo=next(r for r in warden['components'] if r['name']=='Quantum Echo')
        self.assertEqual(echo['total'],0);self.assertEqual(echo['basis'],'explicit-grant')
        self.assertTrue(echo['price_source_ref'])
        hive=BY_REF['rebellion:b0500']['points']['calculation']
        laser=next(r for r in hive['components'] if r['name']=='Medium Laser')
        self.assertEqual(laser['copy_prices'],[6,6,6,12]);self.assertEqual(laser['total'],30)
        self.assertFalse(any(r['name']=='Linked' for r in hive['components']))

    def test_separate_linked_groups(self):
        prices=engine['Prices']()
        component={'name':'Medium Laser','kind':'weapon','quantity':4,'groups':2,'linked':True,'source_ref':'test'}
        calc=engine['calculate']([component],'core',prices)
        self.assertEqual(calc['total'],60) # 30 per arm, not one eight-gun group.

    def test_unclear_linking_stays_explicit(self):
        calc=BY_REF['unmc:b0061']['points']['calculation']
        row=next(r for r in calc['components'] if r['name']=='Micro-Missile Swarm')
        self.assertEqual(row['alternatives'],{'separate':24,'linked':30})
        self.assertIsNone(calc['total'])

    def test_all_arithmetic_and_sources(self):
        docs={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')}
        texts={}
        for doc in docs.values():
            for block in doc['blocks']:
                texts[block['id']]=block.get('text','')
                for row in block.get('rows',[]):
                    texts[row['id']]=' | '.join(c['text'] for c in row['cells'])
                    texts.update((c['id'],c['text']) for c in row['cells'])
        prices=engine['Prices']()
        for definition in prices.entries.values():
            source=texts[definition['source_ref']]
            self.assertIn(str(definition['unit_price']),source)
            self.assertEqual(definition['source_sha256'],docs[definition['source_id']]['sha256'])
            self.assertNotEqual(definition['name'],'Sponsor Protocol')
        for unit in DATA['units']:
            calc=unit['points']['calculation']
            self.assertEqual(calc['known_subtotal'],sum(row['total'] for row in calc['components'] if row['total'] is not None and row['included']))
            self.assertEqual(unit['points']['filter_value'],calc['total'])
            self.assertEqual(calc['total'] is None, bool(calc['missing_components']))
            self.assertTrue(all(row['source_ref'] in texts for row in calc['components']))
            for row in calc['components']:
                if row.get('price_source_ref'):self.assertIn(row['price_source_ref'],texts)
                if row['basis']=='explicit-grant':
                    self.assertTrue('free' in texts[row['price_source_ref']].lower() or 'Flyer Scout' in texts[row['price_source_ref']])

if __name__=='__main__':unittest.main(verbosity=2)
