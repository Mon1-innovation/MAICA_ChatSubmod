class migration_instance(object):

    def __init__(self, last_ver, curr_ver, force_current=False):
        self.last_ver, self.curr_ver = last_ver, curr_ver
        self.force_current = force_current
        self.migration_queue = []

    def migrate(self):
        def compare_vers(v1, v2):
            cmp = None
            v1s = str(v1).split('.')
            v2s = str(v2).split('.')
            if len(v1s) == len(v2s):
                j = -1
                for i in v1s:
                    j += 1
                    x = int(i)
                    y = int(v2s[j])
                    if x > y:
                        cmp = 1
                        break
                    elif x < y:
                        cmp = 2
                        break
                if not cmp:
                    cmp = 0
            else:
                cmp = -1
            # -1 ERROR
            # 0 same
            # 1 first larger
            # 2 second larger
            return cmp
        signal = compare_vers(self.last_ver, self.curr_ver)
        if signal == 0 and not self.force_current:
            return True, 'Version unchanged'
        elif signal == 1 and not self.force_current:
            return False, 'Trying to revert version, denying'
        elif signal == -1 and not self.force_current:
            return False, 'Version schemas incompatable'
        elif signal == 2 or self.force_current:
            for p in self.migration_queue:
                c1 = compare_vers(p[0], self.last_ver) == 1
                c2 = compare_vers(p[0], self.curr_ver)
                is_pending = signal == 2 and c1 == 1 and (c2 == 2 or c2 == 0)
                is_current = self.force_current and c2 == 0
                if is_pending or is_current:
                    p[1]()
