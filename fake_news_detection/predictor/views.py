from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from predictor.runtime import predict_news
from newspaper import Article, Config
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
                    config = Config()
                    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                    config.request_timeout = 30
                    config.fetch_images = False  
                    
                    article = Article(input_data, config=config)
                    article.download()
                    article.parse()
                    
                    title = article.title if article.title else ""
                    text = article.text if article.text else ""
                    text_to_analyze = f"{title}. {text}".strip()
                    
                    if not text_to_analyze or len(text_to_analyze) < 20:
                        return JsonResponse({'error': 'Could not extract enough content from this URL. The page might be protected or have no readable text.'}, status=400)
                except Exception as e:
                    error_msg = str(e)
                    if 'timeout' in error_msg.lower():
                        return JsonResponse({'error': 'The request timed out while trying to reach the URL. This might be due to slow server response or anti-scraping measures. Please try again or paste the text directly.'}, status=400)
                    return JsonResponse({'error': f'Failed to process the URL: {error_msg}'}, status=400)
            else:
                word_count = len(input_data.split())
                if word_count < 100:
                    return JsonResponse({'error': f'Text is too short ({word_count} words). Please provide at least 100 words or a URL for accurate prediction.'}, status=400)
                text_to_analyze = input_data

            probability = predict_news(text_to_analyze)
            
            category = 'neutral'
            if probability < 39:
                result_message = f"Potential Fake News ({probability}% Real)"
                category = 'fake'
            elif probability > 69:
                result_message = f"Likely Authentic News ({probability}% Real)"
                category = 'real'
            else:
                result_message = f"Inconclusive Result ({probability}%). The content is ambiguous."
                category = 'neutral'
            
            response_data = {'result': result_message, 'category': category}
            
            if request.user.is_authenticated:
                news_check = NewsCheck.objects.create(
                    user=request.user,
                    text=input_data,  
                    result_text=result_message,
                    category=category
                )
                response_data['id'] = news_check.id
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
    
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

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


    
def index(request):
    history = None

    if request.user.is_authenticated:
        history = NewsCheck.objects.filter(user=request.user).order_by('-created_at')[:15]
    
    return render(request, 'index.html', {'history': history})

@csrf_exempt
def delete_history(request, item_id):
    if request.method == 'DELETE':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        try:
            item = NewsCheck.objects.get(id=item_id, user=request.user)
            item.delete()
            return JsonResponse({'success': True})
        except NewsCheck.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)