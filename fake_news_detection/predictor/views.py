from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from src.model import predict_news
from newspaper import Article
from .models import NewsCheck
from .forms import SignUpForm
import json


@csrf_exempt 
def check_fact(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_data = data.get('text', '').strip()
            
            if not input_data:
                return JsonResponse({'error': 'Input text or URL is empty'}, status=400)

            if input_data.startswith(('http://', 'https://')):
                try:
                    article = Article(input_data)
                    article.download()
                    article.parse()
                    text_to_analyze = f"{article.title}. {article.text}"
                    
                    if not text_to_analyze:
                        return JsonResponse({'error': 'Could not extract text from this URL'}, status=400)
                except Exception:
                    return JsonResponse({'error': 'Failed to process the URL. Access might be restricted.'}, status=400)
            else:

                text_to_analyze = input_data

            probability = predict_news(text_to_analyze)
            result_message = f"This news is {probability}% real"
            
            if request.user.is_authenticated:
                NewsCheck.objects.create(
                    user=request.user,
                    text=input_data,  
                    result_text=result_message
                )
            
            return JsonResponse({'result': result_message})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
    
#Login and Logout 

def user_login(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_pass = request.POST.get('password')
        user = authenticate(request, username=user_name, password=user_pass)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

# Sign up 

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


    
# History of checking news 

def index(request):
    history = None

    if request.user.is_authenticated:
        history = NewsCheck.objects.filter(user=request.user).order_by('-created_at')[:15]
    
    return render(request, 'index.html', {'history': history})