// SPDX-License-Identifier: MIT. Owned bounded inputs and exclusive publication.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { inflateRawSync } from 'node:zlib';

export class InputError extends Error {}
export function requireCondition(ok, message) { if (!ok) throw new InputError(message); }
export function text(value, max = 2000) {
  requireCondition(typeof value === 'string' && value.trim().length && value.length <= max &&
    !/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/u.test(value) &&
    !/[\uD800-\uDFFF]/u.test(value), 'invalid bounded text');
  return value;
}
export function keys(value, required, optional = []) {
  requireCondition(value && typeof value === 'object' && !Array.isArray(value) &&
    required.every(k => Object.hasOwn(value, k)) && Object.keys(value).every(k => [...required, ...optional].includes(k)), 'invalid object keys');
}
export function digest(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let i = 0; i < 8; ++i) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
export async function loadJson(file) {
  const bytes = await fs.readFile(file);
  requireCondition(bytes.length > 0 && bytes.length <= 256 * 1024, 'empty or oversized JSON');
  try { return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); }
  catch (error) { throw new InputError('invalid UTF-8 JSON: ' + error.message); }
}
export async function receipt(file) {
  const bytes = await fs.readFile(file);
  return { path: path.resolve(file), bytes: bytes.length, sha256: digest(bytes) };
}

// Inspect standard ZIP central-directory bounds before the documented importer.
// This is not full OOXML schema validation. ZIP64/encryption/symlinks/macros are outside scope.
export function checkZip(bytes, kind) {
  requireCondition(bytes.length > 0 && bytes.length <= 10 * 1024 * 1024, 'empty or oversized package');
  let end = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); --i) {
    if (bytes.readUInt32LE(i) === 0x06054b50 && i + 22 + bytes.readUInt16LE(i + 20) === bytes.length) { end = i; break; }
  }
  requireCondition(end >= 0, 'corrupt ZIP end directory');
  const count = bytes.readUInt16LE(end + 10), size = bytes.readUInt32LE(end + 12), offset = bytes.readUInt32LE(end + 16);
  requireCondition(bytes.readUInt16LE(end + 4) === 0 && bytes.readUInt16LE(end + 6) === 0 &&
    bytes.readUInt16LE(end + 8) === count && count > 0 && count <= 512 && offset + size === end, 'unsupported ZIP directory');
  let cursor = offset, expanded = 0;
  const names = new Set(), parts = new Map();
  for (let i = 0; i < count; ++i) {
    requireCondition(cursor + 46 <= end && bytes.readUInt32LE(cursor) === 0x02014b50, 'corrupt ZIP member directory');
    const flags = bytes.readUInt16LE(cursor + 8), method = bytes.readUInt16LE(cursor + 10);
    const compressed = bytes.readUInt32LE(cursor + 20), uncompressed = bytes.readUInt32LE(cursor + 24);
    const n = bytes.readUInt16LE(cursor + 28), extra = bytes.readUInt16LE(cursor + 30), comment = bytes.readUInt16LE(cursor + 32);
    const local = bytes.readUInt32LE(cursor + 42), attributes = bytes.readUInt32LE(cursor + 38);
    requireCondition(cursor + 46 + n + extra + comment <= end && n > 0 && !(flags & 1) && [0, 8].includes(method) &&
      uncompressed !== 0xffffffff && compressed !== 0xffffffff && local !== 0xffffffff, 'unsupported or corrupt ZIP member');
    let name;
    try { name = new TextDecoder('utf-8', { fatal: true }).decode(bytes.subarray(cursor + 46, cursor + 46 + n)); }
    catch { throw new InputError('unsupported member-name encoding'); }
    requireCondition(!name.startsWith('/') && !name.includes('\\') && !name.includes('\0') &&
      !name.split('/').includes('..') && !names.has(name) && ((attributes >>> 16) & 0xf000) !== 0xa000 &&
      !name.startsWith('_xmlsignatures/') && !name.endsWith('vbaProject.bin'), 'unsafe, duplicate, signed or macro-bearing member');
    requireCondition(local + 30 <= offset && bytes.readUInt32LE(local) === 0x04034b50, 'invalid member local offset');
    const localNameLength = bytes.readUInt16LE(local + 26), localExtraLength = bytes.readUInt16LE(local + 28);
    requireCondition(local + 30 + localNameLength + localExtraLength + compressed <= offset &&
      bytes.readUInt16LE(local + 8) === method && bytes.readUInt16LE(local + 6) === flags && localNameLength === n &&
      bytes.subarray(local + 30, local + 30 + n).equals(bytes.subarray(cursor + 46, cursor + 46 + n)), 'inconsistent member header');
    expanded += uncompressed;
    requireCondition(expanded <= 25 * 1024 * 1024, 'expanded package exceeds byte limit');
    const dataStart = local + 30 + localNameLength + localExtraLength;
    const encoded = bytes.subarray(dataStart, dataStart + compressed);
    let payload;
    try { payload = method === 0 ? encoded : inflateRawSync(encoded, { maxOutputLength: Math.max(1, Math.min(uncompressed, 25 * 1024 * 1024)) }); }
    catch { throw new InputError('corrupt or oversized deflated member'); }
    requireCondition(payload.length === uncompressed && crc32(payload) === bytes.readUInt32LE(cursor + 16), 'member size or CRC mismatch');
    parts.set(name, payload);
    names.add(name);
    cursor += 46 + n + extra + comment;
  }
  requireCondition(cursor === end && ['[Content_Types].xml', '_rels/.rels', kind === 'pptx' ? 'ppt/presentation.xml' : 'xl/workbook.xml'].every(n => names.has(n)), 'missing required package parts');
  return { members: count, expanded_bytes: expanded, kind, parts };
}
export async function readPackage(file, kind) {
  const info = await fs.stat(file);
  requireCondition(info.isFile() && info.size > 0 && info.size <= 10 * 1024 * 1024, 'empty or oversized input package');
  const bytes = await fs.readFile(file);
  const checked = checkZip(bytes, kind);
  const { parts, ...bounds } = checked;
  return { bytes, bounds, parts, receipt: { path: path.resolve(file), bytes: bytes.length, sha256: digest(bytes) } };
}

