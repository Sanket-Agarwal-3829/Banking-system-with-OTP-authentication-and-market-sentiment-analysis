from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def otp_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('otp_verified'):
            if not request.session.get('next'):
            # Store the URL the user is trying to access
                request.session['next'] = request.path
                request.session['form_data'] = request.POST.dict()
                print(request.session['next'])
            return redirect('send_otp')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
