from django.urls import path
from django.urls import re_path as url
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('accounts/', views.accounts,  name='accounts'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('submit_transfer/', views.submit_transfer, name='submit_transfer'),
    path('submit_withdraw/', views.submit_withdraw, name='submit_withdraw'),
    path('submit_deposit/', views.submit_deposit, name='submit_deposit'),
    path('transaction/', views.transaction_view, name='transaction'),

    # path('generate-pdf/', views.generate_pdf, name='generate_pdf'),

    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('send-otp/', views.send_otp, name='send_otp'),
    # path('target-view/', target_view, name='target_view'),
    # path('another-target-view/', another_target_view, name='another_target_view'),
    path('crypto-sentiment/', views.crypto_sentiment, name='crypto_sentiment'),
    path('crypto-sentiment-home/', views.crypto_sentiment_home, name='crypto_sentiment_home'),



]