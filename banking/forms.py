from django import forms

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label="OTP")
