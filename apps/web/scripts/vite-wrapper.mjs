/* global process, queueMicrotask */

import { EventEmitter } from 'node:events';
import childProcess from 'node:child_process';
import { createRequire, syncBuiltinESMExports } from 'node:module';
import path from 'node:path';
import { PassThrough } from 'node:stream';
import { pathToFileURL } from 'node:url';

if (process.platform === 'win32') {
  const originalExec = childProcess.exec;

  childProcess.exec = function patchedExec(command, options, callback) {
    const normalizedCommand = typeof command === 'string' ? command.trim().toLowerCase() : '';

    if (normalizedCommand === 'net use') {
      let resolvedCallback = callback;

      if (typeof options === 'function') {
        resolvedCallback = options;
      }

      queueMicrotask(() => {
        resolvedCallback?.(null, '', '');
      });

      const mockProcess = new EventEmitter();
      mockProcess.stdout = new PassThrough();
      mockProcess.stderr = new PassThrough();
      mockProcess.kill = () => true;

      return mockProcess;
    }

    return originalExec.call(childProcess, command, options, callback);
  };

  syncBuiltinESMExports();
}

if (!process.argv.includes('--configLoader')) {
  process.argv.push('--configLoader', 'native');
}

const require = createRequire(import.meta.url);
const viteEntryPath = require.resolve('vite');
const viteBinPath = path.resolve(path.dirname(viteEntryPath), '../../bin/vite.js');

await import(pathToFileURL(viteBinPath).href);
