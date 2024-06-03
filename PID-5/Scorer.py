class PID5Scorer:
    def __init__(self, responses):

        self.responses = responses
        # Scores of following items need to be reversed (3 to 0, 2 to 1, 1 to 2, and 0 to 3)
        self.reverse_items = [7, 30, 35, 58, 87, 90, 96, 97, 98, 131, 142, 155, 164, 177, 210, 215]

        self.facets = {
            "快感缺乏（Anhedonia）": [1, 23, 26, 30, 124, 155, 157, 189],
            "焦虑（Anxiousness）": [79, 93, 95, 96, 109, 110, 130, 141, 174],
            "寻求关注（Attention Seeking）": [14, 43, 74, 111, 113, 173, 191, 211],
            "麻木（Callousness）": [11, 13, 19, 54, 72, 73, 90, 153, 166, 183, 198, 200, 207, 208],
            "欺骗（Deceitfulness）": [41, 53, 56, 76, 126, 134, 142, 206, 214, 218],
            "抑郁（Depressivity）": [27, 61, 66, 81, 86, 104, 119, 148, 151, 163, 168, 169, 178, 212],
            "注意分散（Distractibility）": [6, 29, 47, 68, 88, 118, 132, 144, 199],
            "怪异性（Eccentricity）": [5, 21, 24, 25, 33, 52, 55, 70, 71, 152, 172, 185, 205],
            "情绪稳定性（Emotional Lability）": [18, 62, 102, 122, 138, 165, 181],
            "傲慢（Grandiosity）": [40, 65, 114, 179, 187, 197],
            "敌对（Hostility）": [28, 32, 38, 85, 92, 116, 158, 170, 188, 216],
            "冲动（Impulsivity）": [4, 16, 17, 22, 58, 204],
            "亲密回避（Intimacy Avoidance）": [89, 97, 108, 120, 145, 203],
            "不负责任（Irresponsibility）": [31, 129, 156, 160, 171, 201, 210],
            "操控（Manipulativeness）": [107, 125, 162, 180, 219],
            "感知失调（Perceptual Dysregulation）": [36, 37, 42, 44, 59, 77, 83, 154, 192, 193, 213, 217],
            "持续性（Perseveration）": [46, 51, 60, 78, 80, 100, 121, 128, 137],
            "情感受限（Restricted Affectivity）": [8, 45, 84, 91, 101, 167, 184],
            "完美主义（Rigid Perfectionism）": [34, 49, 105, 115, 123, 135, 140, 176, 196, 220],
            "冒险（Risk Taking）": [3, 7, 35, 39, 48, 67, 69, 87, 98, 112, 159, 164, 195, 215],
            "分离焦虑（Separation Insecurity）": [12, 50, 57, 64, 127, 149, 175],
            "顺从（Submissiveness）": [9, 15, 63, 202],
            "多疑（Suspiciousness）": [2, 103, 117, 131, 133, 177, 190],
            "不寻常的信念与经历（Unusual Beliefs & Experiences）": [94, 99, 106, 139, 143, 150, 194, 209],
            "退缩（Withdrawal）": [10, 20, 75, 82, 136, 146, 147, 161, 182, 186]
        }
        self.domain = {
            "负性情感（Negative Affect）": ["情绪稳定性（Emotional Lability）", "焦虑（Anxiousness）", "分离焦虑（Separation Insecurity）"],
            "解离（Detachment）": ["退缩（Withdrawal）", "快感缺乏（Anhedonia）", "亲密回避（Intimacy Avoidance）"],
            "敌意（Antagonism）": ["操控（Manipulativeness）", "欺骗（Deceitfulness）", "傲慢（Grandiosity）"],
            "失抑制（Disinhibition）": ["不负责任（Irresponsibility）", "冲动（Impulsivity）", "注意分散（Distractibility）"],
            "精神病性（Psychoticism）": ["不寻常的信念与经历（Unusual Beliefs & Experiences）", "怪异性（Eccentricity）", "感知失调（Perceptual Dysregulation）"]
        }
        self._invert_scores()
        self.facet_scores = self._calculate_facet_scores()
        self.domain_scores = self._calculate_domain_scores()

    def _invert_scores(self):
        for item in self.reverse_items:
            if str(item) in self.responses:
                self.responses[str(item)] = 3 - self.responses[str(item)]

    def _calculate_facet_scores(self):
        facet_scores = {}
        for facet, items in self.facets.items():
            total = 0
            count = 0
            for item in items:
                if str(item) in self.responses:
                    total += self.responses[str(item)]
                    count += 1
            if count > 0:
                facet_scores[facet] = total / count
        return facet_scores

    def _calculate_domain_scores(self):
        domain_scores = {}
        for domain, facets in self.domain.items():
            total = 0
            count = 0
            for facet in facets:
                if facet in self.facet_scores:
                    total += self.facet_scores[facet]
                    count += 1
            if count > 0:
                domain_scores[domain] = total / count
        return domain_scores

    def get_scores(self):
        return self.facet_scores, self.domain_scores
