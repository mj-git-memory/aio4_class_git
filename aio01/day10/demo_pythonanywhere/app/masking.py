from time import monotonic

import regex
from flask import g

from .db import get_db

MAX_RULES = 200
MAX_PATTERN = 200
MASKING_BUDGET = 0.2
FALLBACK = '[표현 검사 지연으로 내용을 표시할 수 없습니다.]'
FLAG_VALUES = {'i': regex.I, 'm': regex.M, 's': regex.S}


def compile_rule(rule):
    flags = regex.VERSION0
    for flag in rule['flags']:
        flags |= FLAG_VALUES[flag]
    pattern = regex.escape(rule['pattern']) if rule['type'] == 'keyword' else rule['pattern']
    return regex.compile(pattern, flags)


def validate_rule(kind, pattern, flags):
    if kind not in ('keyword', 'regex') or not pattern.strip() or len(pattern) > MAX_PATTERN:
        raise ValueError('유형과 패턴을 확인해 주세요. 패턴은 공백이 아닌 1~200자입니다.')
    if any(flag not in FLAG_VALUES for flag in flags) or len(flags) != len(set(flags)):
        raise ValueError('정규식 옵션은 i, m, s만 중복 없이 입력하세요.')
    if kind == 'keyword' and flags:
        raise ValueError('키워드에는 정규식 옵션을 지정할 수 없습니다.')
    flags = ''.join(sorted(flags))
    try:
        compiled = compile_rule({'type': kind, 'pattern': pattern, 'flags': flags})
        for sample in ('', 'a', 'ab', '가나다', '0123', ' '):
            if any(match.start() == match.end() for match in compiled.finditer(sample, timeout=0.01)):
                raise ValueError('빈 구간과 일치하는 정규식은 사용할 수 없습니다.')
    except (regex.error, TimeoutError):
        raise ValueError('유효하지 않거나 처리 시간이 긴 정규식입니다.')
    return kind, pattern, flags


class Masker:
    def __init__(self, rules, budget=MASKING_BUDGET):
        self.deadline = monotonic() + budget
        self.compiled = []
        self.invalid = len(rules) > MAX_RULES
        try:
            for rule in rules:
                self.compiled.append(compile_rule(rule))
        except (regex.error, KeyError):
            self.invalid = True

    def apply(self, text):
        if self.invalid:
            return FALLBACK
        covered = bytearray(len(text))
        try:
            for pattern in self.compiled:
                remaining = min(0.02, self.deadline - monotonic())
                if remaining <= 0:
                    return FALLBACK
                for match in pattern.finditer(text, overlapped=True, timeout=remaining):
                    start, end = match.span()
                    if start == end or monotonic() >= self.deadline:
                        return FALLBACK
                    covered[start:end] = b'\x01' * (end - start)
            return ''.join('*' if covered[i] else char for i, char in enumerate(text))
        except (TimeoutError, regex.error):
            return FALLBACK


def masker():
    if 'masker' not in g:
        rules = get_db().execute('SELECT type, pattern, flags FROM masking_rules ORDER BY id').fetchall()
        g.masker = Masker(rules)
    return g.masker


def preview(text):
    # Grapheme clusters avoid splitting emoji and decomposed Hangul.
    letters = regex.findall(r'\X', masker().apply(text))
    return ''.join(letters[:10]) + ('…' if len(letters) > 10 else '')
