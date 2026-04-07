from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme


def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'E-posta ve sifre alanlarini doldurun.')
        else:
            user = authenticate(request, username=email, password=password)
            if user is None:
                messages.error(request, 'E-posta veya sifre hatali.')
            else:
                login(request, user)
                messages.success(request, 'Basariyla giris yaptin.')
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('home')

    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        terms_accepted = request.POST.get('terms') == 'on'

        if not full_name or not email or not password:
            messages.error(request, 'Lutfen zorunlu alanlari doldur.')
        elif not terms_accepted:
            messages.error(request, 'Devam etmek icin sartlari kabul etmelisin.')
        elif User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Bu e-posta ile kayitli bir hesap var.')
        else:
            new_user = User(username=email, email=email, first_name=full_name)

            try:
                validate_password(password, user=new_user)
            except ValidationError as exc:
                for error_text in exc.messages:
                    messages.error(request, error_text)
            else:
                new_user.set_password(password)
                new_user.save()
                login(request, new_user)
                messages.success(request, 'Hesabin olusturuldu. Hos geldin!')
                return redirect('home')

    return render(request, 'register.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Cikis yaptin.')
    return redirect('login')
