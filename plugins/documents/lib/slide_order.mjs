// SPDX-License-Identifier: MIT. Own finite p:/r: slide-list permutation, no file IO.
import {requireCondition as must} from './io.mjs';
const PRESENTATION='http://schemas.openxmlformats.org/presentationml/2006/main';
const RELATIONSHIPS='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
function attribute(tag,name) {
  const escaped=name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const matches=[...tag.matchAll(new RegExp('(?:^|\\s)'+escaped+'\\s*=\\s*(["\\\'])(.*?)\\1','g'))];
  must(matches.length===1,'missing or duplicate slide/root attribute '+name);
  return matches[0][2];
}
export function parseOrderArgument(raw) {
  must(typeof raw==='string' && raw.length>0 && raw.length<=80,'bounded comma-separated order required');
  const parts=raw.split(',').map(s=>s.trim());
  must(parts.length>=1 && parts.length<=20 && parts.every(s=>/^[1-9][0-9]?$/.test(s)),'order must contain positive 1-based integer indices');
  return parts.map(Number);
}
export function reorderSlideList(source,order) {
  must(typeof source==='string' && !/<!DOCTYPE|<!ENTITY|<!\[CDATA\[/i.test(source),'unsupported XML declarations');
  const root=[...source.matchAll(/<p:presentation(?:\s[^<>]*?)?>/g)];
  must(root.length===1,'unsupported presentation root spelling');
  must(attribute(root[0][0],'xmlns:p')===PRESENTATION && attribute(root[0][0],'xmlns:r')===RELATIONSHIPS,'presentation namespaces outside finite scope');
  const lists=[...source.matchAll(/(<p:sldIdLst(?:\s[^<>]*?)?>)([\s\S]*?)(<\/p:sldIdLst\s*>)/g)];
  must(lists.length===1,'exactly one ordinary slide ID list required');
  must(!/\sxmlns(?::|\s|=)/.test(lists[0][1]),'slide list namespace shadowing outside finite scope');
  const list=lists[0],entries=[...list[2].matchAll(/<p:sldId\s+[^<>]*?\/\s*>/g)];
  must(entries.length>=1 && entries.length<=20,'slide list count outside finite scope');
  must(list[2].replace(/<p:sldId\s+[^<>]*?\/\s*>/g,'').trim()==='','unsupported nonempty/nested/comment slide ID children');
  must(Array.isArray(order) && order.length===entries.length && order.every(n=>Number.isInteger(n) && n>=1 && n<=entries.length) && new Set(order).size===entries.length,'order must be a full unique permutation of existing slides');
  const ids=[],rels=[];
  for(const match of entries) {
    const tag=match[0];must(!/\sxmlns(?::|\s|=)/.test(tag),'namespace shadowing outside finite scope');
    const id=attribute(tag,'id'),rel=attribute(tag,'r:id');
    must(/^[0-9]+$/.test(id) && Number.isSafeInteger(Number(id)) && Number(id)>=256 && Number(id)<=4294967295,'invalid slide ID');
    must(/^[A-Za-z_][A-Za-z0-9_.-]{0,127}$/.test(rel),'invalid bounded relationship ID');ids.push(Number(id));rels.push(rel);
  }
  must(new Set(ids).size===ids.length && new Set(rels).size===rels.length,'duplicate slide/relationship ID');
  // Keep exact element bytes/IDs. Only list order/its inter-element whitespace changes.
  const replacement=list[1]+order.map(n=>entries[n-1][0]).join('')+list[3];
  const value=order.every((n,i)=>n===i+1)?source:source.slice(0,list.index)+replacement+source.slice(list.index+list[0].length);
  return {xml:value,original_relationship_ids:rels,ordered_relationship_ids:order.map(n=>rels[n-1]),order:[...order],slide_count:entries.length};
}
