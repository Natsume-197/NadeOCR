from PySide6.QtWidgets import QMessageBox

class PopupWidget():    
        
    def show_info_messagebox(self, type, content):
        msg = QMessageBox()
        
        if(type  == 'warning'):
            msg.setIcon(QMessageBox.Warning)
        elif(type == 'information'):
            msg.setIcon(QMessageBox.Information)
        elif(type == 'error'):
            msg.setIcon(QMessageBox.Critical)
    
        # setting message for Message Box
        msg.setText(content)
        
        # setting Message box window title
        msg.setWindowTitle("Alerta")
        
        # declaring buttons on Message Box
        msg.setStandardButtons(QMessageBox.Ok)
        
        # start the app
        retval = msg.exec_()