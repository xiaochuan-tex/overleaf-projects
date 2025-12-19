const { mkdir, writeFile } = require('fs/promises');
const { join } = require('path');

async function getNextVersion() {
    const url = 'https://registry.npmjs.org/@xiaochuan-dev/overleaf/latest';

    const res = await fetch(url);
    const data = await res.json();

    const preVersion = data.version;
    const _v = preVersion.split('.');
    const preVNum = Number.parseInt(_v[2]);

    const nextV = `0.0.${preVNum + 1}`;
    return nextV;
}

async function writeJson() {
    const des = join(__dirname, '..', 'p', 'package.json');

    const nextV = await getNextVersion();

    const template = 
`{
  "name": "@xiaochuan-dev/overleaf",
  "version": "${nextV}",
  "license": "MIT",
  "files": [
    "dist"
  ],
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  },
  "packageManager": "yarn@1.22.22"
}`;
    await mkdir(join(__dirname, '..', 'p'));

    await writeFile(des, template, 'utf-8');
}

;(async() => {
    await writeJson();
})();