// SPDX-License-Identifier: MIT. Public portable backend, no Codex runtime dependency.
import ExcelJS from 'exceljs';
import { requireCondition as must, text, keys, loadJson, readPackage, receipt, publish, parseCli, runMain } from '../../../lib/io.mjs';
import { address, recalculate } from '../../../lib/formulas.mjs';
import { describedCellValue } from '../../../lib/cell_values.mjs';

function typed(value) {
  if(value===null||typeof value==='boolean'||(typeof value==='number'&&Number.isFinite(value)))return value;
  if(typeof value==='string') { must(value.length<=1000&&!/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff\uD800-\uDFFF]/u.test(value),'invalid cell string');return value; }
  keys(value,['date']);must(/^\d{4}-\d{2}-\d{2}$/.test(value.date),'date must use yyyy-mm-dd');
  const date=new Date(value.date+'T00:00:00Z');must(Number.isFinite(date.getTime())&&date.toISOString().slice(0,10)===value.date,'invalid date');return date;
}
function range(value) {
  const [first,last,...extra]=value.split(':');must(extra.length===0,'invalid range');
  const a=address(first),b=address(last??first);must(a.row<=b.row&&a.column<=b.column,'reversed range');return value;
}
function describe(workbook) {
  must(workbook.worksheets.length>=1&&workbook.worksheets.length<=5,'worksheet count outside scope');
  return { sheets:workbook.worksheets.map(sheet=>{
    must(sheet.rowCount<=99&&sheet.columnCount<=12,'worksheet exceeds bounded A1:L99 scope');
    const cells=[];sheet.eachRow(row=>row.eachCell(cell=>cells.push({cell:cell.address,value:describedCellValue(cell),number_format:cell.numFmt??null})));
    return {name:sheet.name,rows:sheet.rowCount,columns:sheet.columnCount,cells,views:sheet.views};
  }),limitations:['Not render QA, complete workbook fidelity, charts, pivot tables, macros or unrestricted Excel formula evaluation.'] };
}
async function read(file) {
  const source=await readPackage(file,'xlsx');
  const workbook=new ExcelJS.Workbook();await workbook.xlsx.load(source.bytes);describe(workbook);
  return {workbook,source};
}
function validatePlan(plan) {
  keys(plan,['title','author','sheets']);text(plan.title,120);text(plan.author,120);
  must(Array.isArray(plan.sheets)&&plan.sheets.length>=1&&plan.sheets.length<=5,'sheets outside range');
  const names=new Set();
  for(const sheet of plan.sheets) {
    keys(sheet,['name','values','widths'],['formulas','formats','header_row','freeze_rows']);text(sheet.name,31);
    must(!/[*?:/\\\[\]]/.test(sheet.name)&&!sheet.name.startsWith("'")&&!sheet.name.endsWith("'")&&!names.has(sheet.name.toLowerCase()),'invalid or duplicate sheet name');names.add(sheet.name.toLowerCase());
    must(Array.isArray(sheet.values)&&sheet.values.length>=1&&sheet.values.length<=99,'row count outside range');
    const width=sheet.values[0]?.length;must(width>=1&&width<=12,'column count outside range');
    for(const row of sheet.values) {must(Array.isArray(row)&&row.length===width,'values must be rectangular');row.forEach(typed);}
    must(Array.isArray(sheet.widths)&&sheet.widths.length===width&&sheet.widths.every(w=>typeof w==='number'&&w>=8&&w<=60),'invalid column widths');
    if(sheet.header_row!==undefined)must(Number.isInteger(sheet.header_row)&&sheet.header_row>=1&&sheet.header_row<=sheet.values.length,'invalid header row');
    if(sheet.freeze_rows!==undefined)must(Number.isInteger(sheet.freeze_rows)&&sheet.freeze_rows>=0&&sheet.freeze_rows<=sheet.values.length,'invalid frozen rows');
    if(sheet.formulas!==undefined) {must(Array.isArray(sheet.formulas)&&sheet.formulas.length<=200,'formula count outside range');const used=new Set();
      for(const f of sheet.formulas){keys(f,['cell','formula']);const a=address(f.cell);must(!used.has(a.normalized),'duplicate formula cell');used.add(a.normalized);text(f.formula,1000);must(f.formula.startsWith('='),'formula must start with =');}
    }
    if(sheet.formats!==undefined) {must(Array.isArray(sheet.formats)&&sheet.formats.length<=30,'format count outside range');for(const f of sheet.formats){keys(f,['range','code']);range(f.range);text(f.code,100);}}
  }
}
async function create(planFile,output) {
  const plan=await loadJson(planFile);validatePlan(plan);
  const workbook=new ExcelJS.Workbook();workbook.creator=plan.author;workbook.title=plan.title;
  // Create all sheets before formulas so cross-sheet dependencies resolve.
  for(const definition of plan.sheets)workbook.addWorksheet(definition.name,{views:[{showGridLines:false,...(definition.freeze_rows ? {state:'frozen',ySplit:definition.freeze_rows}: {})}]});
  for(const definition of plan.sheets) {
    const sheet=workbook.getWorksheet(definition.name);sheet.addRows(definition.values.map(row=>row.map(typed)));
    definition.widths.forEach((width,index)=>{sheet.getColumn(index+1).width=width;});
    sheet.eachRow(row=>{row.height=22;row.eachCell(cell=>{
      cell.font={name:'Arial',size:11,color:{argb:'FF202020'}};cell.alignment={vertical:'middle',wrapText:true,horizontal:typeof cell.value==='number'?'right':'left'};
      if(cell.value instanceof Date)cell.numFmt='yyyy-mm-dd';
    });});
    if(definition.header_row)sheet.getRow(definition.header_row).eachCell(cell=>{cell.font={name:'Arial',size:11,bold:true,color:{argb:'FFFFFFFF'}};cell.fill={type:'pattern',pattern:'solid',fgColor:{argb:'FF334155'}};});
    for(const f of definition.formulas??[])sheet.getCell(f.cell).value={formula:f.formula.slice(1)};
    for(const f of definition.formats??[]) {
      const [first,last]=f.range.split(':'),a=address(first),b=address(last??first);
      for(let row=a.row;row<=b.row;row++)for(let col=a.column;col<=b.column;col++)sheet.getCell(row,col).numFmt=f.code;
    }
  }
  const calculations=recalculate(workbook);
  await publish(output,[planFile],'xlsx',tmp=>workbook.xlsx.writeFile(tmp));
  return {...await receipt(output),...describe(workbook),calculations,backend:'exceljs@4.4.0',calculation_scope:'own bounded numeric arithmetic/aggregates, numeric or boolean comparisons and lazy three-argument IF; no general Excel engine'};
}
async function edit(input,planFile,output) {
  const plan=await loadJson(planFile);keys(plan,['sheet','changes']);text(plan.sheet,31);
  must(Array.isArray(plan.changes)&&plan.changes.length>=1&&plan.changes.length<=50,'change count outside range');
  const {workbook,source}=await read(input),before=describe(workbook),sheet=workbook.getWorksheet(plan.sheet);must(sheet,'unknown worksheet');
  const seen=new Set();
  for(const change of plan.changes) {
    keys(change,['cell','old','value']);const normalized=address(change.cell).normalized;must(!seen.has(normalized),'duplicate change cell');seen.add(normalized);
    const cell=sheet.getCell(normalized);must(cell.value===change.old,'old value must exactly match primitive input cell');
    must(cell.value===null||typeof cell.value!=='object','cannot edit formula/rich/date cells through primitive input edit');cell.value=typed(change.value);
  }
  const calculations=recalculate(workbook);
  await publish(output,[input,planFile],'xlsx',tmp=>workbook.xlsx.writeFile(tmp));
  must((await receipt(input)).sha256===source.receipt.sha256,'input changed during edit');
  return {...await receipt(output),...describe(workbook),calculations,source_sha256:source.receipt.sha256,before,
    preservation_scope:'Targeted values and formula caches only intended; imported round-trip feature preservation requires independent verification.'};
}

await runMain(async()=>{
  const {operation,options:o}=parseCli(process.argv.slice(2),['create','inspect','set-cells'],['input','output','plan']);must(o.input,'input is required');
  if(operation==='inspect'){must(!o.output&&!o.plan,'inspect options outside scope');const {workbook,source}=await read(o.input);return {...source.receipt,...source.bounds,...describe(workbook)};}
  must(o.output,'output is required');if(operation==='create'){must(!o.plan,'create does not accept edit plan');return create(o.input,o.output);}
  must(o.plan,'set-cells needs explicit edit plan');return edit(o.input,o.plan,o.output);
});
