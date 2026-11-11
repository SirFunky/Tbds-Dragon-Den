const fs = require('fs');
const pages = JSON.parse(fs.readFileSync('tmp/guilds-pages.json', 'utf8'));
const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const books = [
  {slug:'a-dragon-among-mortals', file:'book-one.html', title:'A Dragon Among Mortals', number:'One', expected:46,
   summary:'When an armored stranger falls from the sky into the world of Aleris, a band of adventurers discovers that he is far more than he appears. Shade is a dragon in human form, sent to understand mortal lives. Joining the adventurers’ guild brings dangerous jobs, unexpected friendships, and the challenge of finding a place among people who do not know his true nature.'},
  {slug:'the-dragons-hearth', file:'book-two.html', title:'The Dragon’s Hearth', number:'Two', expected:43,
   summary:'Shade has found a home with Arcebek, Rakihi, and Elcia, but life among mortals is growing more complicated. As Lana draws him into the work of running the guild, he must learn to lead as well as fight. Guild politics, the demands of the Fey, and his ties to the Blue Flight test the life and relationships he is building.'}
];
const source = fs.readFileSync('guilds-and-dragons.html', 'utf8');
const header = source.match(/    <header[\s\S]*?<\/header>/)[0].replace(/(href|src)="(?!#)([^"]+)"/g, '$1="../$2"');
for(const [i, book] of books.entries()) {
  const chapters=[];
  pages[book.slug].forEach((text,index)=>{
    for(const line of text.split('\n').slice(0,5)) {
      const match=line.trim().match(/^Chapter\s+(\d+):\s*(.+)$/);
      if(match)chapters.push({number:Number(match[1]),title:match[2].replace(/\s+/g,' ').trim(),page:index+1});
    }
  });
  if(chapters.length!==book.expected || chapters.some((c,i)=>c.number!==i+1))throw Error('Chapter sequence invalid: '+book.slug);
  const other=books[1-i];
  const art=i===0 ? '<figure class="guilds-featured-art"><img src="dragon-among-mortals.png" alt="Cover of A Dragon Among Mortals" width="1536" height="1024" /></figure>' : '<div class="guilds-cover guilds-book-emblem" aria-hidden="true"><span>GUILDS<br>&amp; DRAGONS</span><b>II</b><span>THE DRAGON’S HEARTH</span></div>';
  const html=`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="${escape(book.summary)}" />
  <title>${escape(book.title)} | Guilds And Dragons</title>
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../site-header.css" />
  <link rel="stylesheet" href="series.css" />
  <link rel="stylesheet" href="book.css" />
</head>
<body><div class="page-shell">
${header}
<main class="guilds-series guilds-book-page">
  <a class="guilds-back" href="../guilds-and-dragons.html">← Guilds And Dragons</a>
  <section class="guilds-hero guilds-book-intro" aria-labelledby="book-title">
    <div class="guilds-intro">
      <p class="guilds-kicker">Guilds And Dragons · Book ${book.number}</p>
      <h1 id="book-title">${escape(book.title)}</h1>
      <p class="guilds-book-summary">${escape(book.summary)}</p>
      <div class="guilds-reading-links">
        <a class="guilds-button" href="${book.slug}.pdf">Read the full PDF <span aria-hidden="true">↗</span></a>
        <a class="guilds-download" href="${book.slug}.pdf" download>Download PDF <span aria-hidden="true">↓</span></a>
      </div>
      <p class="guilds-caption">${chapters.length} chapters · ${pages[book.slug].length} PDF pages</p>
    </div>
    ${art}
  </section>
  <section id="chapters" class="guilds-library" aria-labelledby="chapters-title">
    <div class="guilds-section-heading"><div><p class="guilds-kicker">Table of contents</p><h2 id="chapters-title">Chapters</h2></div></div>
    <p class="guilds-library-intro">Choose a chapter to open its starting page in the PDF. Page numbers below refer to PDF pages.</p>
    <ol class="guilds-chapters">
${chapters.map(c=>`      <li><a href="${book.slug}.pdf#page=${c.page}"><span><span class="guilds-chapter-number">Chapter ${c.number}</span><span class="guilds-chapter-title">${escape(c.title)}</span></span><span class="guilds-chapter-page">p. ${c.page} <span aria-hidden="true">↗</span></span></a></li>`).join('\n')}
    </ol>
  </section>
  <aside class="guilds-more"><a href="../guilds-and-dragons.html">← Back to the collection</a><a href="${other.file}">${i===0?'Next':'Previous'}: ${escape(other.title)} ${i===0?'→':''}</a></aside>
</main>
<footer><span>TBD’s Dragon Den · Guilds And Dragons</span><a href="../index.html">Return home ↗</a></footer>
</div></body>
</html>
`;
  fs.writeFileSync('guilds-and-dragons/'+book.file,html);
  console.log(book.title+': '+chapters.length+' chapter links generated.');
}
