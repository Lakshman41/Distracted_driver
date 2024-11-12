from database import database
class users:
    def __init__(self,username,email_id,password):
        self.username=username
        self.email_id=email_id
        self.password=password

    def change_username(self,new_username):
        self.username=new_username
        self.obj.alter_username(self.email_id,new_username)

    def change_password(self,new_password):
        self.password=new_password
        self.obj.alter_password(self.email_id,new_password)

    def validation_username(self,val_username,val_password):
        if val_password==self.password and val_username==self.username :
            return True
        else :
            return False
        
    def validation_email_id(self,val_email_id,val_password):
        if val_password==self.password and val_email_id==self.username :
            return True
        else :
            return False
        
    def insertion(self):
        self.obj=database()
        self.obj.insert(self.username,self.email_id,self.password)
