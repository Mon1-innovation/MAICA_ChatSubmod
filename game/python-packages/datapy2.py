import re
pattern_all_punc = re.compile(ur'[.。!！?？；;，,—~-]')
pattern_uncrit_punc = re.compile(ur'[.。!！?？；;~]')
pattern_crit_punc = re.compile(ur'[.。!！?？~]')
pattern_excrit_punc = re.compile(ur'[!！~]')
pattern_numeric = re.compile(ur'[0-9]')
pattern_content = re.compile(ur'[一-龥A-Za-z]')
pattern_semileft = re.compile(ur'[(（\[]')
pattern_semiright = re.compile(ur'[)）\]]')