import type { languages } from 'monaco-editor';

export const MINILANG_LANGUAGE_ID = 'minilang';

export const miniLangConfig: languages.LanguageConfiguration = {
  comments: {
    lineComment: '//',
  },
  brackets: [
    ['{', '}'],
    ['(', ')'],
  ],
  autoClosingPairs: [
    { open: '{', close: '}' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
  ],
  surroundingPairs: [
    { open: '{', close: '}' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
  ],
};

export const miniLangTokensProvider: languages.IMonarchLanguage = {
  defaultToken: '',
  tokenPostfix: '.mini',

  keywords: [
    'fn', 'let', 'if', 'else', 'while', 'return', 'true', 'false'
  ],

  typeKeywords: [
    'i32', 'bool', 'void'
  ],

  operators: [
    '=', '->', '==', '!=', '<=', '>=', '<', '>',
    '+', '-', '*', '/', '%', '&&', '||', '!'
  ],

  symbols: /[=><!~?:&|+\-*\/\^%]+/,

  tokenizer: {
    root: [
      // Identifiers and keywords
      [/[a-z_$][\w$]*/, {
        cases: {
          '@typeKeywords': 'type',
          '@keywords': 'keyword',
          '@default': 'identifier'
        }
      }],

      // Whitespace and comments
      { include: '@whitespace' },

      // Delimiters and operators
      [/[{}()\[\]]/, '@brackets'],
      [/@symbols/, {
        cases: {
          '@operators': 'operator',
          '@default': ''
        }
      }],

      // Numbers
      [/\d+/, 'number'],

      // Delimiters
      [/[,:;]/, 'delimiter'],
    ],

    whitespace: [
      [/[ \t\r\n]+/, 'white'],
      [/\/\/.*$/, 'comment'],
    ],
  },
};
