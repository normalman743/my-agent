import sys
import math
import time
import random
import threading
import psutil
import datetime
from datetime import datetime

# 尝试导入PyQt5，如果失败则使用PyQt6
try:
    from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QLineEdit, QPushButton, QLabel, QDialog)
    from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QPoint, 
                             QEasingCurve, pyqtSignal, QThread)
    from PyQt5.QtGui import (QPainter, QColor, QBrush, QPen, QFont, 
                            QPalette, QRadialGradient)
    print("使用 PyQt5")
except ImportError:
    from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QLineEdit, QPushButton, QLabel, QDialog)
    from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QRect, QPoint, 
                             QEasingCurve, pyqtSignal, QThread)
    from PyQt6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, 
                            QPalette, QRadialGradient)
    print("使用 PyQt6")

class IntelligentAIPet(QWidget):
    """智能科技感AI桌宠"""
    
    mood_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 基础属性
        self.radius = 40
        self.base_color = QColor(64, 128, 255)  # 科技蓝，保持不变
        self.current_mood = "idle"
        self.animation_time = 0
        
        # 科技感效果
        self.scan_angle = 0          # 扫描角度
        self.pulse_intensity = 0     # 脉冲强度
        self.particle_effects = []   # 粒子效果
        self.energy_level = 0.5      # 能量等级
        
        # 智能感知数据
        self.system_cpu = 0
        self.system_memory = 0
        self.current_hour = datetime.now().hour
        self.activity_level = "normal"
        
        # 环境响应
        self.last_mouse_pos = QPoint()
        self.mouse_distance = 0
        self.environment_response = 0
        
        # 拖拽
        self.drag_position = QPoint()
        self.chat_dialog = None
        
        self.init_ui()
        self.init_systems()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | 
            Qt.Tool | Qt.X11BypassWindowManagerHint
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(120, 120)  # 稍大一点容纳科技效果
        self.move(200, 200)
        self.setMouseTracking(True)
        
    def init_systems(self):
        """初始化智能系统"""
        # 主渲染循环 - 60fps获得流畅科技效果
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_all_systems)
        self.render_timer.start(16)  # 60fps
        
        # 系统监控 - 每秒更新
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_system)
        self.monitor_timer.start(1000)
        
        # 智能分析 - 每5秒分析一次环境
        self.intelligence_timer = QTimer()
        self.intelligence_timer.timeout.connect(self.analyze_environment)
        self.intelligence_timer.start(5000)
        
        # 初始化粒子系统
        self.init_particles()
        
    def init_particles(self):
        """初始化粒子效果"""
        # 创建围绕AI的能量粒子
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            base_distance = 35 + random.uniform(-5, 5)
            particle = {
                'angle': angle,
                'distance': base_distance,
                'current_distance': base_distance,  # 添加缺失的属性
                'speed': 0.02 + random.uniform(-0.01, 0.01),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(0.3, 0.8),
                'current_alpha': random.uniform(0.3, 0.8),  # 添加缺失的属性
                'pulse_phase': random.uniform(0, 2 * math.pi)
            }
            self.particle_effects.append(particle)
    
    def update_all_systems(self):
        """更新所有系统"""
        self.animation_time += 0.016
        
        # 1. 更新科技效果
        self.update_tech_effects()
        
        # 2. 更新粒子系统
        self.update_particles()
        
        # 3. 环境响应
        self.update_environment_response()
        
        # 4. 智能状态更新
        self.update_intelligent_state()
        
        self.update()
    
    def update_tech_effects(self):
        """更新科技感效果"""
        # 扫描环形效果
        self.scan_angle += 0.05
        if self.scan_angle > 2 * math.pi:
            self.scan_angle = 0
            
        # 脉冲效果 - 根据系统负载调节
        cpu_factor = self.system_cpu / 100.0
        base_pulse = 0.3 + 0.4 * math.sin(self.animation_time * 2)
        self.pulse_intensity = base_pulse + cpu_factor * 0.3
        
        # 能量等级根据时间和系统状态变化
        time_factor = math.sin(self.animation_time * 0.1) * 0.1
        system_factor = (self.system_cpu + self.system_memory) / 200.0
        self.energy_level = 0.4 + time_factor + system_factor
        self.energy_level = max(0.2, min(1.0, self.energy_level))
    
    def update_particles(self):
        """更新粒子效果"""
        for particle in self.particle_effects:
            # 粒子绕圈运动
            particle['angle'] += particle['speed']
            
            # 脉冲效果
            particle['pulse_phase'] += 0.1
            pulse_alpha = 0.5 + 0.5 * math.sin(particle['pulse_phase'])
            particle['current_alpha'] = particle['alpha'] * pulse_alpha * self.energy_level
            
            # 距离微调
            distance_offset = 3 * math.sin(particle['pulse_phase'] * 0.7)
            particle['current_distance'] = particle['distance'] + distance_offset
    
    def update_environment_response(self):
        """更新环境响应"""
        # 获取当前鼠标位置 - 修复鼠标检测
        try:
            current_mouse = QApplication.instance().desktop().cursor().pos()
            pet_center = self.geometry().center()
            
            dx = current_mouse.x() - pet_center.x()
            dy = current_mouse.y() - pet_center.y()
            self.mouse_distance = math.sqrt(dx*dx + dy*dy)
            
            # 根据距离调节响应
            if self.mouse_distance < 100:
                self.environment_response = min(1.0, (100 - self.mouse_distance) / 100.0)
            else:
                self.environment_response *= 0.95  # 渐渐减弱
        except:
            # 如果无法获取鼠标位置，跳过
            self.environment_response *= 0.95
    
    def update_intelligent_state(self):
        """更新智能状态"""
        # 根据系统状态和时间智能切换心情
        if self.system_cpu > 80:
            if self.current_mood != "processing":
                self.set_mood("processing")
        elif self.system_memory > 85:
            if self.current_mood != "analyzing":
                self.set_mood("analyzing")
        elif 22 <= self.current_hour or self.current_hour <= 6:
            if self.current_mood != "sleep_mode":
                self.set_mood("sleep_mode")
        elif self.environment_response > 0.7:
            if self.current_mood != "alert":
                self.set_mood("alert")
        else:
            if self.current_mood not in ["idle", "thinking"]:
                self.set_mood("idle")
    
    def monitor_system(self):
        """监控系统状态"""
        try:
            self.system_cpu = psutil.cpu_percent()
            self.system_memory = psutil.virtual_memory().percent
            self.current_hour = datetime.now().hour
        except:
            # 如果无法获取系统信息，使用模拟数据
            self.system_cpu = 20 + 30 * math.sin(self.animation_time * 0.1)
            self.system_memory = 60 + 20 * math.sin(self.animation_time * 0.07)
    
    def analyze_environment(self):
        """分析环境 - AI的智能思考"""
        # 模拟AI分析周围环境
        analysis_thoughts = [
            "检测到系统负载变化...",
            "分析用户行为模式...", 
            "优化能效参数...",
            "扫描网络活动...",
            "更新学习模型..."
        ]
        
        if random.random() < 0.3:  # 30%概率进入思考状态
            self.set_mood("thinking")
            print(f"🤖 AI思考: {random.choice(analysis_thoughts)}")
            
            # 2秒后回到正常状态
            QTimer.singleShot(2000, lambda: self.set_mood("idle"))
    
    def paintEvent(self, event):
        """绘制科技感AI"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 1. 绘制外层科技环效果
        self.draw_tech_rings(painter, center_x, center_y)
        
        # 2. 绘制粒子效果
        self.draw_particles(painter, center_x, center_y)
        
        # 3. 绘制主体核心
        self.draw_ai_core(painter, center_x, center_y)
        
        # 4. 绘制扫描线
        self.draw_scan_line(painter, center_x, center_y)
        
        # 5. 绘制表情(仅表情变化，颜色不变)
        self.draw_expressions(painter, center_x, center_y)
        
    def draw_tech_rings(self, painter, x, y):
        """绘制科技环效果"""
        # 外层能量环
        for i in range(3):
            ring_radius = self.radius + 15 + i * 8
            ring_alpha = int(80 * self.energy_level * (1 - i * 0.3))
            
            painter.setPen(QPen(QColor(64, 128, 255, ring_alpha), 2))
            painter.setBrush(Qt.NoBrush)
            
            # 不完整的环，营造科技感
            span_angle = int(270 + 60 * math.sin(self.animation_time + i))
            painter.drawArc(x - ring_radius, y - ring_radius, 
                           ring_radius * 2, ring_radius * 2, 
                           int(self.scan_angle * 180 / math.pi * 16), span_angle * 16)
    
    def draw_particles(self, painter, x, y):
        """绘制粒子效果"""
        for particle in self.particle_effects:
            px = x + particle['current_distance'] * math.cos(particle['angle'])
            py = y + particle['current_distance'] * math.sin(particle['angle'])
            
            alpha = int(255 * particle['current_alpha'])
            size = particle['size'] * (0.8 + 0.4 * self.energy_level)
            
            # 粒子颜色 - 保持科技蓝色系
            particle_color = QColor(100, 180, 255, alpha)
            painter.setBrush(QBrush(particle_color))
            painter.setPen(Qt.NoPen)
            
            painter.drawEllipse(int(px - size), int(py - size), 
                              int(size * 2), int(size * 2))
    
    def draw_ai_core(self, painter, x, y):
        """绘制AI核心 - 基础颜色保持不变"""
        # 主体渐变 - 始终是科技蓝
        gradient = QRadialGradient(x, y, self.radius)
        
        # 根据能量等级调节亮度，但保持蓝色
        base_color = self.base_color
        light_factor = int(120 + 40 * self.energy_level)
        dark_factor = int(80 + 20 * self.energy_level)
        
        gradient.setColorAt(0, base_color.lighter(light_factor))
        gradient.setColorAt(0.7, base_color)
        gradient.setColorAt(1, base_color.darker(dark_factor))
        
        # 脉冲边框
        border_alpha = int(150 + 105 * self.pulse_intensity)
        border_color = QColor(100, 200, 255, border_alpha)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, 3))
        painter.drawEllipse(x - self.radius, y - self.radius, 
                          self.radius * 2, self.radius * 2)
        
        # 内层高光
        highlight = QRadialGradient(x - 15, y - 15, 20)
        highlight.setColorAt(0, QColor(255, 255, 255, int(60 * self.energy_level)))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        
        painter.setBrush(QBrush(highlight))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x - 25, y - 25, 50, 50)
    
    def draw_scan_line(self, painter, x, y):
        """绘制扫描线效果"""
        if self.current_mood in ["processing", "analyzing", "alert"]:
            # 旋转扫描线
            line_length = self.radius - 5
            end_x = x + line_length * math.cos(self.scan_angle)
            end_y = y + line_length * math.sin(self.scan_angle)
            
            # 渐变扫描线
            scan_alpha = int(200 * self.energy_level)
            painter.setPen(QPen(QColor(0, 255, 200, scan_alpha), 2))
            painter.drawLine(x, y, int(end_x), int(end_y))
            
            # 扫描点
            painter.setBrush(QBrush(QColor(0, 255, 200, scan_alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(end_x - 3), int(end_y - 3), 6, 6)
    
    def draw_expressions(self, painter, x, y):
        """绘制表情 - 只变表情，不变颜色"""
        # 眼睛位置
        eye_size = 6
        eye_offset_x = 12
        eye_offset_y = 8
        
        # 根据心情绘制不同表情
        if self.current_mood == "sleep_mode":
            # 休眠模式 - 眯眼
            painter.setPen(QPen(QColor(200, 220, 255), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x - eye_offset_x - eye_size, y - eye_offset_y,
                           x - eye_offset_x + eye_size, y - eye_offset_y)
            painter.drawLine(x + eye_offset_x - eye_size, y - eye_offset_y,
                           x + eye_offset_x + eye_size, y - eye_offset_y)
            
        elif self.current_mood == "alert":
            # 警觉模式 - 大眼睛 + 闪烁
            blink = 1.0 if int(self.animation_time * 4) % 2 == 0 else 0.7
            eye_alpha = int(255 * blink)
            
            painter.setBrush(QBrush(QColor(255, 255, 255, eye_alpha)))
            painter.setPen(QPen(QColor(0, 255, 200, eye_alpha), 2))
            painter.drawEllipse(x - eye_offset_x - eye_size, y - eye_offset_y - eye_size,
                              eye_size * 2, eye_size * 2)
            painter.drawEllipse(x + eye_offset_x - eye_size, y - eye_offset_y - eye_size,
                              eye_size * 2, eye_size * 2)
            
        elif self.current_mood in ["processing", "analyzing"]:
            # 处理模式 - 数字眼睛
            painter.setFont(QFont("Consolas", 8, QFont.Bold))
            painter.setPen(QPen(QColor(0, 255, 150), 2))
            
            # 显示数字或字符
            left_char = str(int(self.system_cpu) % 10)
            right_char = str(int(self.system_memory) % 10)
            
            painter.drawText(x - eye_offset_x - 4, y - eye_offset_y + 3, left_char)
            painter.drawText(x + eye_offset_x - 4, y - eye_offset_y + 3, right_char)
            
        elif self.current_mood == "thinking":
            # 思考模式 - 转动的眼睛
            pupil_angle = self.animation_time * 2
            pupil_x = 3 * math.cos(pupil_angle)
            pupil_y = 3 * math.sin(pupil_angle)
            
            # 眼球
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(QPen(QColor(150, 200, 255), 1))
            painter.drawEllipse(x - eye_offset_x - eye_size, y - eye_offset_y - eye_size,
                              eye_size * 2, eye_size * 2)
            painter.drawEllipse(x + eye_offset_x - eye_size, y - eye_offset_y - eye_size,
                              eye_size * 2, eye_size * 2)
            
            # 转动瞳孔
            painter.setBrush(QBrush(QColor(50, 100, 150)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - eye_offset_x + pupil_x - 2), int(y - eye_offset_y + pupil_y - 2), 4, 4)
            painter.drawEllipse(int(x + eye_offset_x + pupil_x - 2), int(y - eye_offset_y + pupil_y - 2), 4, 4)
            
        else:
            # 默认状态 - 正常眼睛
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(QPen(QColor(150, 200, 255), 1))
            painter.drawEllipse(x - eye_offset_x - eye_size//2, y - eye_offset_y - eye_size//2,
                              eye_size, eye_size)
            painter.drawEllipse(x + eye_offset_x - eye_size//2, y - eye_offset_y - eye_size//2,
                              eye_size, eye_size)
            
            # 瞳孔
            painter.setBrush(QBrush(QColor(50, 100, 150)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - eye_offset_x - 2, y - eye_offset_y - 2, 4, 4)
            painter.drawEllipse(x + eye_offset_x - 2, y - eye_offset_y - 2, 4, 4)
        
        # 嘴部指示器
        mouth_y = y + 15
        if self.current_mood == "processing":
            # 处理中 - 进度条嘴
            progress = (math.sin(self.animation_time * 4) + 1) / 2
            bar_width = 20
            filled_width = int(bar_width * progress)
            
            painter.setPen(QPen(QColor(100, 200, 255), 2))
            painter.drawRect(x - bar_width//2, mouth_y - 2, bar_width, 4)
            
            painter.setBrush(QBrush(QColor(0, 255, 150)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(x - bar_width//2, mouth_y - 2, filled_width, 4)
            
        else:
            # 其他状态 - 简单线条
            painter.setPen(QPen(QColor(150, 200, 255), 2, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x - 8, mouth_y, x + 8, mouth_y)
    
    def set_mood(self, mood):
        """设置心情状态"""
        if self.current_mood != mood:
            self.current_mood = mood
            self.mood_changed.emit(mood)
            print(f"🤖 AI状态: {mood}")
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # 触摸反应
            self.set_mood("alert")
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            # 释放后回到空闲状态
            QTimer.singleShot(1000, lambda: self.set_mood("idle"))
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """双击 - 手动切换状态"""
        if event.button() == Qt.LeftButton:
            moods = ["idle", "thinking", "processing", "analyzing", "alert", "sleep_mode"]
            current_index = moods.index(self.current_mood) if self.current_mood in moods else 0
            next_mood = moods[(current_index + 1) % len(moods)]
            self.set_mood(next_mood)
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        self.show_chat_dialog()
    
    def show_chat_dialog(self):
        """显示对话框"""
        if self.chat_dialog is None or not self.chat_dialog.isVisible():
            self.chat_dialog = TechChatDialog(self)
            pet_pos = self.pos()
            self.chat_dialog.move(pet_pos.x() + 140, pet_pos.y() - 100)
            
        self.chat_dialog.show()
        self.chat_dialog.raise_()
        self.chat_dialog.activateWindow()
        
        self.set_mood("alert")
        QTimer.singleShot(2000, lambda: self.set_mood("idle"))

class TechChatDialog(QDialog):
    """科技感对话框"""
    
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AI Console")
        self.setFixedSize(400, 500)
        
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 科技感样式
        self.setStyleSheet("""
            QDialog {
                background: transparent;
            }
            QWidget {
                background-color: rgba(20, 25, 35, 240);
                border: 2px solid rgba(64, 128, 255, 150);
                border-radius: 15px;
                color: #00ff88;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QTextEdit {
                background-color: rgba(10, 15, 25, 200);
                border: 1px solid rgba(0, 255, 136, 100);
                border-radius: 10px;
                padding: 15px;
                font-size: 12px;
                color: #00ff88;
            }
            QLineEdit {
                background-color: rgba(10, 15, 25, 200);
                border: 1px solid rgba(64, 128, 255, 150);
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                color: #4080ff;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 136, 200);
            }
            QPushButton {
                background-color: rgba(64, 128, 255, 200);
                border: 1px solid rgba(0, 255, 136, 150);
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 136, 200);
                border: 1px solid rgba(64, 128, 255, 200);
            }
        """)
        
        # 布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("🤖 AI SYSTEM CONSOLE")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4080ff; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 聊天区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("> SYSTEM INITIALIZED")
        self.chat_display.append("> AI CORE ONLINE")
        self.chat_display.append("> READY FOR INTERACTION")
        main_layout.addWidget(self.chat_display)
        
        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("> ENTER COMMAND...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("EXEC")
        self.send_button.setFixedSize(60, 35)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)
        
        self.input_field.setFocus()
    
    def send_message(self):
        """发送消息"""
        message = self.input_field.text().strip()
        if not message:
            return
            
        self.chat_display.append(f"> USER: {message}")
        self.input_field.clear()
        
        self.parent_pet.set_mood("processing")
        
        # 模拟AI处理
        QTimer.singleShot(1500, lambda: self.show_ai_response(message))
    
    def show_ai_response(self, message):
        """显示AI回复"""
        responses = [
            f"> PROCESSING: {message}",
            "> ANALYSIS COMPLETE",
            "> NEURAL NETWORKS UPDATED",
            "> SYSTEM OPTIMIZATION IN PROGRESS",
            "> READY FOR NEXT COMMAND"
        ]
        
        response = random.choice(responses)
        self.chat_display.append(f"> AI: {response}")
        
        self.parent_pet.set_mood("idle")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 创建智能AI桌宠
    ai_pet = IntelligentAIPet()
    ai_pet.show()
    
    # 显示说明
    print("🚀 智能科技AI桌宠启动成功！")
    print("🔹 科技特性:")
    print("  - 实时系统监控响应")
    print("  - 智能环境感知")
    print("  - 粒子能量效果")
    print("  - 扫描线科技感")
    print("  - 基础颜色保持科技蓝")
    print("🔹 智能状态:")
    print("  - idle: 空闲待机")
    print("  - thinking: 智能分析")
    print("  - processing: 高CPU处理中")
    print("  - analyzing: 高内存分析中") 
    print("  - alert: 环境警觉")
    print("  - sleep_mode: 深夜休眠")
    print("🔹 交互方式:")
    print("  - 拖拽: 移动位置")
    print("  - 双击: 手动切换状态")
    print("  - 右键: 打开AI控制台")
    print("  - 自动: 根据系统状态智能响应")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()