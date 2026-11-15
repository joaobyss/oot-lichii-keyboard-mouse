"""Replaces some payload files inside a PyInstaller onefile exe, keeping every other byte of the archive."""
import struct, sys, zlib, shutil
COOKIE = '!8sIIII64s'; CL = struct.calcsize(COOKIE); TF = '!IIIIBc'; TL = struct.calcsize(TF)
src, dst = sys.argv[1], sys.argv[2]
repl = dict(a.split('=', 1) for a in sys.argv[3:])      # entry name (with backslashes) = file
data = open(src, 'rb').read()
magic = b'MEI\014\013\012\013\016'
c = data.rfind(magic)
m, alen, toc_off, toc_len, pyver, pylib = struct.unpack(COOKIE, data[c:c + CL])
end = c + CL; start = end - alen
assert end == len(data), 'extra bytes after the archive'
toc = data[start + toc_off:start + toc_off + toc_len]
out_pkg = bytearray(data[start:start + toc_off])     # untouched data region
new_toc = bytearray(); pos = 0; done = set()
while pos < len(toc):
    elen, off, clen, ulen, comp, tc = struct.unpack(TF, toc[pos:pos + TL])
    raw = toc[pos:pos + elen]
    name = raw[TL:].rstrip(b'\0').decode('utf-8')
    if name in repl:
        blob = open(repl[name], 'rb').read()
        z = zlib.compress(blob, 9) if comp else blob
        noff = len(out_pkg); out_pkg += z
        raw = struct.pack(TF, elen, noff, len(z), len(blob), comp, tc) + raw[TL:]
        done.add(name); print('replaced', name, ulen, '->', len(blob))
    new_toc += raw; pos += elen
assert done == set(repl), 'not found: %s' % (set(repl) - done)
new_toc_off = len(out_pkg)
total = new_toc_off + len(new_toc) + CL
cookie = struct.pack(COOKIE, m, total, new_toc_off, len(new_toc), pyver, pylib)
open(dst, 'wb').write(data[:start] + bytes(out_pkg) + bytes(new_toc) + cookie)
print('wrote', dst)
