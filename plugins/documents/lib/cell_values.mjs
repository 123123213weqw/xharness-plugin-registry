// SPDX-License-Identifier: MIT. Public ExcelJS convenience accessor, no internals.
// cell.value can omit falsy formula results in its returned object. Never infer
// zero from absence: read the documented cell.result and preserve its exact type.
export function describedCellValue(cell) {
  const value=cell.value;
  if(value && typeof value==='object' && Object.hasOwn(value,'formula')) {
    const {result:omitted,...fields}=value;
    const result=cell.result;
    return result===undefined ? fields : {...fields,result};
  }
  return value;
}
