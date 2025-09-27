import re
pattern_all_punc = re.compile(ur'[.。!！?？；;，,—~-]+')
pattern_uncrit_punc = re.compile(ur'[.。!！?？；;~]+')
pattern_subcrit_punc = re.compile(ur'[.。!！?？；;~]+')
pattern_crit_punc = re.compile(ur'[.。!！?？~]+')
pattern_excrit_punc = re.compile(ur'[!！~]+')
pattern_numeric = re.compile(ur'[0-9]')
pattern_content = re.compile(ur'[一-龥A-Za-z]')
pattern_semileft = re.compile(ur'[(（\[]')
pattern_semiright = re.compile(ur'[)）\]]')



pattern_common_punc = ur'(\s*[.!?;,~]+\s*)'
pattern_crit = ur'[.!?~]'
pattern_excrit = ur'[~!]'

pattern_emotion = ur'\[(.*?)\]'
bad_pattern = ur'(\ud83c[\udf00-\udfff])|(\ud83d[\udc00-\ude4f\ude80-\udeff])|[\u2600-\u2B55]' 


pr1 = ur'\s*\.\.\.'
pr2 = ur'\s*[；;:︰]'
pr3 = ur'\s*[.。?？]'