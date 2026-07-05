"""
JARVIS Main Application Window

Features:
- Futuristic black & neon blue HUD design
- Circular glowing microphone animation
- Real-time command input and AI responses
- System monitoring (battery, CPU, memory)
- Command history and memory
"""

import logging
import sys
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFrame, QScrollArea,
    QGridLayout, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen
from PyQt6.QtChart import QChart, QChartView, QPieSeries, QPieSlice

from core.jarvis_engine import JARVISEngine
from core.voice_processor import VoiceProcessor

logger = logging.getLogger(__name__)


class JARVISApplication(QMainWindow):
    """Main JARVIS Application Window"""
    
    def __init__(self):
        """Initialize JARVIS Application"""
        super().__init__()
        
        # Initialize components
        self.engine = JARVISEngine()
        self.voice_processor = VoiceProcessor()
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        self.setup_timers()
        
        logger.info("JARVIS Application initialized")
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("JARVIS - Personal AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Main interaction area
        left_panel = self.create_left_panel()
        
        # Right panel - System info and memory
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with chat area"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🤖 JARVIS")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Personal Offline AI Assistant")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Courier", 9))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00ff00;
                border: 2px solid #00ffff;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(self.chat_display, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Say 'Hey Jarvis' or type commands...")
        self.command_input.setFont(QFont("Arial", 11))
        self.command_input.returnPressed.connect(self.process_command)
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1f3a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #ff0000;
                background-color: #2a2f4a;
            }
        """)
        input_layout.addWidget(self.command_input)
        
        # Microphone button
        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedSize(45, 45)
        self.mic_button.setFont(QFont("Arial", 18))
        self.mic_button.clicked.connect(self.toggle_microphone)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                border: 2px solid #ff0000;
                border-radius: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)
        input_layout.addWidget(self.mic_button)
        
        # Send button
        send_button = QPushButton("Send")
        send_button.setFixedWidth(80)
        send_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        send_button.clicked.connect(self.process_command)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: #000;
                border: 2px solid #00ffff;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00cccc;
            }
        """)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        # Status bar
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.status_label)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with system info"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # System Info Title
        sys_title = QLabel("⚙️ System Info")
        sys_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(sys_title)
        
        # Battery
        battery_layout = QHBoxLayout()
        battery_label = QLabel("🔋 Battery:")
        self.battery_value = QLabel("---%")
        battery_layout.addWidget(battery_label)
        battery_layout.addStretch()
        battery_layout.addWidget(self.battery_value)
        layout.addLayout(battery_layout)
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("⚡ CPU:")
        self.cpu_value = QLabel("---%")
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addStretch()
        cpu_layout.addWidget(self.cpu_value)
        layout.addLayout(cpu_layout)
        
        # Memory
        mem_layout = QHBoxLayout()
        mem_label = QLabel("💾 Memory:")
        self.mem_value = QLabel("---%")
        mem_layout.addWidget(mem_label)
        mem_layout.addStretch()
        mem_layout.addWidget(self.mem_value)
        layout.addLayout(mem_layout)
        
        # Time
        time_layout = QHBoxLayout()
        time_label = QLabel("🕐 Time:")
        self.time_value = QLabel("--:--")
        time_layout.addWidget(time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.time_value)
        layout.addLayout(time_layout)
        
        layout.addSpacing(20)
        
        # Memory section
        mem_title = QLabel("💭 Memory")
        mem_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(mem_title)
        
        # Memory list
        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setMaximumHeight(250)
        self.memory_display.setFont(QFont("Courier", 8))
        self.memory_display.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00ff00;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.memory_display)
        
        layout.addStretch()
        
        # Command history
        history_title = QLabel("📝 Recent Commands")
        history_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(history_title)
        
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMaximumHeight(150)
        self.history_display.setFont(QFont("Courier", 8))
        self.history_display.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #00ccff;
                border: 2px solid #ff0000;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.history_display)
        
        # Apply styling to labels
        for child in panel.findChildren(QLabel):
            child.setStyleSheet("color: #00ffff; font-weight: bold;")
        
        return panel
    
    def setup_styles(self):
        """Setup application-wide styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: #00ffff;
            }
            QLabel {
                color: #00ffff;
            }
            QLineEdit {
                background-color: #1a1f3a;
                color: #00ffff;
                border: 2px solid #00ffff;
                padding: 5px;
            }
            QTextEdit {
                background-color: #0a0e27;
                color: #00ff00;
                border: 2px solid #00ffff;
            }
        """)
    
    def setup_timers(self):
        """Setup application timers"""
        # System info update timer
        self.info_timer = QTimer()
        self.info_timer.timeout.connect(self.update_system_info)
        self.info_timer.start(2000)  # Update every 2 seconds
        
        # Time update timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Update every 1 second
    
    def update_system_info(self):
        """Update system information"""
        try:
            import psutil
            
            # Battery
            battery = psutil.sensors_battery()
            if battery:
                self.battery_value.setText(f"{int(battery.percent)}%")
            
            # CPU
            cpu = psutil.cpu_percent(interval=0.1)
            self.cpu_value.setText(f"{int(cpu)}%")
            
            # Memory
            memory = psutil.virtual_memory()
            self.mem_value.setText(f"{int(memory.percent)}%")
        except Exception as e:
            logger.warning(f"Could not update system info: {e}")
    
    def update_time(self):
        """Update current time"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_value.setText(current_time)
    
    def toggle_microphone(self):
        """Toggle microphone on/off"""
        if self.voice_processor.is_listening:
            self.voice_processor.stop_listening()
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff0000;
                    color: white;
                    border: 2px solid #ff0000;
                    border-radius: 22px;
                }
            """)
            self.status_label.setText("🔴 Microphone Off")
        else:
            self.voice_processor.start_listening()
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff00;
                    color: #000;
                    border: 2px solid #00ff00;
                    border-radius: 22px;
                }
            """)
            self.status_label.setText("🟢 Listening...")
    
    def process_command(self):
        """Process user command"""
        user_input = self.command_input.text().strip()
        
        if not user_input:
            return
        
        # Display user message
        self.display_message(f"👤 You: {user_input}", "#00ffff")
        
        # Remove wake word if present
        if user_input.lower().startswith("hey jarvis"):
            user_input = user_input[len("hey jarvis"):].strip()
        
        # Process command
        try:
            response = self.engine.process_command(user_input)
            self.display_message(f"🤖 JARVIS: {response}", "#00ff00")
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.display_message(f"❌ Error: {e}", "#ff0000")
        
        # Update command history
        self.update_command_history(user_input)
        
        # Clear input
        self.command_input.clear()
        self.command_input.setFocus()
    
    def display_message(self, message: str, color: str = "#00ffff"):
        """Display a message in the chat area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        self.chat_display.append(colored_message)
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def update_command_history(self, command: str):
        """Update command history display"""
        status = self.engine.get_status()
        history_text = "Recent Commands:\n" + "=" * 20 + "\n"
        for cmd in status.get('command_history', [])[-5:]:
            history_text += f"• {cmd}\n"
        self.history_display.setText(history_text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("JARVIS Application closing...")
        self.engine.deactivate()
        event.accept()
