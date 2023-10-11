import tkinter as tk
from tkinter import messagebox
from twilio.rest import Client
import random
import threading
import time

account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"
client = Client(account_sid, auth_token)
expiration_time = 120


class OTPVerification:
    def __init__(self, master):
        self.master = master
        self.master.title('OTP Verification')
        self.master.geometry("600x275")
        self.otp = None
        self.timer_thread = None
        self.resend_timer = None
        self.wrong_attempts = 0
        self.locked = False
        self.stop_timer = False

        self.label1 = tk.Label(self.master,
                               text='Enter your mobile number:',
                               font=('Arial', 14))
        self.label1.pack()

        self.mobile_number_entry = tk.Entry(self.master,
                                            width=20,
                                            font=('Arial', 14))
        self.mobile_number_entry.pack()

        self.send_otp_button = tk.Button(self.master,
                                         text='Send OTP',
                                         command=self.send_otp,
                                         font=('Arial', 14))
        self.send_otp_button.pack()

        self.timer_label = tk.Label(self.master,
                                    text='',
                                    font=('Arial', 12, 'bold'))
        self.timer_label.pack()

        self.resend_otp_button = tk.Button(self.master,
                                           text='Resend OTP',
                                           state=tk.DISABLED,
                                           command=self.resend_otp,
                                           font=('Arial', 14))
        self.resend_otp_button.pack()

        self.label2 = tk.Label(self.master,
                               text='Enter OTP sent to your mobile:',
                               font=('Arial', 14))
        self.label2.pack()

        self.otp_entry = tk.Entry(self.master,
                                  width=20,
                                  font=('Arial', 14))
        self.otp_entry.pack()

        self.verify_otp_button = tk.Button(self.master,
                                           text='Verify OTP',
                                           command=self.verify_otp,
                                           font=('Arial', 14))
        self.verify_otp_button.pack()

    def start_timer(self):
        self.timer_thread = threading.Thread(target=self.timer_countdown)
        self.timer_thread.start()

    def timer_countdown(self):
        start_time = time.time()
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = expiration_time - elapsed_time
            if self.stop_timer:
                break
            if remaining_time <= 0:
                messagebox.showerror('Error', 'OTP has expired.')
                self.resend_otp_button.config(state=tk.NORMAL)
                self.otp = None
                break
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            timer_label = f'Time Remaining: {minutes:02d}:{seconds:02d}'
            self.timer_label.config(text=timer_label)
            time.sleep(1)

    def send_otp(self):
        if self.locked:
            messagebox.showinfo(
                'Account Locked', 'Your account is locked. Try again later.')
            return
        mobile_number = self.mobile_number_entry.get()
        if not mobile_number:
            messagebox.showerror('Error', 'Please enter your mobile number.')
            return

        self.otp = random.randint(1000, 9999)
        message = client.messages.create(
            body=f'Your OTP is {self.otp}.',
            from_='TWILIO_MOBILE_NUMBER',
            to=mobile_number
        )
        messagebox.showinfo(
            'OTP Sent', f'OTP has been sent to {mobile_number}.')
        self.start_timer()
        self.send_otp_button.config(state=tk.DISABLED)
        self.resend_otp_button.config(state=tk.DISABLED)
        self.otp_entry.delete(0, tk.END)

    def resend_otp(self):
        if self.locked:
            messagebox.showinfo(
                'Account Locked', 'Your account is locked. Try again later.')
            return
        mobile_number = self.mobile_number_entry.get()
        if not mobile_number:
            messagebox.showerror('Error', 'Please enter your mobile number.')
            return

        self.otp = random.randint(1000, 9999)
        message = client.messages.create(
            body=f'Your OTP is {self.otp}.',
            from_='TWILIO_MOBILE_NUMBER',
            to=mobile_number
        )
        messagebox.showinfo(
            'OTP Sent', f'New OTP has been sent to {mobile_number}.')
        self.start_timer()
        self.resend_otp_button.config(state=tk.DISABLED)

    def verify_otp(self):
        user_otp = self.otp_entry.get()
        if not user_otp:
            messagebox.showerror('Error', 'Please enter OTP.')
            return
        if self.otp is None:
            messagebox.showerror('Error', 'Please generate OTP first.')
            return
        if int(user_otp) == self.otp:
            messagebox.showinfo('Success', 'OTP verified successfully.')
            self.stop_timer = True
            exit()
        else:
            self.wrong_attempts += 1
            if self.wrong_attempts == 3:
                self.lock_account()
            else:
                messagebox.showerror('Error', 'OTP does not match.')

    def lock_account(self):
        self.locked = True
        self.label1.config(text='Account Locked')
        self.mobile_number_entry.config(state=tk.DISABLED)
        self.send_otp_button.config(state=tk.DISABLED)
        self.timer_label.config(text='')
        self.resend_otp_button.config(state=tk.DISABLED)
        self.label2.config(text='')
        self.otp_entry.config(state=tk.DISABLED)
        self.verify_otp_button.config(state=tk.DISABLED)
        self.stop_timer = True
        countdown_time = 10 * 60
        self.start_countdown(countdown_time)

    def start_countdown(self, remaining_time):
        if remaining_time <= 0:
            self.reset_account()
            return

        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_label = f'Account Locked. Try again in: {minutes:02d}:{seconds:02d}'
        self.timer_label.config(text=timer_label)
        self.master.after(1000, self.start_countdown, remaining_time - 1)

    def reset_account(self):
        self.locked = False
        self.wrong_attempts = 0
        self.label1.config(text='Enter your mobile number:')
        self.mobile_number_entry.config(state=tk.NORMAL)
        self.send_otp_button.config(state=tk.NORMAL)
        self.timer_label.config(text='')
        self.resend_otp_button.config(state=tk.DISABLED)
        self.label2.config(text='Enter OTP sent to your mobile:')
        self.otp_entry.config(state=tk.NORMAL)
        self.verify_otp_button.config(state=tk.NORMAL)
        self.stop_timer = False

    def enable_resend_button(self):
        self.resend_otp_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    root = tk.Tk()
    otp_verification = OTPVerification(root)
    root.mainloop()
