"""Short, extractive answers. Every selected fact retains its source citation."""
import re

from crestline.routing import normalize

STOP = set('what which who how many much is are the a an for of to in can does do about crestline policy campaign work que cual cuantos cuantas como es la el los las de del para en'.split())


def terms(text):
    return set(re.findall(r'[a-z0-9]+', normalize(text))) - STOP


def concise_evidence(question, evidence):
    q = normalize(question)
    query_terms = terms(question)
    candidates = []
    for position, source in enumerate(evidence):
        section = source.source.split(' — ')[-1]
        lines = [line.strip().lstrip('- ').strip() for line in source.text.splitlines()[1:] if line.strip()]
        lines = [line for line in lines if not line.isupper() and not line.startswith('Last Updated:')]
        # Preserve tier names when the limit is on the following line.
        if re.search(r'rate limit|limite.*api', q):
            label = ''
            for line in lines:
                if re.match(r'Free Tier|Starter|Business|Enterprise', line):
                    label = line.rstrip(':')
                elif re.search(r'\brequests\b', line, re.I) and label:
                    candidates.append((100-position, f'{label}: {line}', source.id))
            continue
        for index, line in enumerate(lines):
            if line.endswith(':') and index+1 < len(lines):
                line += ' ' + lines[index+1]
            score = 2*len(query_terms & terms(line)) + len(query_terms & terms(section))
            if re.search(r'carryover|acumul.*vacaciones', q) and 'CARRYOVER' in section:
                score += 20
            if re.search(r'target audience|publico objetivo', q) and 'TARGET AUDIENCE' in section:
                score += 20
            if 'engineering' in q and 'Engineering teams:' in line:
                score += 30
            if 'remote' in q and re.search(r'engineering|sales|standard', q) and 'HYBRID SCHEDULE' in section:
                if not (terms(line) & query_terms - {'remote', 'days'}):
                    score = 0
            if score > 0 and len(line) > 12:
                candidates.append((score-position*.01, line, source.id))
    candidates.sort(key=lambda item: -item[0])
    if not candidates:
        return "I couldn't isolate a direct answer. Please narrow the question or review the sources."
    # Avoid unrelated lower-scoring passages, and never split a fact mid-sentence.
    threshold = candidates[0][0]*.60
    chosen, seen = [], set()
    max_facts = 4 if re.search(r'rate limit|limite.*api', q) else 3
    for score, line, source_id in candidates:
        if score < threshold or line in seen or len(line)>500:
            continue
        if chosen and sum(len(x) for x in chosen)+len(line)>700:
            break
        seen.add(line)
        chosen.append(f'{line} [{source_id}]')
        if len(chosen)>=max_facts:
            break
    if not chosen:
        return "Please narrow the question; the relevant passage is available under Sources."
    return chosen[0] if len(chosen)==1 else '\n\n'.join('- '+line for line in chosen)
