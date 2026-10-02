// SPDX-License-Identifier: MIT. Bounded numeric/boolean AST evaluator, no eval.
import { requireCondition as must } from './io.mjs';

export function address(value) {
  const found = typeof value === 'string' && /^\$?([A-L])\$?([1-9][0-9]?)$/.exec(value);
  must(found, 'cell address outside A1:L99 scope');
  return {row:Number(found[2]), column:found[1].charCodeAt(0)-64, normalized:found[1]+found[2]};
}
function tokens(formula) {
  must(typeof formula === 'string' && formula.length <= 1000 && !/[\[\]|]/.test(formula), 'unsupported formula');
  formula=formula.trim();
  const parts=[], regexp=/\s*(?:('(?:[^']|'')+'!)|(\d+(?:\.\d*)?|\.\d+)|([A-Za-z_][A-Za-z_0-9]*!(?!=))|(\$?[A-L]\$?[1-9][0-9]?)|([A-Za-z]+)|(<=|>=|<>|!=|==|[=<>+*/():,-]))/gy;
  let cursor=0;
  while(cursor<formula.length) {
    regexp.lastIndex=cursor;const found=regexp.exec(formula);
    must(found && found.index===cursor, 'unsupported formula token');
    parts.push(found.slice(1).find(x=>x!==undefined));cursor=regexp.lastIndex;
    must(parts.length<=400, 'formula token limit');
  }
  return parts;
}
const comparisons=['=','==','<>','!=','<','<=','>','>='];
const aggregates=['SUM','MIN','MAX','AVERAGE'];
// Parse both IF branches before evaluating either. Invalid syntax/functions are
// refused even in an unselected branch; cell reads/arithmetic occur only later.
function parse(formula, sheetName) {
  const list=tokens(formula);let position=0,nesting=0;
  const peek=()=>list[position],take=()=>list[position++];
  function reference(defaultSheet=sheetName) {
    let target=defaultSheet;
    if(peek()?.endsWith('!')) {
      const token=take().slice(0,-1);
      target=token.startsWith("'")?token.slice(1,-1).replaceAll("''", "'"):token;
    }
    return {kind:'ref',sheet:target,cell:address(take()).normalized};
  }
  function atom() {
    must(++nesting<100, 'formula syntax depth limit');
    try {
      if(['+','-'].includes(peek())) {const op=take();return {kind:'unary',op,value:atom()};}
      if(peek()==='(') {take();const result=expression();must(take()===')','missing closing parenthesis');return result;}
      if(/^\d|^\./.test(peek()??'')) {const number=Number(take());must(Number.isFinite(number),'nonfinite numeric literal');return {kind:'literal',value:number};}
      if(['TRUE','FALSE'].includes((peek()??'').toUpperCase()))return {kind:'literal',value:take().toUpperCase()==='TRUE'};
      if(list[position+1]==='(') {
        const func=take().toUpperCase();take();
        must(func==='IF'||aggregates.includes(func),'unsupported formula function');
        const args=[];
        must(peek()!==')','invalid function arguments');
        while(true) {
          const argument=expression();
          if(peek()===':') {
            must(func!=='IF' && argument.kind==='ref','range only allowed in aggregate arguments');
            take();const last=reference(argument.sheet);
            must(argument.sheet===last.sheet,'cross-sheet range endpoints');
            const a=address(argument.cell),b=address(last.cell);
            must(a.row<=b.row && a.column<=b.column,'reversed range');
            args.push({kind:'range',first:argument,last});
          } else args.push(argument);
          if(peek()!==',')break;
          take();must(peek()!==')','invalid function arguments');
        }
        must(take()===')' && (func!=='IF'||args.length===3),'invalid function arguments');
        return {kind:'function',func,args};
      }
      return reference();
    } finally {--nesting;}
  }
  function product() {
    let node=atom();
    while(['*','/'].includes(peek()))node={kind:'binary',op:take(),left:node,right:atom()};
    return node;
  }
  function addition() {
    let node=product();
    while(['+','-'].includes(peek()))node={kind:'binary',op:take(),left:node,right:product()};
    return node;
  }
  function expression() {
    let node=addition();
    if(comparisons.includes(peek()))node={kind:'compare',op:take(),left:node,right:addition()};
    must(!comparisons.includes(peek()),'chained comparison outside scope');
    return node;
  }
  const tree=expression();must(position===list.length,'invalid formula trailing tokens');return tree;
}
const finiteScalar=value=>(typeof value==='number' && Number.isFinite(value))||typeof value==='boolean';
function number(value) {must(typeof value==='number' && Number.isFinite(value),'formula requires numeric nonblank input');return value;}