export async function publish(output, inputs, kind, serialize) {
  requireCondition(path.isAbsolute(output) && inputs.every(i => path.resolve(i) !== path.resolve(output)), 'output must be absolute and separate from input');
  const parent = path.dirname(output);
  requireCondition((await fs.stat(parent)).isDirectory(), 'output parent missing');
  const temporary = path.join(parent, '.document-tool-' + randomUUID() + '.tmp.' + kind);
  const handle = await fs.open(temporary, 'wx', 0o600);
  await handle.close();
  try {
    await serialize(temporary);
    await readPackage(temporary, kind);
    const sealed = await fs.open(temporary, 'r');
    try { await sealed.sync(); } finally { await sealed.close(); }
    try { await fs.link(temporary, output); }
    catch (error) { if (error.code === 'EEXIST') throw new InputError('exclusive publication refused existing output'); throw error; }
    return await receipt(output);
  } finally { await fs.unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; }); }
}

export function parseCli(argv, operations, allowed) {
  const [operation, ...rest] = argv;
  requireCondition(operations.includes(operation), 'unsupported operation');
  const options = {};
  requireCondition(rest.length % 2 === 0, 'options require values');
  for (let i = 0; i < rest.length; i += 2) {
    requireCondition(rest[i].startsWith('--'), 'invalid option');
    const key = rest[i].slice(2);
    requireCondition(allowed.includes(key) && !Object.hasOwn(options, key), 'unknown or duplicate option');
    options[key] = rest[i + 1];
  }
  return { operation, options };
}
export async function runMain(body) {
  try { console.log(JSON.stringify({ ok: true, pid: process.pid, result: await body() })); }
  catch (error) {
    console.log(JSON.stringify({ ok: false, pid: process.pid, error: error.message, error_class: error.constructor.name }));
    process.exitCode = error instanceof InputError ? 2 : 3;
  }
}
