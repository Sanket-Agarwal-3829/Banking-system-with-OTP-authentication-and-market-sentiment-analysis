from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from datetime import datetime
import re

from banking.models import *

from django.db.models import Q

# OTP 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OTPVerificationForm
from .otp_util import send_otp_via_email, EmailDevice
from .decorators import otp_required

@login_required
def send_otp(request):
    user = request.user
    send_otp_via_email(user)
    messages.success(request, 'OTP has been sent to your email.')
    return redirect('otp_verification')

@login_required
def otp_verification(request):
    user = request.user
    form = OTPVerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        otp = form.cleaned_data['otp']
        device = EmailDevice.objects.get(user=user, name='email')
        if device.verify_otp(otp):
            # OTP is valid
            print('verified')
            request.session['otp_verified'] = True
            next_url = request.session.get('next', '/')
            print(request.session['next'])
            request.session['next'] = None
            return redirect(next_url)
        else:
            # OTP is invalid
            messages.error(request, 'Invalid OTP')
    return render(request, 'otp_verification.html', {'form': form})

# @otp_required
# def target_view(request):
#     if request.method == 'POST':
#         # Handle the form submission
#         # Reset the session key for future OTP verification
#         request.session['otp_verified'] = False
#         # Process the form and redirect or render as needed
#         return redirect('success_page')

#     return render(request, 'target_view.html')

# @otp_required
# def another_target_view(request):
#     if request.method == 'POST':
#         # Handle another form submission
#         # Reset the session key for future OTP verification
#         request.session['otp_verified'] = False   
#         # Process the form and redirect or render as needed
#         return redirect('another_success_page')

#     return render(request, 'another_target_view.html')

# ----------------------------------
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)    
            return redirect('accounts')      
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html', {})


def logout_view(request):
    logout(request)
    return render(request, 'login.html', {})


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        Account_Type = request.POST.get('Account_Type')
        password = request.POST.get('password')
        check_password = request.POST.get('check_password')
        verification_type = request.POST.get('verification_type')
        id_number = request.POST.get('ID-number')
        regex = r'^[A-Z0-9]{5}\d[0156]\d([0][1-9]|[12]\d|3[01])\d[A-Z0-9]{3}[A-Z]{2}$'
        if not re.match(regex, id_number):
            messages.error(request, 'Invalid Id number format')
            return render(request, 'register.html')
        if password == check_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_profile = UserProfiles(
                    UP_user=user,
                    UP_UserName=username,
                    UP_UserAdress=address,
                    UP_email=email,
                    UP_contact=contact
                )
                user_profile.save()

                account = Account(
                    AC_user=user_profile,
                    AC_AccoutType=Account_Type
                )
                account.save()

                # Generate account number in the format year, month, day + 00 + id
                account_number = f"{datetime.now().strftime('%Y%m%d')}00{account.id}"
                account.AC_AccoutNumber = account_number
                account.save()

                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Account created for {username}!')
                    return redirect('accounts')
                else:
                    messages.error(request, 'Authentication failed')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'register.html', {})

def accounts(request):
    data = {}
    data['Request_Account'] = Account.objects.get(AC_user = UserProfiles.objects.get(UP_user = request.user))
    data['account_transactions'] = Transactions.objects.filter(Q(TC_sender_account = data['Request_Account']) | Q(TC_receiver_account = data['Request_Account'])).order_by('-TC_date')
    return render(request, 'accounts.html', data)

def deposit_view(request):
    return render(request, 'deposit.html',{})

def withdraw_view(request):
    return render(request, 'withdraw.html',{})

def transfer_view(request):
    return render(request, 'transfer.html',{})

@otp_required
def submit_transfer(request):
    request.session['otp_verified'] = False
    print(request.user)
    print(Account.objects.filter(AC_user = UserProfiles.objects.filter(UP_user = request.user).first()).first().AC_balance)
    account_number = request.session['form_data'].get('account-number')
    account_name = request.session['form_data'].get('account-name')
    transfer_amount = request.session['form_data'].get('transfer-amount')
    recevier_accounts = Account.objects.filter(AC_AccoutNumber = account_number , AC_user__UP_UserName = account_name)
    sender_accounts = Account.objects.filter(AC_user = UserProfiles.objects.filter(UP_user = request.user).first())
    if recevier_accounts.exists():
        recevier_account = recevier_accounts.first()
        sender_account = sender_accounts.first()
        if recevier_account != sender_account:
            if float(sender_account.AC_balance) >= float(transfer_amount):
                print('yo')
                sender_account.AC_balance = float(sender_account.AC_balance) - float(transfer_amount)
                recevier_account.AC_balance = float(recevier_account.AC_balance) + float(transfer_amount)
                sender_account.save()
                recevier_account.save()
                transaction = Transactions(
                    TC_sender_account = sender_account,
                    TC_amount = transfer_amount,
                    TC_type = 'transfer',
                    TC_balance = sender_account.AC_balance,
                    TC_receiver_account = recevier_account
                )
                transaction.save()
                return render(request, 'transfer.html', {'success': 'Transfer Sucessfull'})
            else:
                return render(request, 'transfer.html', {'error': 'Insufficient funds'})
        else:
            return render(request, 'transfer.html', {'error': 'Cannot trsfer to your account'})
    else:
        return render(request, 'transfer.html', {'error': 'Account details doesnt match'})


