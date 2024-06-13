# trials
import sys
import os
from PyQt5.QtWidgets import (QComboBox, QApplication, QMessageBox, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QGridLayout, QDesktopWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
# from dotenv import load_dotenv
from zhipuai import ZhipuAI
from PIL import Image
import pytesseract
import re

# 加载环境变量
# load_dotenv()

client = ZhipuAI(
    api_key='09b8d49dd72b9a3dcb672947f6ec1797.BobXUuGN1oRlHQcL'
)
messages = []

def get_completion(prompt, model="glm-4", temperature=0.01):
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    if len(response.choices) > 0:
        return response.choices[0].message.content
    return "generate answer error"

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_count = 0
        self.image_path_array = []
        self.condition = 1 # 条件状态，记录小人头的开合状态

    # 监听拖拽内容第一次进入应用窗口事件
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.condition = 2
            self.update_image()
        else:
            event.ignore()

    # 监听拖拽内容进入窗口后的移动事件
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # 监听拖拽内容被松开事件
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            items = []
            for item in event.mimeData().urls():
                items.append(item.toLocalFile())
            self.load_image(items)
        else:
            event.ignore()

    # 监听拖拽内容离开程序窗口事件
    def dragLeaveEvent(self, event):
        event.accept()
        self.condition = 1
        self.update_image()

    def update_image(self):
        # 根据条件选择图像
        if self.condition ==1:
            pixmap = QPixmap('1.png')
        elif self.condition == 2:
            pixmap = QPixmap('2.png')
        elif self.condition == 3:
            pixmap = QPixmap('3.png')
        
        self.head_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))


    def initUI(self):
        self.setWindowTitle('AcademicHelper •́ω•̀')
        self.resize(800,600)
        self.center()
        # 使用样式表设置背景颜色
        self.setStyleSheet("QWidget { background-color: #dd5f36; }")  # 亮绿色背景
        self.setAcceptDrops(True) #接受拖放标签

        
        self.label = QLabel('您的论文格式小助手上线啦', self) #居中显示标签
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 水平靠右并且垂直居中
        # 设置标签的固定高度
        self.label.setFixedHeight(50)  # 设置标签的高度为50像素

        self.head_label = QLabel(self)
        self.head_label.setPixmap(QPixmap('1.png').scaled(200, 200, Qt.KeepAspectRatio))
        self.head_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.head_label.setFixedHeight(200)  # 设置标签的高度为50像素

        
        self.result_label = QLabel(self)
        self.result_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        self.load_button = QPushButton('Load Image', self)
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMinimumWidth(300)  # 设置按钮最小宽度
        self.load_button.setMaximumWidth(500)  # 设置按钮最大宽度

        
        self.complete_button = QPushButton('Complete', self)
        self.complete_button.clicked.connect(self.complete_action)
        self.complete_button.setMinimumWidth(300)  # 设置按钮最小宽度
        self.complete_button.setMaximumWidth(500)  # 设置按钮最大宽度

        
        # 创建下拉框
        self.dropdown = QComboBox(self)
        self.dropdown.addItem("Option 1")
        self.dropdown.addItem("Option 2")
        self.dropdown.addItem("Option 3")
        self.dropdown.setMinimumWidth(300)  # 设置按钮最小宽度
        self.dropdown.setMaximumWidth(500)  # 设置按钮最大宽度

        self.grid_layout = QGridLayout()

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.dropdown, 0, Qt.AlignHCenter)  # 将下拉框添加到布局中
        vbox.addWidget(self.load_button, 0, Qt.AlignHCenter)
        vbox.addWidget(self.complete_button, 0, Qt.AlignHCenter)
        vbox.addLayout(self.grid_layout)
        vbox.addWidget(self.result_label)  
        vbox.addWidget(self.head_label)      
        

        
        self.setLayout(vbox)

    def center(self):
        qr = self.frameGeometry()  # 获取窗口的几何形状
        cp = QDesktopWidget().availableGeometry().center()  # 获取显示屏幕的中心点
        qr.moveCenter(cp)  # 将窗口的中心点放置到屏幕的中心点
        self.move(qr.topLeft())  # 移动窗口的顶部左角到计算出的位置
    
        # 定义一个函数load_image，用于加载图片
    def load_image(self, img_path=None): #img_path图像地址数组
        if (img_path): #拖拽
            for fileName in img_path:
                pixmap = QPixmap(fileName).scaled(150, 150, Qt.KeepAspectRatio)
                image_label = QLabel(self)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(image_label, self.image_count// 2, self.image_count % 2)  # 假设每行最多显示2张图片
                self.image_path_array.append(fileName)
                self.image_count += 1
            self.condition=3
            self.update_image()

        else: #从文件中选‘
            options = QFileDialog.Options()
            fileNames, _ = QFileDialog.getOpenFileNames(self, "Load Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
            if fileNames:
                
                for fileName in fileNames:
                    pixmap = QPixmap(fileName).scaled(150, 150, Qt.KeepAspectRatio)
                    image_label = QLabel(self)
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    self.grid_layout.addWidget(image_label, self.image_count// 2, self.image_count % 2)  # 假设每行最多显示3张图片
                    self.image_path_array.append(fileName)
                    self.image_count += 1
                self.condition=3
                self.update_image()


    def complete_action(self):
        if hasattr(self, 'image_path_array'):
            self.process_image_and_call_api(self.image_path_array)
            
        

    # def image_to_strings(img):
    #     custom_config = r'--psm 6 -c preserve_interword_spaces=1'
    #     text = pytesseract.image_to_string(img, config=custom_config)

    #     # 处理识别结果，在两个名字之间插入换行符
    #     def insert_newline_between_names(text):
    #         processed_text = re.sub(r"(\S+)\s{3,}(\S+)", r"\1\n\2", text)
    #         return processed_text

    #     processed_text = insert_newline_between_names(text)
    #     return (processed_text)
    
    
    def process_image_and_call_api(self, img_path_combination):
        def insert_newline_between_names(text):
        # 正则表达式匹配两个或更多连续的空格，并将其替换为换行符
            processed_text = re.sub(r"(\S+)\s{2,}(\S+)", r"\1\n\2", text)
            return processed_text
        
        # 使用pytesseract进行图片识别
        processed_text = ''
        
        for img_path in img_path_combination:
            img = Image.open(img_path)
            custom_config = r'--psm 6 -c preserve_interword_spaces=1'
            text = pytesseract.image_to_string(img, config=custom_config)
            processed_text += insert_newline_between_names(text)
            
            processed_text += '\n'

        # 调用API
        if self.dropdown.currentText() == '国标-顺序编码制（GB/T 7714-2015）':
            prompt = '请基于以下信息，按照GB/T 7714-2015的顺序编码制生成文中引用格式。文中引用格式应为：[编号]，参考文献列表按文中出现顺序排列。直接给出引用即可，不需要任何解释。以下为输出样例：\n文中引用：\n...根据研究结果[1]，...\n参考文献：\n[1] 张三. 文章标题[J]. 期刊名称, 年份, 卷(期): 页码.\n' + processed_text
        if self.dropdown.currentText() == '国标-著者-出版年制（GB/T 7714-2015）':
            prompt = '请基于以下信息，按照GB/T 7714-2015的著者-出版年制生成文中引用格式。文中引用格式应为：（作者，出版年份），参考文献列表按作者姓氏字母顺序排列。直接给出引用即可，不需要任何解释。以下为输出样例：\n文中引用：\n...根据研究结果（张三，2019），...\n参考文献：张三. 文章标题[J]. 期刊名称, 2019, 30(2): 123-130.\n' + processed_text
        if self.dropdown.currentText() == 'APA':
            prompt = '请基于以下信息直接给出MLA格式的论文引用尾注，不需要任何解释。文本中包含一个或多个人名，每个人名包含名和姓，请正确识别。\n' + processed_text
        if self.dropdown.currentText() == 'APA':
            prompt = '请基于以下信息直接给出MLA格式的论文引用尾注，不需要任何解释。文本中包含一个或多个人名，每个人名包含名和姓，请正确识别。\n' + processed_text
        if self.dropdown.currentText() == 'Chicago':
            prompt = '请基于以下信息直接给出MLA格式的论文引用尾注，不需要任何解释。文本中包含一个或多个人名，每个人名包含名和姓，请正确识别。\n' + processed_text
        if self.dropdown.currentText() == 'Harvard':
            prompt = '请基于以下信息直接给出MLA格式的论文引用尾注，不需要任何解释。文本中包含一个或多个人名，每个人名包含名和姓，请正确识别。\n' + processed_text
        

        result = get_completion(prompt)
        self.result_label.setText(f"API Response:\n{result}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
