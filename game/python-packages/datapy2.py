import re
pattern_all_punc = re.compile(ur'[.。!！?？；;，,~]')
pattern_crit_punc = re.compile( ur'[.。!！?？~]')
pattern_excrit_punc = re.compile(ur'[!！~]')
pattern_numeric = re.compile(ur'[0123456789]')
pattern_semileft = re.compile(ur'[(（\[]')
pattern_semiright = re.compile(ur'[)）\]]')