@otp_required
def submit_withdraw(request):
    request.session['otp_verified'] = False
    withdrawal_amount = request.session['form_data'].get('withdraw-amount')
    withdrawal_account = Account.objects.filter(AC_user = UserProfiles.objects.filter(UP_user = request.user).first()).first()
    if float(withdrawal_account.AC_balance) >= float(withdrawal_amount):
        withdrawal_account.AC_balance = float(withdrawal_account.AC_balance) - float(withdrawal_amount)
        withdrawal_account.save()
        transaction = Transactions(
                    TC_sender_account = withdrawal_account,
                    TC_amount = withdrawal_amount,
                    TC_type = 'withdraw',
                    TC_balance = withdrawal_account.AC_balance

                )
        transaction.save()
        return render(request, 'withdraw.html', {'success': 'Withdrawal Sucessfull'})
    else:
        return render(request, 'withdraw.html' , {'error': 'Insufficient funds'})

@otp_required
def submit_deposit(request):
    try:
        print(request.session['form_data'])
    except:
        pass
    deposit_amount = request.session['form_data'].get('deposit-amount')
    deposit_account = Account.objects.filter(AC_user = UserProfiles.objects.filter(UP_user = request.user).first()).first()
    deposit_account.AC_balance = float(deposit_account.AC_balance) + float(deposit_amount)
    deposit_account.save()
    transaction = Transactions(
                TC_sender_account = deposit_account,
                TC_amount = deposit_amount,
                TC_type = 'deposit',
                TC_balance = deposit_account.AC_balance
            )
    transaction.save()
    request.session['otp_verified'] = False

    return render(request, 'deposit.html', {'success': 'Deposit Sucessfull'})
    

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
def transaction_view(request):
    data = {}
    data['Request_Account'] = Account.objects.get(AC_user = UserProfiles.objects.get(UP_user = request.user))
    if request.method == "POST":
        daterange = request.session['form_data'].get('daterange').split()
        data['daterange'] = request.POST.get('daterange')
        print(daterange)
        if request.POST.get('daterange') == '':
            data['transactions'] = Transactions.objects.filter(Q(TC_sender_account = data['Request_Account']) | Q(TC_receiver_account = data['Request_Account'])).order_by('-TC_date')
        else:
            start_date = daterange[0]
            end_date = daterange[-1]
            data['transactions'] = Transactions.objects.filter(Q(TC_sender_account = data['Request_Account']) | Q(TC_receiver_account = data['Request_Account'])).filter(TC_date__date__gte=start_date,TC_date__date__lte=end_date).order_by('-TC_date')
        print(data['transactions'])
        if request.POST.get('action') == 'generate_pdf':
            template_path = 'pdf_template.html'
            template = get_template(template_path)
            html = template.render(data)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="TranSaction Report.pdf"'

            pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response)

            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response

    else:
        data['transactions'] = Transactions.objects.filter(Q(TC_sender_account = data['Request_Account']) | Q(TC_receiver_account = data['Request_Account'])).order_by('-TC_date')
        data['daterange'] = ''
   
    
    return render(request, 'transaction.html',data)




def crypto_sentiment_home(request):
    btc_data = SentimentData.objects.filter(crypto='BTC').latest('date')
    eth_data = SentimentData.objects.filter(crypto='ETH').latest('date')

    context = {
        'btc_recommendation': btc_data.recommendation,
        'eth_recommendation': eth_data.recommendation,
    }
    return render(request, 'crypto_index.html', context)

def crypto_sentiment(request):
    btc_data = SentimentData.objects.filter(crypto='BTC').latest('date')
    eth_data = SentimentData.objects.filter(crypto='ETH').latest('date')

    context = {
        'btc_graph': btc_data.graph,
        'btc_recommendation': btc_data.recommendation,
        'btc_market_cap': btc_data.market_cap,
        'btc_current_price': btc_data.current_price,
        'btc_volatility': btc_data.volatility,
        'eth_graph': eth_data.graph,
        'eth_recommendation': eth_data.recommendation,
        'eth_market_cap': eth_data.market_cap,
        'eth_current_price': eth_data.current_price,
        'eth_volatility': eth_data.volatility,
    }
    return render(request, 'crypto_sentiment.html', context)