export function recalculate(workbook) {
  const cache=new Map(),active=new Set(),pending=new Map();let steps=0;
  const step=()=>must(++steps<=200000,'formula evaluation step limit');
  function value(sheetName,ref,depth=0) {
    step();must(depth<100,'formula dependency depth limit');
    const cellRef=address(ref).normalized,id=sheetName+'!'+cellRef;
    if(cache.has(id))return cache.get(id);
    must(!active.has(id),'circular formula dependency');
    const sheet=workbook.getWorksheet(sheetName);must(sheet,'missing formula worksheet');
    const cell=sheet.getCell(cellRef),content=cell.value;let result;
    if(content && typeof content==='object' && 'formula' in content) {
      active.add(id);
      try {result=evaluate(parse(content.formula,sheetName),depth+1);}
      finally {active.delete(id);}
      pending.set(id,{cell,formula:content.formula,result});
    } else {must(finiteScalar(content),'formula requires numeric or boolean nonblank input');result=content;}
    must(finiteScalar(result),'invalid or nonfinite formula result');cache.set(id,result);return result;
  }
  function evaluate(node,depth) {
    step();
    if(node.kind==='literal')return node.value;
    if(node.kind==='ref')return value(node.sheet,node.cell,depth);
    if(node.kind==='unary') {const n=number(evaluate(node.value,depth));return node.op==='-'?-n:n;}
    if(node.kind==='binary') {
      const a=number(evaluate(node.left,depth)),b=number(evaluate(node.right,depth));
      must(node.op!=='/'||b!==0,'division by zero');
      const n=node.op==='+'?a+b:node.op==='-'?a-b:node.op==='*'?a*b:a/b;
      must(Number.isFinite(n),'invalid or nonfinite formula result');return n;
    }
    if(node.kind==='compare') {
      const a=evaluate(node.left,depth),b=evaluate(node.right,depth);
      must(finiteScalar(a)&&finiteScalar(b)&&typeof a===typeof b,'comparison requires same numeric or boolean types');
      if(['=','=='].includes(node.op))return a===b;
      if(['<>','!='].includes(node.op))return a!==b;
      must(typeof a==='number','ordered comparison requires numeric inputs');
      return node.op==='<'?a<b:node.op==='<='?a<=b:node.op==='>'?a>b:a>=b;
    }
    must(node.kind==='function','invalid formula AST');
    if(node.func==='IF') {
      const condition=evaluate(node.args[0],depth);
      must(finiteScalar(condition),'IF condition requires numeric or boolean input');
      return evaluate(node.args[condition?1:2],depth);
    }
    const numbers=[];
    for(const argument of node.args) {
      if(argument.kind==='range') {
        const a=address(argument.first.cell),b=address(argument.last.cell);
        for(let row=a.row;row<=b.row;row++)for(let col=a.column;col<=b.column;col++)
          numbers.push(number(value(argument.first.sheet,String.fromCharCode(64+col)+row,depth)));
      } else numbers.push(number(evaluate(argument,depth)));
    }
    const n=node.func==='MIN'?Math.min(...numbers):node.func==='MAX'?Math.max(...numbers):numbers.reduce((a,b)=>a+b,0)/(node.func==='AVERAGE'?numbers.length:1);
    must(Number.isFinite(n),'invalid or nonfinite formula result');return n;
  }
  for(const sheet of workbook.worksheets)sheet.eachRow(row=>row.eachCell(cell=>{
    if(cell.value && typeof cell.value==='object' && 'formula' in cell.value)value(sheet.name,cell.address);
    else must(!cell.value || typeof cell.value!=='object' || !('sharedFormula' in cell.value),'shared/array formulas outside bounded edit scope');
  }));
  // Only publish in-memory caches after every formula succeeds. A rejected
  // calculation therefore neither changes an earlier cache nor publishes XLSX.
  for(const {cell,formula,result} of pending.values())cell.value={formula,result};
  workbook.calcProperties.fullCalcOnLoad=true;
  return [...cache].map(([cell,result])=>({cell,result}));
}
