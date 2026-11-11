from pathlib import Path
p=Path(__file__).resolve().parent.parent/'PUBLICERING.md'
t=p.read_text(encoding='utf-8')
t=t.replace('Alla 18 bifogade bilder finns med. Resultatet är Necron-seger enligt spelarens minne; inga slutpoäng, exakta turer eller enskilda attackresultat har hittats på.','Den återfunna Facebook-tråden fastställer uppdraget Awaken the Data Spirits, Matched Play, bildgrupper för slutet av runda 1–4 och resultatet 18–8 till Necrons. Alla 18 tidigare bilder samt två återfunna MVP-original finns med. T’au hade Recon/Infiltration; Necrons hade Security. Debriefen återger spelarens kommentar om för aggressivt spel efter runda två. Enskilda attacker och poäng per runda är inte påhittade.')
p.write_text(t,encoding='utf-8')
