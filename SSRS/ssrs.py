import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QFrame, QLineEdit, QDialog, QFormLayout


def save_to_json(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4)


class StartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("输入您的ID")
        self.layout = QFormLayout()
        self.id_input = QLineEdit()
        self.layout.addRow("ID:", self.id_input)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addRow(self.ok_button)
        self.setLayout(self.layout)

    def get_id(self):
        return self.id_input.text()


class Survey(QWidget):
    def __init__(self, filename):
        super().__init__()

        self.setWindowTitle("社会支持评定量表（SSRS）")
        self.setGeometry(100, 100, 900, 900)
        self.current_page = 0
        self.questions_per_page = 10

        self.layout = QVBoxLayout()
        self.questions_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setLayout(self.questions_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        self.questions = []
        self.responses = {}
        self.user_id = ""

        # Load questions from the JSON file
        self.load_questions(filename)

        # Navigation buttons
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton('前一页')  # previous page
        self.prev_button.clicked.connect(self.show_prev_page)
        self.prev_button.setEnabled(False)
        self.nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton('下一页')  # next page
        self.next_button.clicked.connect(self.show_next_page)
        self.nav_layout.addWidget(self.next_button)

        self.submit_button = QPushButton('提交')  # submit
        self.submit_button.clicked.connect(self.submit_answers)
        self.submit_button.setEnabled(False)
        self.nav_layout.addWidget(self.submit_button)

        self.layout.addLayout(self.nav_layout)
        self.setLayout(self.layout)

    def load_questions(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.questions = data['questions']

    def show_page(self, page):
        for i in reversed(range(self.questions_layout.count())):
            widget = self.questions_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        start = page * self.questions_per_page
        end = min(start + self.questions_per_page, len(self.questions))

        for question in self.questions[start:end]:
            self.add_question(question)

        self.prev_button.setEnabled(page > 0)
        self.next_button.setEnabled(end < len(self.questions))
        self.submit_button.setEnabled(end >= len(self.questions))

    def add_question(self, question):
        question_frame = QFrame()
        question_layout = QVBoxLayout()

        label = QLabel(f"{question['item']}. {question['description']}")
        question_layout.addWidget(label)

        combo_box = QComboBox()
        combo_box.addItem("请选择最符合的一项", None)
        for option in question['options']:
            combo_box.addItem(str(option), option)

        combo_box.currentIndexChanged.connect(lambda _, b=combo_box, q=question['item']: self.record_response(b, q))
        question_layout.addWidget(combo_box)

        question_frame.setLayout(question_layout)
        self.questions_layout.addWidget(question_frame)

    def record_response(self, combo_box, question_item):
        self.responses[question_item] = combo_box.currentData()

    def show_next_page(self):
        self.current_page += 1
        self.show_page(self.current_page)

    def show_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        self.show_page(self.current_page)

    def submit_answers(self):
        print("问卷采集已完成！")
        print("Responses:", self.responses)

        mapping = {"一个也没有": 1, "1-2个": 2, "3-5个": 3, "6个或以上": 4,
                   "远离家人，且独居一室": 1, "住处经常变动，多数时间和陌生人住在一起": 2,"和同学、同事或朋友住在一起": 3, "和家人住在一起": 4,
                   "相互之间从不关心，只是点头之交": 1,"遇到困难可能会稍微关心": 2,"有些人很关心您": 3,"大多数人都很关心您": 4,
                   "无": 1,"极少": 2,"一般": 3,"全力支持": 4,
                   "从不向任何人倾诉": 1,"只向关系极为密切的1-2人倾诉": 2,"如果朋友主动询问会说出来": 3,"主动倾诉自己的烦恼以获得支持和理解": 4,
                   "只靠自己，不接受别人帮助": 1,"很少请求别人帮助": 2,"有时请求别人帮助": 3,"有困难时经常向亲友、组织求援": 4,
                   "从不参加": 1,"偶尔参加": 2,"经常参加": 3,"主动参加并积极活动": 4,
                   }
        num_responses = {key: mapping[value] for key, value in self.responses.items()}
        print(num_responses)

        

        self.close()


def main():
    app = QApplication(sys.argv)

    dialog = StartDialog()
    if dialog.exec():
        user_id = dialog.get_id()
        main_window = Survey('SSRS.json')
        main_window.user_id = user_id
        main_window.show()
        main_window.show_page(main_window.current_page)
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
