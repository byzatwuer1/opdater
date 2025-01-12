from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import sqlite3
from datetime import datetime

class SocialMediaScheduler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Sosyal Medya Planlayıcı')
        self.setGeometry(100, 100, 800, 600)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Ana layout
        layout = QHBoxLayout()
        
        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Platform seçimi
        platform_group = QGroupBox("Platform")
        platform_layout = QVBoxLayout()
        self.youtube_radio = QRadioButton("YouTube")
        self.instagram_radio = QRadioButton("Instagram")
        platform_layout.addWidget(self.youtube_radio)
        platform_layout.addWidget(self.instagram_radio)
        platform_group.setLayout(platform_layout)
        
        # Dosya seçimi
        self.file_button = QPushButton("Dosya Seç")
        self.file_button.clicked.connect(self.select_file)
        self.file_label = QLabel("Seçili dosya: ")
        
        # Tarih ve saat seçimi
        date_group = QGroupBox("Zamanlama")
        date_layout = QVBoxLayout()
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        date_layout.addWidget(QLabel("Tarih:"))
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(QLabel("Saat:"))
        date_layout.addWidget(self.time_edit)
        date_group.setLayout(date_layout)
        
        # Planlama butonu
        self.schedule_button = QPushButton("Planla")
        self.schedule_button.clicked.connect(self.schedule_post)
        
        # Sol panel bileşenlerini ekle
        left_layout.addWidget(platform_group)
        left_layout.addWidget(self.file_button)
        left_layout.addWidget(self.file_label)
        left_layout.addWidget(date_group)
        left_layout.addWidget(self.schedule_button)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        
        # Sağ Panel (Planlanmış gönderiler listesi)
        self.posts_table = QTableWidget()
        self.posts_table.setColumnCount(4)
        self.posts_table.setHorizontalHeaderLabels(["Platform", "Dosya", "Zaman", "Durum"])
        
        # Layout'a panelleri ekle
        layout.addWidget(left_panel)
        layout.addWidget(self.posts_table)
        
        main_widget.setLayout(layout)
        
        self.create_database()
        self.update_posts_table()
        
    def create_database(self):
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scheduled_posts
                    (id INTEGER PRIMARY KEY,
                     platform TEXT,
                     file_path TEXT,
                     scheduled_time TEXT,
                     status TEXT)''')
        conn.commit()
        conn.close()
        
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Seç")
        if file_name:
            self.file_label.setText(f"Seçili dosya: {file_name}")
            self.selected_file = file_name
    
    def schedule_post(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, "Hata", "Lütfen bir dosya seçin!")
            return
            
        if not (self.youtube_radio.isChecked() or self.instagram_radio.isChecked()):
            QMessageBox.warning(self, "Hata", "Lütfen bir platform seçin!")
            return
            
        platform = "YouTube" if self.youtube_radio.isChecked() else "Instagram"
        scheduled_time = self.date_edit.dateTime().toPyDateTime()
        
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        c.execute('''INSERT INTO scheduled_posts 
                    (platform, file_path, scheduled_time, status)
                    VALUES (?, ?, ?, ?)''',
                 (platform, self.selected_file, scheduled_time.isoformat(), "Bekliyor"))
        conn.commit()
        conn.close()
        
        self.update_posts_table()
        QMessageBox.information(self, "Başarılı", "Gönderi planlandı!")
        
    def update_posts_table(self):
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        posts = c.execute('''SELECT platform, file_path, scheduled_time, status 
                           FROM scheduled_posts''').fetchall()
        conn.close()
        
        self.posts_table.setRowCount(len(posts))
        for i, post in enumerate(posts):
            for j, value in enumerate(post):
                self.posts_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.posts_table.resizeColumnsToContents()

def main():
    app = QApplication(sys.argv)
    scheduler = SocialMediaScheduler()
    scheduler.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()