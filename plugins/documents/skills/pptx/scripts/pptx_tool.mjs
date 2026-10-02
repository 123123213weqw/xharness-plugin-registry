// SPDX-License-Identifier: MIT. Portable plugin backend, separate from Codex QA.
import fs from 'node:fs/promises';
import path from 'node:path';
import PptxGenJS from 'pptxgenjs';
import JSZip from 'jszip';
import { XMLValidator, XMLParser } from 'fast-xml-parser';
import {parseOrderArgument,reorderSlideList} from '../../../lib/slide_order.mjs';
import { InputError, requireCondition as must, text, keys, digest, loadJson, readPackage, publish, parseCli, runMain } from '../../../lib/io.mjs';

function xml(payload) {
  const value = new TextDecoder('utf-8', { fatal: true }).decode(payload);
  must(!/<!DOCTYPE|<!ENTITY|<!\[CDATA\[/i.test(value), 'DTD, entities and CDATA are outside this narrow XML scope');
  must(XMLValidator.validate(value) === true, 'malformed XML part');
  return value;
}
function decode(value) {
  return value.replace(/&(#x[0-9a-f]+|#[0-9]+|amp|lt|gt|quot|apos);/gi, (_, entity) => {
    if (entity[0] === '#') return String.fromCodePoint(entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1)));
    return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" }[entity.toLowerCase()];
  });
}
function escape(value) { return value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;'); }
function texts(value) { return [...value.matchAll(/<a:t(?:\s[^>]*)?>([^<]*)<\/a:t>/g)].map(match => decode(match[1])); }
async function packageRead(file) {
  const result = await readPackage(file, 'pptx');
  for (const [name, payload] of result.parts) if (name.endsWith('.xml') || name.endsWith('.rels')) xml(payload);
  return result;
}
function snapshot(result) {
  const parser = new XMLParser({ ignoreAttributes:false, processEntities:false });
  const definition = parser.parse(xml(result.parts.get('ppt/presentation.xml')))?.['p:presentation']?.['p:sldIdLst']?.['p:sldId'];
  must(definition, 'unsupported or absent presentation slide list');
  const relPart = result.parts.get('ppt/_rels/presentation.xml.rels');
  must(relPart, 'missing presentation relationships');
  const relDefinition = parser.parse(xml(relPart))?.Relationships?.Relationship;
  const relationships = new Map((Array.isArray(relDefinition) ? relDefinition : [relDefinition]).filter(Boolean).map(r => [r['@_Id'],r]));
  const slides = (Array.isArray(definition) ? definition : [definition]).map(item => {
    const relation = relationships.get(item['@_r:id']);
    must(relation && relation['@_TargetMode'] !== 'External', 'unresolved or external slide relationship');
    const target = relation['@_Target'];
    must(typeof target === 'string', 'invalid slide target');
    const name = target.startsWith('/') ? target.slice(1) : path.posix.normalize('ppt/' + target);
    must(/^ppt\/slides\/[^/]+\.xml$/.test(name) && result.parts.has(name), 'slide relationship outside package');
    return name;
  });
  must(slides.length > 0 && slides.length <= 20, 'slide count outside supported range');
  return { ...result.receipt, ...result.bounds, slide_part_count: slides.length,
    slides: slides.map((name,index) => { const data = xml(result.parts.get(name)); return { slide:index+1, part: name, text_runs: texts(data), native_tables: [...data.matchAll(/<a:tbl(?:\s|>)/g)].length }; }),
    notes: [...result.parts.keys()].filter(n => /^ppt\/notesSlides\/notesSlide[1-9][0-9]*\.xml$/.test(n)).map(name => ({ part: name, text_runs: texts(xml(result.parts.get(name))) })),
    limitations: ['Only ordinary p:/a: namespace spellings supported by narrow text/slide inspection.', 'Not rendering, chart/image extraction, full schema validation, animation or application fidelity.'] };
}
function validatePlan(plan) {
  keys(plan, ['title','author','slides'], ['font']); text(plan.title,120); text(plan.author,120); if (plan.font) text(plan.font,80);
  must(Array.isArray(plan.slides) && plan.slides.length >= 1 && plan.slides.length <= 10, 'slide count outside authoring scope');
  for (const slide of plan.slides) {
    keys(slide, ['title','paragraphs'], ['table','notes']); text(slide.title,100);
    must(Array.isArray(slide.paragraphs) && slide.paragraphs.length >= 1 && slide.paragraphs.length <= 4, 'paragraph count outside range');
    slide.paragraphs.forEach(p => text(p,300)); if (slide.notes) text(slide.notes,2000);
    if (slide.table) {
      keys(slide.table, ['headers','rows','widths_inches']); const { headers, rows, widths_inches: widths } = slide.table;
      must(Array.isArray(headers) && headers.length >= 1 && headers.length <= 6 && Array.isArray(rows) && rows.length >= 1 && rows.length <= 6, 'table dimensions outside range');
      must(Array.isArray(widths) && widths.length === headers.length && widths.every(x => typeof x === 'number' && x >= .8 && x <= 12) && Math.abs(widths.reduce((a,b)=>a+b,0) - 12) < .001, 'table widths must sum to 12 inches');
      for (const row of [headers, ...rows]) { must(Array.isArray(row) && row.length === headers.length, 'table width mismatch'); row.forEach(c => text(c,120)); }
    }
  }
}
async function create(planFile, output) {
  const plan = await loadJson(planFile); validatePlan(plan);
  const pres = new PptxGenJS(); pres.layout = 'LAYOUT_WIDE'; pres.author = plan.author; pres.title = plan.title;
  const font = plan.font ?? 'Arial'; pres.theme = { headFontFace: font, bodyFontFace: font, lang: 'en-US' };
  for (const [index, content] of plan.slides.entries()) {
    const slide = pres.addSlide(); slide.background = { color: 'FFFFFF' };
    slide.addText(content.title, { x:.65, y:.42, w:12, h:.8, fontFace:font, fontSize:28, bold:true, color:'142735', margin:0, breakLine:false, fit:'none' });
    slide.addText(content.paragraphs.join('\n'), { x:.65, y:1.45, w:12, h:content.table ? 1.6 : 4.6, fontFace:font, fontSize:19, color:'202020', margin:0, paraSpaceAfter:10, fit:'none', valign:'top' });
    if (content.table) {
      const t = content.table;
      const rows = [t.headers.map(c => ({ text:c, options:{ bold:true, fill:'E7E6E6' } })), ...t.rows];
      slide.addTable(rows, { x:.65, y:3.3, w:12, h:2.8, colW:t.widths_inches, fontFace:font, fontSize:17, color:'202020', border:{ type:'solid', pt:.6, color:'888888' }, margin:8, valign:'middle', autoPage:false });
    }
    slide.addText(String(index+1), { x:12.25, y:6.95, w:.4, h:.25, fontFace:font, fontSize:10, color:'666666', margin:0, align:'right' });
    if (content.notes) slide.addNotes(content.notes);
  }
  const receipt = await publish(output, [planFile], 'pptx', tmp => pres.writeFile({ fileName:tmp, compression:true }));
  const result = snapshot(await packageRead(output));
  must(result.slide_part_count === plan.slides.length, 'actual slide count mismatch');
  return { ...result, receipt, backend:'pptxgenjs@4.0.1', font_requested:font, font_available_not_verified:true };
}
async function replace(input, output, oldText, newText) {
  text(oldText,500); text(newText,500);
  const before = await packageRead(input), changes = [];
  for (const [name,payload] of before.parts) {
    if (!/^ppt\/slides\/slide[1-9][0-9]*\.xml$/.test(name)) continue;
    let source = xml(payload);
    source = source.replace(/(<a:t(?:\s[^>]*)?>)([^<]*)(<\/a:t>)/g, (full,open,inner,close) => {
      if (decode(inner) !== oldText) return full;
      changes.push(name); return open + escape(newText) + close;
    });
    if (changes.includes(name)) before.parts.set(name,Buffer.from(source));
  }
  must(changes.length === 1, 'replace requires exactly one complete matching text run');
  const zip = new JSZip(); for (const [name,payload] of before.parts) zip.file(name,payload);
  await publish(output,[input],'pptx',async tmp => fs.writeFile(tmp,await zip.generateAsync({ type:'nodebuffer', compression:'DEFLATE' })));
  const after = await packageRead(output);
  const original = await packageRead(input);
  must(original.receipt.sha256 === before.receipt.sha256, 'input changed during replacement');
  for (const [name,payload] of original.parts) if (name !== changes[0]) must(after.parts.has(name) && digest(after.parts.get(name)) === digest(payload), 'unrequested package part changed');
  return { ...snapshot(after), changed_part:changes[0], source_sha256:original.receipt.sha256, other_uncompressed_parts_preserved:true };
}

async function reorder(input,output,orderText) {
  const before=await packageRead(input),originalSnapshot=snapshot(before);
  const source=xml(before.parts.get('ppt/presentation.xml'));
  const plan=reorderSlideList(source,parseOrderArgument(orderText));
  // Original snapshot historically uses Map; explicitly reject ambiguous IDs for this transform.
  const parser=new XMLParser({ignoreAttributes:false,processEntities:false});
  const relDefinition=parser.parse(xml(before.parts.get('ppt/_rels/presentation.xml.rels')))?.Relationships?.Relationship;
  const rels=(Array.isArray(relDefinition)?relDefinition:[relDefinition]).filter(Boolean);
  must(rels.length>0 && new Set(rels.map(r=>r['@_Id'])).size===rels.length,'duplicate/absent presentation relationship IDs');
  for(const ident of plan.original_relationship_ids) {
    const relation=rels.find(r=>r['@_Id']===ident);
    must(relation && relation['@_Type']==='http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide' && relation['@_TargetMode']!=='External','slide relationship type/mode outside finite scope');
  }
  const contentTypes=parser.parse(xml(before.parts.get('[Content_Types].xml')))?.Types?.Override;
  const types=(Array.isArray(contentTypes)?contentTypes:[contentTypes]).filter(Boolean);
  must(types.filter(t=>t['@_PartName']==='/ppt/presentation.xml' && t['@_ContentType']==='application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml').length===1,'ordinary PPTX presentation content type required');
  const expectedParts=plan.order.map(n=>originalSnapshot.slides[n-1].part);
  const parts=new Map(before.parts);parts.set('ppt/presentation.xml',Buffer.from(plan.xml));
  const zip=new JSZip();for(const [name,payload] of parts)zip.file(name,payload,{createFolders:false});
  let verified;
  const receipt=await publish(output,[input],'pptx',async tmp=>{
    await fs.writeFile(tmp,await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'}));
    const actual=await packageRead(tmp),observed=snapshot(actual);
    must(actual.parts.size===before.parts.size,'package part count changed during reorder');
    must(observed.slide_part_count===expectedParts.length && observed.slides.every((s,i)=>s.part===expectedParts[i]),'saved slide relationship order mismatch');
    for(const [name,payload] of before.parts)if(name!=='ppt/presentation.xml')must(actual.parts.has(name) && digest(actual.parts.get(name))===digest(payload),'unrequested package part changed during reorder');
    must(digest(actual.parts.get('ppt/presentation.xml'))===digest(parts.get('ppt/presentation.xml')),'saved presentation XML mismatch');
    must((await packageRead(input)).receipt.sha256===before.receipt.sha256,'input changed before reorder publication');
    verified=observed;
  });
  return {...verified,path:receipt.path,bytes:receipt.bytes,sha256:receipt.sha256,receipt,changed_part:plan.xml===source?null:'ppt/presentation.xml',source_sha256:before.receipt.sha256,order:plan.order,other_uncompressed_parts_preserved:true,preservation_checked_before_publication:true,embedded_slide_numbers_not_rewritten:true,limitations:[...verified.limitations,'Reorder requires complete unique permutation; no slide deletion/insertion/duplication or repair.','Existing notes/shared object bytes retained; original shared graph not fully XSD-validated.','Visible embedded slide-number text remains unchanged; archive compression bytes may differ.']};
}

await runMain(async () => {
  const { operation, options:o } = parseCli(process.argv.slice(2),['create','inspect','replace','reorder'],['input','output','old','new','order']);
  must(o.input, 'input is required');
  if (operation === 'inspect') { must(!o.output && !o.old && !o.new && !o.order, 'inspect options outside scope'); return snapshot(await packageRead(o.input)); }
  must(o.output, 'output is required');
  if (operation === 'create') { must(!o.old && !o.new && !o.order, 'create does not accept replacement options'); return create(o.input,o.output); }
  if(operation==='reorder'){must(o.order && !o.old && !o.new,'reorder requires only order/input/output');return reorder(o.input,o.output,o.order);}
  must(!o.order,'replace does not accept reorder options');return replace(o.input,o.output,o.old,o.new);
});
