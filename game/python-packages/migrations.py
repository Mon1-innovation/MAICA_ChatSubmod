class migration_instance():

    def __init__(self, last_ver, curr_ver):
        self.last_ver, self.curr_ver = last_ver, curr_ver
        # Must be lined in sequence!
        self.migration_queue = [
            ("1.1.20", self.migration_1_1_20),
            ("1.1.21", self.migration_1_1_21),
            ("1.2.0", self.migration_1_2_0)
        ]

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
        if signal == 0:
            return True, 'Version unchanged'
        elif signal == 1:
            return False, 'Trying to revert version, denying'
        elif signal == -1:
            return False, 'Version schemas incompatable'
        elif signal == 2:
            for p in self.migration_queue:
                c1 = compare_vers(p[0], self.last_ver) == 1; c2 = compare_vers(p[0], self.curr_ver)
                if c1 == 1 and (c2 == 2 or c2 == 0):
                    p[1]()

    def migration_1_1_20(self):
        print(0)

    def migration_1_1_21(self):
        print(1)

    def migration_1_2_0(self):
        print(2)

if __name__ == '__main__':
    i = migration_instance('1.1.9', '1.2.0')
    i.migrate()